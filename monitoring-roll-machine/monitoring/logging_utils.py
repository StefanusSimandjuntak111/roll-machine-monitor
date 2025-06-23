"""
Utilitas untuk setup logging aplikasi.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """Setup logging dengan file rotation harian."""
    # Buat direktori log jika belum ada
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Format log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler dengan rotasi
    log_file = os.path.join(
        log_dir,
        f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("kivy").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING) 