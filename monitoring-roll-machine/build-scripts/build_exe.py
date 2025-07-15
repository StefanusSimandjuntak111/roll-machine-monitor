"""
Script untuk build executable menggunakan PyInstaller.
"""
import PyInstaller.__main__
import sys
import os
import platform

def build_exe():
    """Build executable untuk monitoring roll machine."""
    # Pastikan working directory benar
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Determine the main script path
    main_script = "monitoring/ui/main_window.py"
    
    # Check if main script exists
    if not os.path.exists(main_script):
        print(f"Error: Main script not found: {main_script}")
        return

    # Platform-specific configurations
    is_windows = platform.system() == "Windows"
    
    # Base configuration
    opts = [
        main_script,  # Script utama
        "--name=MonitoringRollMachine",
        "--onefile",  # Bundle jadi satu file
        "--windowed",  # Tanpa console window
        # Hidden imports
        "--hidden-import=serial",
        "--hidden-import=serial.tools.list_ports",
        "--hidden-import=pyqtgraph",
        "--hidden-import=PySide6",
        "--hidden-import=tempfile",
        "--hidden-import=platform",
        "--hidden-import=subprocess",
        # Data files
        "--add-data=monitoring/config.json;monitoring",
        "--add-data=monitoring/mock;monitoring/mock",
        # Exclude unnecessary
        "--exclude-module=matplotlib",
        "--exclude-module=notebook",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
    ]
    
    # Windows-specific options
    if is_windows:
        opts.extend([
            "--hidden-import=win32api",
            "--hidden-import=win32con",
            "--hidden-import=win32gui",
        ])
        
        # Add icon if exists
        icon_path = "assets/icon.ico"
        if os.path.exists(icon_path):
            opts.append(f"--icon={icon_path}")
    
    # Linux-specific options
    else:
        opts.extend([
            "--hidden-import=fcntl",
        ])

    print(f"Building executable for {platform.system()}...")
    print(f"Main script: {main_script}")
    print(f"Options: {opts}")
    
    # Build executable
    PyInstaller.__main__.run(opts)
    
    print("Build completed!")

if __name__ == "__main__":
    build_exe() 