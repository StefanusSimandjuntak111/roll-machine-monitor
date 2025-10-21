"""
Offline queue for Supabase operations.
Handles queuing and retrying failed Supabase operations when connection is restored.
"""
import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class OfflineQueue:
    """Manager for queuing and processing offline Supabase operations."""
    
    def __init__(self, queue_dir: str = "logs"):
        """
        Initialize offline queue.
        
        Args:
            queue_dir: Directory to store queue file
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(exist_ok=True)
        self.queue_file = self.queue_dir / "supabase_queue.json"
        
        # Maximum retry count before giving up
        self.max_retries = 10
        
        # Operation types
        self.BATCH_METADATA = "batch_metadata"
        self.PRODUCTION_LOG = "production_log"
    
    def add_operation(
        self, 
        operation_type: str, 
        data: Dict[str, Any],
        priority: int = 0
    ) -> bool:
        """
        Add a failed operation to the queue.
        
        Args:
            operation_type: Type of operation (batch_metadata, production_log)
            data: Data to be saved
            priority: Priority level (0 = normal, higher = more important)
            
        Returns:
            True if successfully queued
        """
        try:
            queue = self._load_queue()
            
            operation = {
                'id': self._generate_operation_id(),
                'type': operation_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'retry_count': 0,
                'priority': priority,
                'last_error': None
            }
            
            queue.append(operation)
            self._save_queue(queue)
            
            logger.info(f"Operation queued: {operation_type} (ID: {operation['id']})")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing operation: {e}")
            return False
    
    def process_queue(self, supabase_client) -> Tuple[int, int]:
        """
        Process all queued operations with Supabase client.
        
        Args:
            supabase_client: SupabaseClient instance to use for operations
            
        Returns:
            Tuple of (success_count, failed_count)
        """
        if not supabase_client or not supabase_client.is_connected:
            logger.warning("Cannot process queue: Supabase not connected")
            return 0, 0
        
        queue = self._load_queue()
        if not queue:
            logger.debug("Queue is empty, nothing to process")
            return 0, 0
        
        success_count = 0
        failed_count = 0
        remaining_queue = []
        
        # Sort by priority (higher first) then by timestamp (older first)
        queue.sort(key=lambda x: (-x.get('priority', 0), x.get('timestamp', '')))
        
        logger.info(f"Processing {len(queue)} queued operations...")
        
        for operation in queue:
            op_type = operation.get('type')
            op_data = operation.get('data')
            op_id = operation.get('id')
            retry_count = operation.get('retry_count', 0)
            
            # Skip if max retries exceeded
            if retry_count >= self.max_retries:
                logger.warning(
                    f"Operation {op_id} exceeded max retries ({self.max_retries}), "
                    f"removing from queue"
                )
                failed_count += 1
                continue
            
            # Try to process the operation
            success = False
            error_msg = None
            
            try:
                if op_type == self.BATCH_METADATA:
                    result = supabase_client.insert_batch_metadata(op_data)
                    success = result is not None
                    
                elif op_type == self.PRODUCTION_LOG:
                    result = supabase_client.insert_production_log(op_data)
                    success = result is not None
                    
                else:
                    logger.error(f"Unknown operation type: {op_type}")
                    failed_count += 1
                    continue
                
                if success:
                    logger.info(f"Successfully processed operation {op_id} ({op_type})")
                    success_count += 1
                else:
                    error_msg = "Operation returned None"
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Failed to process operation {op_id}: {error_msg}")
                
                # Increment retry count and add back to queue
                operation['retry_count'] = retry_count + 1
                operation['last_error'] = error_msg
                operation['last_retry'] = datetime.now().isoformat()
                remaining_queue.append(operation)
                failed_count += 1
        
        # Save remaining queue
        self._save_queue(remaining_queue)
        
        logger.info(
            f"Queue processing complete: {success_count} succeeded, "
            f"{failed_count} failed, {len(remaining_queue)} remaining"
        )
        
        return success_count, failed_count
    
    def get_queue_count(self) -> int:
        """
        Get count of pending operations in queue.
        
        Returns:
            Number of pending operations
        """
        queue = self._load_queue()
        return len(queue)
    
    def get_queue_info(self) -> Dict[str, Any]:
        """
        Get detailed information about queue.
        
        Returns:
            Dictionary with queue statistics
        """
        queue = self._load_queue()
        
        batch_metadata_count = sum(1 for op in queue if op.get('type') == self.BATCH_METADATA)
        production_log_count = sum(1 for op in queue if op.get('type') == self.PRODUCTION_LOG)
        
        oldest_timestamp = None
        if queue:
            oldest_timestamp = min(op.get('timestamp', '') for op in queue)
        
        return {
            'total_count': len(queue),
            'batch_metadata_count': batch_metadata_count,
            'production_log_count': production_log_count,
            'oldest_timestamp': oldest_timestamp
        }
    
    def clear_queue(self) -> bool:
        """
        Clear all operations from queue.
        
        Returns:
            True if successful
        """
        try:
            self._save_queue([])
            logger.info("Queue cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            return False
    
    def _load_queue(self) -> List[Dict[str, Any]]:
        """Load queue from file."""
        if not self.queue_file.exists():
            return []
        
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
                return queue if isinstance(queue, list) else []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading queue: {e}")
            return []
    
    def _save_queue(self, queue: List[Dict[str, Any]]) -> None:
        """Save queue to file."""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving queue: {e}")
            raise
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"op_{timestamp}"


# Global singleton instance
_offline_queue: Optional[OfflineQueue] = None


def get_offline_queue(queue_dir: str = "logs") -> OfflineQueue:
    """Get or create OfflineQueue singleton instance."""
    global _offline_queue
    if _offline_queue is None:
        _offline_queue = OfflineQueue(queue_dir=queue_dir)
    return _offline_queue

