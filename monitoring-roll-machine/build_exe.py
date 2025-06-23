"""
Script untuk build executable menggunakan PyInstaller.
"""
import PyInstaller.__main__
import sys
import os

def build_exe():
    """Build executable untuk monitoring roll machine."""
    # Pastikan working directory benar
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Konfigurasi PyInstaller
    opts = [
        "monitoring/ui/kiosk_ui.py",  # Script utama
        "--name=MonitoringRollMachine",
        "--onefile",  # Bundle jadi satu file
        "--windowed",  # Tanpa console window
        "--icon=assets/icon.ico",  # Icon (jika ada)
        # Hidden imports
        "--hidden-import=kivy",
        "--hidden-import=serial",
        # Data files
        "--add-data=.env.example;.",
        # Exclude unnecessary
        "--exclude-module=matplotlib",
        "--exclude-module=notebook",
        "--exclude-module=PIL",
    ]

    # Build executable
    PyInstaller.__main__.run(opts)

if __name__ == "__main__":
    build_exe() 