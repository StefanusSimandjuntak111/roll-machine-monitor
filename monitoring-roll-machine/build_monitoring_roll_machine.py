#!/usr/bin/env python3
"""
Build script for Monitoring Roll Machine application.
Follows the specifications in installer.md exactly.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("BUILDING MONITORING ROLL MACHINE v1.3.5")
    print("Following installer.md specifications exactly")
    print("=" * 60)
    
    # Set working directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check if virtual environment exists
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please create and activate venv first:")
        print("  python -m venv venv")
        print("  venv\\Scripts\\activate")
        return 1
    
    # Activate virtual environment
    print("🔧 Activating virtual environment...")
    activate_script = venv_path / "Scripts" / "activate.bat"
    if os.name == 'nt':  # Windows
        os.system(f'call "{activate_script}" && set')
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found! Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Check if main.py exists, if not use __main__.py
    main_file = "monitoring/main.py"
    if not os.path.exists(main_file):
        main_file = "monitoring/__main__.py"
        print(f"⚠️  main.py not found, using {main_file}")
    
    # Check if icon.ico exists
    icon_file = "monitoring/ui/assets/icon.ico"
    if not os.path.exists(icon_file):
        print(f"⚠️  {icon_file} not found, building without icon")
        icon_file = None
    
    # Check if config.ini exists
    config_file = "config.ini"
    if not os.path.exists(config_file):
        print(f"⚠️  {config_file} not found, using config.json instead")
        config_file = "monitoring/config.json"
    
    # Build PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name=Monitoring-Roll-Machine-v1.3.5",  # Executable name
        f"--distpath={project_root}/dist",  # Output directory
        f"--workpath={project_root}/build",  # Build directory
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite without asking
    ]
    
    # Add icon if exists
    if icon_file and os.path.exists(icon_file):
        cmd.append(f"--icon={icon_file}")
    
    # Add main file
    cmd.append(main_file)
    
    # Add additional files
    additional_files = [
        (config_file, "."),  # Config file to root
        ("requirements.txt", "."),  # Requirements to root
        ("README.md", "."),  # README to root
    ]
    
    for src, dst in additional_files:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
    
    # Add monitoring package
    cmd.extend(["--add-data", f"monitoring{os.pathsep}monitoring"])
    
    print("🚀 Building with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    # Execute PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        
        # Check output
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                print(f"📦 Executable created: {exe_file}")
                print(f"📏 Size: {exe_file.stat().st_size / (1024*1024):.2f} MB")
                
                # Move to releases directory
                releases_dir = project_root / "releases"
                releases_dir.mkdir(exist_ok=True)
                
                target_file = releases_dir / exe_file.name
                shutil.move(str(exe_file), str(target_file))
                print(f"📁 Moved to: {target_file}")
                
                return 0
            else:
                print("❌ No executable found in dist directory")
                return 1
        else:
            print("❌ Dist directory not created")
            return 1
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

