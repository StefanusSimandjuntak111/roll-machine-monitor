"""
Batch manager untuk auto-generate batch numbers dan tracking perubahan produk.
Format batch: number only (contoh: 1, 2, 3)
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
    Manager untuk auto-generate batch numbers berdasarkan counter.
    
    Rules:
    - Format: number only (contoh: 1, 2, 3)
    - Counter bertambah SETIAP KALI ganti product_code
    - Batch baru setiap kali product_code berubah (tidak memori product sebelumnya)
    - Counter tidak direset per hari (continuous numbering)
    
    Example:
    - K-CR-1 → Batch 1
    - K-CR-1 → Batch 1 (same product, same batch)
    - K-CR-1 → Batch 1 (same product, same batch)
    - K-CR-2 → Batch 2 (different product, new batch)
    - K-CR-2 → Batch 2 (same product, same batch)
    - K-CR-3 → Batch 3 (different product, new batch)
    - K-CR-1 → Batch 4 (different from current, new batch)
    """
    
    def __init__(self, data_dir: str = "logs"):
        """
        Inisialisasi BatchManager.
        
        Args:
            data_dir: Direktori untuk menyimpan batch tracking data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.batch_file = self.data_dir / "batch_tracking.json"
        
        # State tracking
        self.current_counter: int = 0
        self.current_product_code: Optional[str] = None
        self.current_batch: Optional[str] = None
        
        # Load existing state
        self._load_state()
    
    def _load_state(self) -> None:
        """Load batch tracking state dari file."""
        if not self.batch_file.exists():
            logger.info("No existing batch tracking file found, starting fresh")
            return
        
        try:
            with open(self.batch_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.current_counter = state.get('current_counter', 0)
            self.current_product_code = state.get('current_product_code')
            self.current_batch = state.get('current_batch')
            
            logger.info(f"Loaded batch state: {self.current_batch}")
            
        except Exception as e:
            logger.error(f"Error loading batch state: {e}")
    
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
    
    def get_batch_for_product(self, product_code: str) -> str:
        """
        Get atau generate batch number untuk product code.

        Logic:
        1. Jika product_code berbeda dari current → increment counter, set batch baru
        2. Jika product_code sama dengan current → pakai batch yang sama
        
        Example:
        - K-CR-1 → Batch 1
        - K-CR-1 → Batch 1 (same product, same batch)
        - K-CR-2 → Batch 2 (different product, new batch)
        - K-CR-1 → Batch 3 (different from current, new batch)

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)

        Returns:
            Batch number dalam format number only (contoh: 1, 2, 3)
        """
        # Check jika product berbeda dari current → increment counter
        if self.current_product_code != product_code:
            logger.info(f"Product changed from '{self.current_product_code}' to '{product_code}' - incrementing batch counter")
            self.current_counter += 1
            self.current_product_code = product_code
            self.current_batch = str(self.current_counter)
            self._save_state()
            return self.current_batch

        # Product sama dengan current → pakai batch yang sama
        if not self.current_batch:
            # Fallback jika batch belum di-set (first run)
            logger.info(f"First product '{product_code}' - starting batch 1")
            self.current_counter = 1
            self.current_product_code = product_code
            self.current_batch = str(self.current_counter)
            self._save_state()
        else:
            logger.info(f"Same product '{product_code}' - keeping batch {self.current_batch}")

        return self.current_batch
    
    def force_new_batch(self, product_code: Optional[str] = None) -> str:
        """
        Force create batch baru dengan increment counter.
        
        Args:
            product_code: Optional kode produk
            
        Returns:
            Batch number baru
        """
        self.current_counter += 1
        
        if product_code:
            self.current_product_code = product_code
        
        self.current_batch = str(self.current_counter)
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
        self.current_counter = 0
        self.current_product_code = None
        self.current_batch = None
        self._save_state()


# Global singleton instance
_batch_manager: Optional[BatchManager] = None


def get_batch_manager(data_dir: str = "logs") -> BatchManager:
    """Get atau create BatchManager singleton instance."""
    global _batch_manager
    if _batch_manager is None:
        _batch_manager = BatchManager(data_dir=data_dir)
    return _batch_manager

