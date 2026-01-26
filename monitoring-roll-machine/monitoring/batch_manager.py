"""
Batch manager untuk auto-generate batch names dan tracking perubahan produk.
Format batch: Batch_{product_code}_YYYY-MM-DD_#### (contoh: Batch_BD-1_2026-01-24_0001)
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
    - Format: Batch_{product_code}_YYYY-MM-DD_#### (contoh: Batch_BD-1_2026-01-24_0001)
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
        # NOTE:
        # Batch format dikunci ke format standar sesuai requirement:
        # Batch_{product_code}_YYYY-MM-DD_####.
        # Nilai config batch_name_format tetap disimpan untuk kompatibilitas,
        # tetapi generator batch akan selalu memakai format standar ini.
        self.batch_format = self.settings.get("batch_name_format", "Batch_{product_code}_{date}")
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
        self.batch_format = self.settings.get("batch_name_format", "Batch_{product_code}_{date}")
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
    
    def update_product_and_increment(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Update product code dan increment counter jika product code berubah.
        Method ini dipanggil saat product code berubah (termasuk saat memilih BOM).
        
        Logic:
        1. Jika product_code berbeda dari current → increment counter dan generate batch baru
        2. Jika product_code sama dengan current → pakai batch yang sama (tidak increment)

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)
            color_code: Kode warna (optional)
            additional_data: Data tambahan untuk format variables (optional)

        Returns:
            Batch name dalam format custom + auto increment
        """
        # Check jika product berbeda dari current → increment counter dan generate batch baru
        if self.current_product_code != product_code:
            # Increment counter saat product code berubah
            self.current_counter += 1
            logger.info(f"Product changed from '{self.current_product_code}' to '{product_code}' - incrementing counter to {self.current_counter}")
            
            # Update product code
            self.current_product_code = product_code
            
            # Generate batch baru dengan counter yang sudah di-increment
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
            
            logger.info(f"New batch generated after product change: {self.current_batch}")
            return self.current_batch
        
        # Product sama dengan current → pakai batch yang sama (tidak increment)
        if not self.current_batch:
            # Fallback jika batch belum di-set (first run) - increment counter untuk pertama kali
            self.current_counter += 1
            logger.info(f"First product '{product_code}' - incrementing counter to {self.current_counter}")
            self.current_product_code = product_code
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
            logger.info(f"First batch generated: {self.current_batch}")
        else:
            logger.info(f"Same product '{product_code}' - keeping batch {self.current_batch} (counter not incremented)")

        return self.current_batch
    
    def get_batch_for_product(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Get atau generate batch name untuk product code menggunakan custom format.
        TIDAK increment counter - hanya return batch yang sesuai dengan product code.
        Method ini digunakan untuk preview atau display saja.

        Logic:
        1. Jika product_code berbeda dari current → generate batch baru TANPA increment counter
        2. Jika product_code sama dengan current → pakai batch yang sama

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)
            color_code: Kode warna (optional)
            additional_data: Data tambahan untuk format variables (optional)

        Returns:
            Batch name dalam format custom + auto increment (contoh: 2024-01-15_BD-1_001_0001)
        """
        # Check jika product berbeda dari current → generate batch baru TANPA increment counter
        if self.current_product_code != product_code:
            logger.info(f"Product changed from '{self.current_product_code}' to '{product_code}' - generating new batch (counter not incremented yet)")
            # Update product code tapi TIDAK increment counter
            self.current_product_code = product_code
            # Generate batch dengan counter saat ini (belum di-increment)
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
            return self.current_batch

        # Product sama dengan current → pakai batch yang sama
        if not self.current_batch:
            # Fallback jika batch belum di-set (first run)
            logger.info(f"First product '{product_code}' - generating batch (counter not incremented yet)")
            self.current_product_code = product_code
            self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
            self._save_state()
        else:
            logger.info(f"Same product '{product_code}' - keeping batch {self.current_batch}")

        return self.current_batch
    
    def increment_and_get_batch(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Get batch name untuk print (TIDAK increment counter).
        Method ini dipanggil saat Print button diklik.
        
        Counter hanya increment saat product code berubah, bukan saat print.
        Method ini hanya return batch yang sudah ada.

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)
            color_code: Kode warna (optional)
            additional_data: Data tambahan untuk format variables (optional)

        Returns:
            Batch name untuk print (tidak increment counter)
        """
        # Update product code jika berbeda (untuk konsistensi)
        if self.current_product_code != product_code:
            logger.warning(f"Product code mismatch: current='{self.current_product_code}', print='{product_code}' - updating")
            self.current_product_code = product_code
            # Generate batch jika belum ada
            if not self.current_batch:
                self.current_batch = self._generate_batch_name(product_code, color_code, additional_data)
                self._save_state()
        
        logger.info(f"Print button clicked - using batch: {self.current_batch} (counter: {self.current_counter}, no increment on print)")
        
        return self.current_batch
    
    def get_next_batch_preview(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Get batch preview untuk print berikutnya (dengan counter + 1, tanpa increment counter).
        Method ini dipanggil setelah print selesai atau saat product code berubah untuk menampilkan batch berikutnya.

        Args:
            product_code: Kode produk (contoh: K-CR-1, K-CR-2)
            color_code: Kode warna (optional)
            additional_data: Data tambahan untuk format variables (optional)

        Returns:
            Batch name preview untuk print berikutnya (dengan counter + 1)
        """
        # Update product code jika berbeda (untuk konsistensi)
        if self.current_product_code != product_code:
            self.current_product_code = product_code
            logger.info(f"Product code updated to '{product_code}' for batch preview")
        
        # Generate batch dengan counter + 1 untuk preview (tanpa increment counter)
        preview_counter = self.current_counter + 1
        logger.info(f"Generating next batch preview with counter {preview_counter} (current: {self.current_counter})")
        
        # Generate batch preview dengan counter + 1
        preview_batch = self._generate_batch_name_with_counter(product_code, color_code, preview_counter, additional_data)
        
        logger.info(f"Next batch preview: {preview_batch}")
        return preview_batch
    
    def _generate_batch_name_with_counter(self, product_code: str, color_code: str, counter: int, additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate batch name dengan counter yang ditentukan (untuk preview).
        Menggunakan batch_format dari settings.

        Args:
            product_code: Kode produk
            color_code: Kode warna
            counter: Counter yang akan digunakan
            additional_data: Data tambahan untuk format variables

        Returns:
            Generated batch name dengan counter yang ditentukan
        """
        try:
            now = datetime.now()
            batch_date = now.strftime("%Y-%m-%d")

            sanitized_product_code = self._sanitize_product_code(product_code or "PRODUCT")

            # Prepare data for format replacement
            format_data = {
                "product_code": sanitized_product_code,
                "date": batch_date,
                "color_code": color_code or "",
            }
            
            # Add additional data if provided
            if additional_data:
                format_data.update(additional_data)
            
            # Use custom batch format from settings
            batch_name = self.batch_format
            
            # Replace placeholders
            for key, value in format_data.items():
                placeholder = "{" + key + "}"
                batch_name = batch_name.replace(placeholder, str(value))
            
            # Add auto increment (always 4 digits)
            auto_increment = f"{counter:04d}"
            final_batch_name = f"{batch_name}_{auto_increment}"
            
            return final_batch_name
            
        except Exception as e:
            logger.error(f"Error generating batch name with counter: {e}")
            return f"BATCH_{counter:04d}"

    @staticmethod
    def _sanitize_product_code(product_code: str) -> str:
        """Sanitasi ringan agar product code aman dipakai di nama batch."""
        value = (product_code or "").strip()
        if not value:
            return "PRODUCT"

        # Hindari karakter yang berpotensi bikin masalah (path/format).
        for ch in ("/", "\\", "|", ":", "*", "?", "\"", "<", ">", "\n", "\r", "\t"):
            value = value.replace(ch, "-")
        value = " ".join(value.split())  # normalize whitespace
        return value.replace(" ", "-")
    
    def _generate_batch_name(self, product_code: str, color_code: str = "", additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate batch name berdasarkan custom format dan auto increment.
        Menggunakan current_counter.
        
        Args:
            product_code: Kode produk
            color_code: Kode warna
            additional_data: Data tambahan untuk format variables
            
        Returns:
            Generated batch name
        """
        return self._generate_batch_name_with_counter(product_code, color_code, self.current_counter, additional_data)
    
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

