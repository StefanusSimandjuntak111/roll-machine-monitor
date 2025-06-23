"""
Modul untuk menangani konfigurasi aplikasi.
"""
import os
import json
from typing import Dict, Any

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config() -> Dict[str, Any]:
    """Load konfigurasi dari file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    return {}

def save_config(config: Dict[str, Any]) -> None:
    """Simpan konfigurasi ke file."""
    try:
        # Pastikan hanya data yang bisa di-serialize ke JSON yang disimpan
        serializable_config = {
            k: v for k, v in config.items()
            if isinstance(v, (str, int, float, bool, list, dict))
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(serializable_config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}") 