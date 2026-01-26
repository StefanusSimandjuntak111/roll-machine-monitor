"""
Supabase client untuk integrasi database cloud.
Mengelola koneksi dan operasi CRUD ke Supabase.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client untuk integrasi dengan Supabase database."""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Inisialisasi Supabase client dengan credentials.

        Args:
            url: Supabase project URL (dari config atau environment)
            key: Supabase API key (dari config atau environment)
        """
        # Try to get credentials from config first, then environment variables
        from .config import load_config
        config = load_config()

        self.url: str = url or config.get("supabase_url", "") or os.getenv("SUPABASE_URL", "")
        self.key: str = key or config.get("supabase_key", "") or os.getenv("SUPABASE_KEY", "")
        self.client: Optional[Client] = None
        self._connected: bool = False

        if not self.url or not self.key:
            logger.warning("Supabase credentials not provided - please configure in settings")
            return

        try:
            self.client = create_client(self.url, self.key)
            self._connected = True
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check apakah client terhubung dengan Supabase."""
        return self._connected and self.client is not None
    
    def insert_production_log(self, data: Dict[str, Any], queue_on_fail: bool = True) -> Optional[Dict[str, Any]]:
        """
        Insert production log data ke Supabase.
        
        Args:
            data: Dictionary berisi data produksi
            queue_on_fail: If True, add to offline queue on failure
            
        Returns:
            Response dari Supabase atau None jika gagal
        """
        if not self.is_connected:
            logger.warning("Supabase client not connected")
            if queue_on_fail:
                self._queue_failed_operation('production_log', data)
            return None
            
        try:
            # Pastikan timestamp dalam format ISO
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            # Insert ke tabel production_logs
            response = self.client.table('production_logs').insert(data).execute()
            logger.info(f"Production log inserted successfully: {data.get('batch', 'Unknown')}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error inserting production log to Supabase: {e}")
            if queue_on_fail:
                self._queue_failed_operation('production_log', data)
            return None
    
    def get_logs_by_batch(self, batch: str) -> List[Dict[str, Any]]:
        """
        Ambil semua logs untuk batch tertentu.
        
        Args:
            batch: Nomor batch
            
        Returns:
            List of production logs
        """
        if not self.is_connected:
            logger.warning("Supabase client not connected")
            return []
            
        try:
            response = self.client.table('production_logs')\
                .select('*')\
                .eq('batch', batch)\
                .order('timestamp', desc=False)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error fetching logs by batch from Supabase: {e}")
            return []
    
    def get_logs_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Ambil semua logs untuk tanggal tertentu.
        
        Args:
            date_str: Tanggal dalam format YYYY-MM-DD
            
        Returns:
            List of production logs
        """
        if not self.is_connected:
            logger.warning("Supabase client not connected")
            return []
            
        try:
            # Supabase menggunakan timestamp, jadi kita filter dengan range
            start_datetime = f"{date_str}T00:00:00"
            end_datetime = f"{date_str}T23:59:59"
            
            response = self.client.table('production_logs')\
                .select('*')\
                .gte('timestamp', start_datetime)\
                .lte('timestamp', end_datetime)\
                .order('timestamp', desc=False)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error fetching logs by date from Supabase: {e}")
            return []
    
    def get_batch_summary(self, batch: str) -> Optional[Dict[str, Any]]:
        """
        Ambil summary/rekap untuk batch tertentu.
        
        Args:
            batch: Nomor batch
            
        Returns:
            Dictionary berisi summary data atau None
        """
        logs = self.get_logs_by_batch(batch)
        
        if not logs:
            return None
        
        total_rolls = len(logs)
        # Gunakan length_print jika tersedia (dengan tolerance), fallback ke product_length
        total_length = sum(
            log.get('length_print') if log.get('length_print') is not None else log.get('product_length', 0)
            for log in logs
        )
        avg_cycle_time = sum(log.get('cycle_time', 0) or 0 for log in logs) / total_rolls if total_rolls > 0 else 0
        avg_roll_time = sum(log.get('roll_time', 0) for log in logs) / total_rolls if total_rolls > 0 else 0
        
        # Get product info from first log
        first_log = logs[0]
        
        return {
            'batch': batch,
            'product_code': first_log.get('product_code', 'Unknown'),
            'product_name': first_log.get('product_name', 'Unknown'),
            'total_rolls': total_rolls,
            'total_length': total_length,
            'avg_cycle_time': avg_cycle_time,
            'avg_roll_time': avg_roll_time,
            'start_time': logs[0].get('timestamp'),
            'end_time': logs[-1].get('timestamp'),
            'logs': logs
        }
    
    def get_all_batches(self, date_str: Optional[str] = None) -> List[str]:
        """
        Ambil daftar semua batch dari batch_metadata table.
        
        Args:
            date_str: Optional tanggal dalam format YYYY-MM-DD (filter berdasarkan created_at)
            
        Returns:
            List of unique batch numbers
        """
        if not self.is_connected:
            logger.warning("Supabase client not connected")
            return []
            
        try:
            # Query batch_metadata table untuk mendapatkan daftar batch
            query = self.client.table('batch_metadata').select('batch, created_at')
            
            if date_str:
                # Filter berdasarkan tanggal created_at
                start_datetime = f"{date_str}T00:00:00"
                end_datetime = f"{date_str}T23:59:59"
                query = query.gte('created_at', start_datetime).lte('created_at', end_datetime)
            
            # Order by batch descending
            query = query.order('batch', desc=True)
            
            response = query.execute()
            
            # Extract batch numbers (already sorted by query)
            batches = [item.get('batch') for item in response.data if item.get('batch')]
            
            logger.info(f"Fetched {len(batches)} batches from batch_metadata: {batches}")
            return batches
            
        except Exception as e:
            logger.error(f"Error fetching batches from Supabase: {e}")
            return []
    
    def insert_batch_metadata(self, batch_data: Dict[str, Any], queue_on_fail: bool = True) -> Optional[Dict[str, Any]]:
        """
        Insert atau update batch metadata.
        
        Args:
            batch_data: Dictionary berisi metadata batch
            queue_on_fail: If True, add to offline queue on failure
            
        Returns:
            Response dari Supabase atau None jika gagal
        """
        if not self.is_connected:
            logger.warning("Supabase client not connected")
            if queue_on_fail:
                self._queue_failed_operation('batch_metadata', batch_data)
            return None
            
        try:
            # Upsert (insert or update) batch metadata
            response = self.client.table('batch_metadata')\
                .upsert(batch_data, on_conflict='batch')\
                .execute()
            
            logger.info(f"Batch metadata saved: {batch_data.get('batch', 'Unknown')}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error saving batch metadata to Supabase: {e}")
            if queue_on_fail:
                self._queue_failed_operation('batch_metadata', batch_data)
            return None
    
    def process_offline_queue(self) -> Tuple[int, int]:
        """
        Process offline queue of failed operations.
        
        Returns:
            Tuple of (success_count, failed_count)
        """
        try:
            from .offline_queue import get_offline_queue
            queue = get_offline_queue()
            return queue.process_queue(self)
        except Exception as e:
            logger.error(f"Error processing offline queue: {e}")
            return 0, 0
    
    def get_queue_count(self) -> int:
        """
        Get count of pending operations in offline queue.
        
        Returns:
            Number of pending operations
        """
        try:
            from .offline_queue import get_offline_queue
            queue = get_offline_queue()
            return queue.get_queue_count()
        except Exception as e:
            logger.error(f"Error getting queue count: {e}")
            return 0
    
    def get_queue_info(self) -> Dict[str, Any]:
        """
        Get detailed information about offline queue.
        
        Returns:
            Dictionary with queue statistics
        """
        try:
            from .offline_queue import get_offline_queue
            queue = get_offline_queue()
            return queue.get_queue_info()
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {'total_count': 0, 'batch_metadata_count': 0, 'production_log_count': 0}
    
    def _queue_failed_operation(self, operation_type: str, data: Dict[str, Any]) -> None:
        """
        Add failed operation to offline queue.
        
        Args:
            operation_type: Type of operation (batch_metadata, production_log)
            data: Data that failed to save
        """
        try:
            from .offline_queue import get_offline_queue
            queue = get_offline_queue()
            queue.add_operation(operation_type, data)
            logger.info(f"Operation queued for retry: {operation_type}")
        except Exception as e:
            logger.error(f"Error queuing failed operation: {e}")


# Global singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get atau create Supabase client singleton instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

