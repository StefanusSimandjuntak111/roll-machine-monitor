"""
Manajemen sesi monitoring dan ekspor data.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from .exporter import export_to_csv

logger = logging.getLogger(__name__)

class MonitoringSession:
    """Manajemen sesi monitoring dan ekspor data."""
    def __init__(self, export_dir: str = "exports") -> None:
        self.export_dir = export_dir
        self.data: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self._ensure_export_dir()

    def _ensure_export_dir(self) -> None:
        """Pastikan direktori ekspor ada."""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def start(self) -> None:
        """Mulai sesi monitoring baru."""
        self.start_time = datetime.now()
        self.data = []
        logger.info(f"Sesi monitoring dimulai: {self.start_time}")

    def add_data(self, data: Dict[str, Any]) -> None:
        """Tambah data monitoring ke sesi."""
        if not self.start_time:
            self.start()
        data_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **data
        }
        self.data.append(data_with_timestamp)

    def end(self) -> str:
        """Akhiri sesi dan ekspor data ke CSV."""
        self.end_time = datetime.now()
        if not self.start_time:
            raise ValueError("Sesi belum dimulai")
        
        # Format nama file: YYYY-MM-DD_HH-MM-SS.csv
        filename = self.start_time.strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        filepath = os.path.join(self.export_dir, filename)
        
        export_to_csv(self.data, filepath)
        logger.info(f"Sesi monitoring berakhir: {self.end_time}")
        logger.info(f"Data diekspor ke: {filepath}")
        
        return filepath

    def get_current_values(self) -> Dict[str, Any]:
        """Ambil nilai terkini dari data monitoring."""
        if not self.data:
            return {}
        return self.data[-1] 