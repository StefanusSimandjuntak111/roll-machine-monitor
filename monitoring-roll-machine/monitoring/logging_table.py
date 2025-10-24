import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging
from .supabase_client import SupabaseClient
from .config import load_config

logger = logging.getLogger(__name__)


class LoggingTable:
    """
    Production logging table dengan dual-storage:
    - JSON files (local backup)
    - Supabase database (cloud storage)
    """
    
    def __init__(self, logs_dir: str = "logs", supabase_client: Optional[SupabaseClient] = None, safe_mode: bool = False):
        self.logs_dir = logs_dir
        self.max_entries = 50
        self.safe_mode = safe_mode  # Safe Mode flag
        self.ensure_logs_directory()

        # Initialize Supabase client
        self.supabase_client = supabase_client
        if self.supabase_client is None:
            config = load_config()
            if config.get('enable_supabase', False):
                self.supabase_client = SupabaseClient(
                    url=config.get('supabase_url'),
                    key=config.get('supabase_key')
                )
                logger.info("Supabase integration enabled for logging")
            else:
                logger.info("Supabase integration disabled")
        
    def ensure_logs_directory(self):
        """Ensure logs directory exists"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
    def get_today_filename(self) -> str:
        """Get filename for today's log file"""
        today = date.today()
        return os.path.join(self.logs_dir, f"production_log_{today.strftime('%Y-%m-%d')}.json")
        
    def load_today_data(self) -> List[Dict[str, Any]]:
        """Load today's production data"""
        filename = self.get_today_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
        
    def save_data(self, data: Dict[str, Any]):
        """
        Save production data to both local JSON and Supabase.
        In Safe Mode, only saves to local JSON (simulation mode).

        Args:
            data: Production data to save
        """
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()

        # 1. Save to local JSON FIRST (primary storage, always succeeds)
        filename = self.get_today_filename()
        existing_data = self.load_today_data()
        existing_data.append(data)

        # Keep only the last max_entries
        if len(existing_data) > self.max_entries:
            existing_data = existing_data[-self.max_entries:]

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            if self.safe_mode:
                logger.debug(f"SAFE MODE: Data saved to local JSON only (simulation): {filename}")
            else:
                logger.debug(f"Data saved to local JSON: {filename}")
        except Exception as e:
            logger.error(f"Error saving log data to JSON: {e}")

        # 2. Try to save to Supabase (cloud sync, auto-queues on failure) - SKIP IN SAFE MODE
        if self.safe_mode:
            logger.debug("SAFE MODE: Skipping Supabase save - simulation mode active")
            return

        if self.supabase_client:
            try:
                # insert_production_log will automatically queue if connection fails
                self.supabase_client.insert_production_log(data)
                if self.supabase_client.is_connected:
                    logger.debug(f"Data saved to Supabase: batch {data.get('batch')}")
            except Exception as e:
                logger.error(f"Error saving to Supabase: {e}")
                # No need to manually queue - insert_production_log handles it
            
    def get_last_50_entries(self) -> List[Dict[str, Any]]:
        """Get the last 50 entries from today's log, sorted by timestamp descending (newest first)"""
        data = self.load_today_data()
        
        # Sort data by timestamp in descending order (newest first)
        sorted_data = sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Return the last max_entries (which are now the newest due to reverse sort)
        return sorted_data[:self.max_entries] if len(sorted_data) > self.max_entries else sorted_data
        
    def log_production_data(self, 
                          product_name: str,
                          product_code: str,
                          product_length: float,
                          batch: str,
                          cycle_time: Optional[float],
                          roll_time: float,
                          settings_timestamp: Optional[str] = None):
        """
        Log production data with all required fields.
        
        Args:
            product_name: Nama produk
            product_code: Kode produk
            product_length: Panjang hasil rolling
            batch: Nomor batch (auto-generated)
            cycle_time: Cycle time (dapat None)
            roll_time: Roll time
            settings_timestamp: Timestamp settings terakhir
        """
        data = {
            'product_name': product_name,
            'product_code': product_code,
            'product_length': product_length,
            'batch': batch,
            'cycle_time': cycle_time,  # Time from roll length reset to 0 until next reset to 0
            'roll_time': roll_time,    # Time from roll length starting at 0 until user clicks print
            'timestamp': datetime.now().isoformat(),
            'settings_timestamp': settings_timestamp  # When settings were last changed before this entry
        }
        self.save_data(data)
    
    def get_batch_summary(self, batch: str) -> Optional[Dict[str, Any]]:
        """
        Get summary untuk batch tertentu dari Supabase atau local JSON.
        
        Args:
            batch: Nomor batch
            
        Returns:
            Dictionary berisi summary data atau None
        """
        # Try Supabase first
        if self.supabase_client and self.supabase_client.is_connected:
            try:
                summary = self.supabase_client.get_batch_summary(batch)
                if summary:
                    return summary
            except Exception as e:
                logger.error(f"Error getting batch summary from Supabase: {e}")
        
        # Fallback to local JSON
        try:
            all_data = self.load_today_data()
            batch_data = [d for d in all_data if d.get('batch') == batch]
            
            if not batch_data:
                return None
            
            total_rolls = len(batch_data)
            total_length = sum(d.get('product_length', 0) for d in batch_data)
            avg_cycle_time = sum(d.get('cycle_time', 0) or 0 for d in batch_data) / total_rolls if total_rolls > 0 else 0
            avg_roll_time = sum(d.get('roll_time', 0) for d in batch_data) / total_rolls if total_rolls > 0 else 0
            
            return {
                'batch': batch,
                'product_code': batch_data[0].get('product_code', 'Unknown'),
                'product_name': batch_data[0].get('product_name', 'Unknown'),
                'total_rolls': total_rolls,
                'total_length': total_length,
                'avg_cycle_time': avg_cycle_time,
                'avg_roll_time': avg_roll_time,
                'start_time': batch_data[0].get('timestamp'),
                'end_time': batch_data[-1].get('timestamp'),
                'logs': batch_data
            }
        except Exception as e:
            logger.error(f"Error getting batch summary from local JSON: {e}")
            return None 