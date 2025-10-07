"""
Batch manager untuk auto-generate batch names dan tracking perubahan produk.
Format batch: Custom format dari Batch Name Settings + auto increment (contoh: 2024-01-15_BD-1_001_0001)
"""
import json
import os
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BatchManager:
    """
    Manager untuk auto-generate batch names berdasarkan counter dan custom format.
    
    Rules:
    - Format: Custom format dari Batch Name Settings + auto increment (contoh: 2024-01-15_BD-1_001_0001)
    - Counter bertambah SETIAP KALI ganti product_code
    - Batch baru setiap kali product_code berubah (tidak memori product sebelumnya)
    - Counter tidak direset per hari (continuous numbering)
    - Auto increment menggunakan format 4 digit dengan leading zero (0001, 0002, dst)
    
    Example:
    - K-CR-1 → Batch 2024-01-15_BD-1_001_0001
    - K-CR-1 → Batch 2024-01-15_BD-1_001_0001 (same product, same batch)
    - K-CR-1 → Batch 2024-01-15_BD-1_001_0001 (same product, same batch)
    - K-CR-2 → Batch 2024-01-15_BD-2_002_0002 (different product, new batch)
    - K-CR-2 → Batch 2024-01-15_BD-2_002_0002 (same product, same batch)
    - K-CR-3 → Batch 2024-01-15_BD-3_003_0003 (different product, new batch)
    - K-CR-1 → Batch 2024-01-15_BD-1_001_0004 (different from current, new batch)
    """
    
    def __init__(self, data_dir: str = "logs", settings: Optional[Dict[str, Any]] = None):
        """
        Inisialisasi BatchManager.
        
        Args:
            data_dir: Direktori untuk menyimpan batch tracking data
            settings: Dictionary berisi settings untuk batch name format
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.batch_file = self.data_dir / "batch_tracking.json"
        
        # Batch name settings
        self.settings = settings or {}
        self.batch_format = self.settings.get("batch_name_format", "YYYY-MM-DD_product-code_color-code")
        self.start_number = int(self.settings.get("batch_start_number", "1"))
        
        # State tracking
        self.current_counter: int = self.start_number - 1  # Start from start_number - 1 so first increment gives start_number
        self.current_product_code: Optional[str] = None
        self.current_batch: Optional[str] = None

        # Load existing state
        self._load_state()
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update batch name settings.

        Args:
            settings: Dictionary berisi settings untuk batch name format
        """
        old_start_number = self.start_number
        self.settings = settings
        self.batch_format = self.settings.get("batch_name_format", "YYYY-MM-DD_product-code_color-code")
        self.start_number = int(self.settings.get("batch_start_number", "1"))

        # If start_number changed, reset counter to start_number - 1 so next increment gives start_number
        if self.start_number != old_start_number:
            self.current_counter = self.start_number - 1
            self.current_batch = None  # Reset current batch so next generation uses new counter
            self.current_product_code = None
            self._save_state()
            logger.info(f"Start number changed from {old_start_number} to {self.start_number}, reset counter to {self.current_counter}")

        logger.info(f"Updated batch settings - Format: {self.batch_format}, Start: {self.start_number}")
    
    def _load_state(self) -> None:
        """Load batch tracking state dari file."""
        if not self.batch_file.exists():
            logger.info("No existing batch tracking file found, starting fresh")
            return

        try:
            with open(self.batch_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.current_counter = state.get('current_counter', self.start_number - 1)
            self.current_product_code = state.get('current_product_code')
            self.current_batch = state.get('current_batch')

            logger.info(f"Loaded batch state: {self.current_batch}")

        except Exception as e:
            logger.error(f"Error loading batch state: {e}")
            # Fallback to default
            self.current_counter = self.start_number - 1
    
    def _save_state(self) -> None:
        """Save batch tracking state ke file."""
        try:
            state = {
                'current_counter': self.current_counter,
                'current_product_code': self.current_product_code,
                'current_batch': self.current_batch,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.batch_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved batch state: {self.current_batch}")
            
        except Exception as e:
            logger.error(f"Error saving batch state: {e}")
    
    def get_batch_for_product(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Get atau generate batch name untuk product code menggunakan custom format.

        Logic:
        1. Jika product_code berbeda dari current → increment counter, set batch baru
        2. Jika product_code sama dengan current → pakai batch yang sama
        
        Example:
        - K-CR-1 → Batch 2024-01-15_BD-1_001_0001
        - K-CR-1 → Batch 2024-01-15_BD-1_001_0001 (same product, same batch)
        - K-CR-2 → Batch 2024-01-15_BD-2_002_0002 (different product, new batch)
        - K-CR-1 → Batch 2024-01-15_BD-1_001_0003 (different from current, new batch)

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)
            color_code: Kode warna (optional)
            additional_data: Data tambahan untuk format variables (optional)

        Returns:
            Batch name dalam format custom + auto increment (contoh: 2024-01-15_BD-1_001_0001)
        """
        # Check jika product berbeda dari current → increment counter
        if self.current_product_code != product_code:
            logger.info(f"Product changed from '{self.current_product_code}' to '{product_code}' - incrementing batch counter")
            self.current_counter += 1
            self.current_product_code = product_code
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
            return self.current_batch

        # Product sama dengan current → pakai batch yang sama
        if not self.current_batch:
            # Fallback jika batch belum di-set (first run)
            logger.info(f"First product '{product_code}' - starting batch")
            self.current_product_code = product_code
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
        else:
            logger.info(f"Same product '{product_code}' - keeping batch {self.current_batch}")

        return self.current_batch
    
    def _generate_batch_name(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate batch name berdasarkan custom format dan auto increment.
        
        Args:
            product_code: Kode produk
            color_code: Kode warna
            additional_data: Data tambahan untuk format variables
            
        Returns:
            Generated batch name
        """
        try:
            # Get current data
            now = datetime.now()
            
            # Default data
            data = {
                "date": now.strftime("%Y-%m-%d"),
                "product_code": product_code or "PRODUCT",
                "color_code": color_code or "COLOR", 
                "time": now.strftime("%H-%M"),
                "length": "25.5",
                "operator": "OP001"
            }
            
            # Add additional data if provided
            if additional_data:
                data.update(additional_data)
            
            # Replace variables in custom format
            batch_name = self.batch_format
            for key, value in data.items():
                batch_name = batch_name.replace(f"{{{key}}}", str(value))
            
            # Add auto increment part (4 digits with leading zeros)
            auto_increment = f"{self.current_counter:04d}"
            final_batch_name = f"{batch_name}_{auto_increment}"
            
            return final_batch_name
            
        except Exception as e:
            logger.error(f"Error generating batch name: {e}")
            return f"BATCH_{self.current_counter:04d}"
    
    def force_new_batch(self, product_code: Optional[str] = None, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Force create batch baru dengan increment counter.
        
        Args:
            product_code: Optional kode produk
            color_code: Optional kode warna
            additional_data: Data tambahan untuk format variables
            
        Returns:
            Batch name baru
        """
        self.current_counter += 1
        
        if product_code:
            self.current_product_code = product_code
        
        self.current_batch = self._generate_batch_name(product_code or "", color_code, additional_data)
        self._save_state()
        
        logger.info(f"Forced new batch: {self.current_batch}")
        return self.current_batch
    
    def get_current_batch(self) -> Optional[str]:
        """Get batch number yang sedang aktif."""
        return self.current_batch
    
    def get_batch_info(self) -> Dict[str, Any]:
        """
        Get informasi lengkap tentang batch saat ini.
        
        Returns:
            Dictionary berisi info batch
        """
        return {
            'batch': self.current_batch,
            'counter': self.current_counter,
            'product_code': self.current_product_code
        }
    
    def reset_batch(self) -> None:
        """Reset batch tracking (untuk testing atau manual reset)."""
        logger.warning("Resetting batch tracking state")
        self.current_counter = self.start_number - 1
        self.current_product_code = None
        self.current_batch = None
        self._save_state()


# Global singleton instance
_batch_manager: Optional[BatchManager] = None


def get_batch_manager(data_dir: str = "logs", settings: Optional[Dict[str, Any]] = None) -> BatchManager:
    """Get atau create BatchManager singleton instance."""
    global _batch_manager
    if _batch_manager is None:
        _batch_manager = BatchManager(data_dir=data_dir, settings=settings)
    elif settings:
        # Update settings if provided
        _batch_manager.update_settings(settings)
    return _batch_manager

