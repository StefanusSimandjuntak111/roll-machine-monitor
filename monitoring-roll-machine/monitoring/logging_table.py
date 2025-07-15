import json
import os
from datetime import datetime, date
from typing import List, Dict, Any
import logging

class LoggingTable:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.max_entries = 50
        self.ensure_logs_directory()
        
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
        """Save production data to today's log file"""
        filename = self.get_today_filename()
        existing_data = self.load_today_data()
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
            
        existing_data.append(data)
        
        # Keep only the last max_entries
        if len(existing_data) > self.max_entries:
            existing_data = existing_data[-self.max_entries:]
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving log data: {e}")
            
    def get_last_50_entries(self) -> List[Dict[str, Any]]:
        """Get the last 50 entries from today's log"""
        data = self.load_today_data()
        return data[-self.max_entries:] if len(data) > self.max_entries else data
        
    def log_production_data(self, 
                          product_name: str,
                          product_code: str,
                          product_length: float,
                          batch: str,
                          time_to_print: float,
                          time_to_roll: float):
        """Log production data with all required fields"""
        data = {
            'product_name': product_name,
            'product_code': product_code,
            'product_length': product_length,
            'batch': batch,
            'time_to_print': time_to_print,  # waktu dari mesin tidak menggulung sampai ke print
            'time_to_roll': time_to_roll,    # waktu dari print ke gulung lagi
            'timestamp': datetime.now().isoformat()
        }
        self.save_data(data) 