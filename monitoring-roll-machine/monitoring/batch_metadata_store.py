"""
Local storage for batch metadata.
Provides persistent storage and retrieval of batch metadata in local JSON file.
"""
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pathlib import Path

logger = logging.getLogger(__name__)


class BatchMetadataStore:
    """Local storage manager for batch metadata."""
    
    def __init__(self, data_dir: str = "logs"):
        """
        Initialize batch metadata store.
        
        Args:
            data_dir: Directory to store batch metadata file
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.metadata_file = self.data_dir / "batch_metadata.json"
    
    def save_batch_metadata(self, batch_data: Dict[str, Any]) -> bool:
        """
        Save batch metadata to local storage.
        
        Args:
            batch_data: Dictionary containing batch metadata
            
        Returns:
            True if successfully saved
        """
        try:
            batch_number = batch_data.get('batch')
            if not batch_number:
                logger.error("Cannot save batch metadata: 'batch' field is missing")
                return False
            
            # Load existing metadata
            all_metadata = self._load_all_metadata()
            
            # Ensure created_at timestamp exists
            if 'created_at' not in batch_data:
                batch_data['created_at'] = datetime.now().isoformat()
            
            # Update or add batch metadata (upsert)
            all_metadata[batch_number] = batch_data
            
            # Save to file
            self._save_all_metadata(all_metadata)
            
            logger.info(f"Batch metadata saved locally: {batch_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving batch metadata to local storage: {e}")
            return False
    
    def load_batch_metadata(self, batch: str) -> Optional[Dict[str, Any]]:
        """
        Load specific batch metadata from local storage.
        
        Args:
            batch: Batch number to load
            
        Returns:
            Batch metadata dictionary or None if not found
        """
        try:
            all_metadata = self._load_all_metadata()
            return all_metadata.get(batch)
            
        except Exception as e:
            logger.error(f"Error loading batch metadata from local storage: {e}")
            return None
    
    def get_all_batches(self, date_str: Optional[str] = None) -> List[str]:
        """
        Get list of all batch numbers from local storage.
        
        Args:
            date_str: Optional date filter in YYYY-MM-DD format
            
        Returns:
            List of batch numbers sorted by creation date (newest first)
        """
        try:
            all_metadata = self._load_all_metadata()
            
            # Filter by date if specified
            if date_str:
                filtered_batches = []
                for batch_num, metadata in all_metadata.items():
                    created_at = metadata.get('created_at', '')
                    if created_at and created_at.startswith(date_str):
                        filtered_batches.append(batch_num)
                
                # Sort by batch number (descending)
                filtered_batches.sort(reverse=True)
                return filtered_batches
            else:
                # Return all batches sorted by created_at timestamp (newest first)
                batches_with_time = [
                    (batch_num, metadata.get('created_at', ''))
                    for batch_num, metadata in all_metadata.items()
                ]
                batches_with_time.sort(key=lambda x: x[1], reverse=True)
                return [batch_num for batch_num, _ in batches_with_time]
            
        except Exception as e:
            logger.error(f"Error getting batches from local storage: {e}")
            return []
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all batch metadata.
        
        Returns:
            Dictionary mapping batch numbers to metadata
        """
        return self._load_all_metadata()
    
    def delete_batch_metadata(self, batch: str) -> bool:
        """
        Delete specific batch metadata from local storage.
        
        Args:
            batch: Batch number to delete
            
        Returns:
            True if successfully deleted
        """
        try:
            all_metadata = self._load_all_metadata()
            
            if batch in all_metadata:
                del all_metadata[batch]
                self._save_all_metadata(all_metadata)
                logger.info(f"Batch metadata deleted locally: {batch}")
                return True
            else:
                logger.warning(f"Batch {batch} not found in local storage")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting batch metadata from local storage: {e}")
            return False
    
    def get_batch_count(self) -> int:
        """
        Get total count of batches in local storage.
        
        Returns:
            Number of batches stored
        """
        all_metadata = self._load_all_metadata()
        return len(all_metadata)
    
    def _load_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load all metadata from file."""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return metadata if isinstance(metadata, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading batch metadata file: {e}")
            return {}
    
    def _save_all_metadata(self, metadata: Dict[str, Dict[str, Any]]) -> None:
        """Save all metadata to file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving batch metadata file: {e}")
            raise


# Global singleton instance
_batch_metadata_store: Optional[BatchMetadataStore] = None


def get_batch_metadata_store(data_dir: str = "logs") -> BatchMetadataStore:
    """Get or create BatchMetadataStore singleton instance."""
    global _batch_metadata_store
    if _batch_metadata_store is None:
        _batch_metadata_store = BatchMetadataStore(data_dir=data_dir)
    return _batch_metadata_store

