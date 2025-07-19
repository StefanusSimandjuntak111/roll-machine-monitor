#!/usr/bin/env python3
"""
Create Offline Bundle for Roll Machine Monitor
==============================================

This script creates a complete offline bundle that includes:
- Pre-built virtual environment with all dependencies
- All application files
- Ready for distribution without internet dependency

Usage:
    python create-offline-bundle.py
"""

import os
import sys
import shutil
import subprocess
import venv
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def create_offline_bundle():
    """Create the complete offline bundle"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    bundle_dir = project_root / "venv-bundle"
    
    print("=" * 60)
    print("Creating Roll Machine Monitor Offline Bundle")
    print("=" * 60)
    
    # Clean up existing bundle
    if bundle_dir.exists():
        print(f"Removing existing bundle: {bundle_dir}")
        shutil.rmtree(bundle_dir)
    
    # Create bundle directory
    bundle_dir.mkdir(exist_ok=True)
    
    # Create virtual environment directly in bundle directory
    print("\n1. Creating virtual environment...")
    venv_path = bundle_dir / "venv"
    venv.create(venv_path, with_pip=True)
    
    # Get Python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Verify venv was created
    if not python_exe.exists():
        print(f"Error: Python executable not found at {python_exe}")
        sys.exit(1)
    
    print(f"Virtual environment created at: {venv_path}")
    
    # Upgrade pip
    print("2. Upgrading pip...")
    run_command(f'"{pip_exe}" install --upgrade pip', cwd=project_root)
    
    # Install requirements
    print("3. Installing Python requirements...")
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        run_command(f'"{pip_exe}" install -r requirements.txt', cwd=project_root)
    else:
        print("Warning: requirements.txt not found, installing basic packages...")
        # Install basic packages that are likely needed
        basic_packages = [
            "pyserial",
            "matplotlib",
            "numpy",
            "pandas"
        ]
        for package in basic_packages:
            try:
                run_command(f'"{pip_exe}" install {package}', cwd=project_root, check=False)
            except:
                print(f"Warning: Could not install {package}")
    
    # Create a simple batch file to test the bundle
    print("4. Creating test script...")
    test_script = bundle_dir / "test-bundle.bat"
    with open(test_script, 'w') as f:
        f.write("@echo off\n")
        f.write("echo Testing Roll Machine Monitor Bundle...\n")
        f.write(f'"{venv_path}\\Scripts\\python.exe" --version\n')
        f.write(f'"{venv_path}\\Scripts\\python.exe" -c "import sys; print(\"Python path:\", sys.executable)"\n')
        f.write("echo Bundle test completed.\n")
        f.write("pause\n")
    
    # Create bundle info file
    print("5. Creating bundle info...")
    info_file = bundle_dir / "BUNDLE_INFO.txt"
    with open(info_file, 'w') as f:
        f.write("Roll Machine Monitor Offline Bundle\n")
        f.write("===================================\n\n")
        f.write("This bundle contains:\n")
        f.write("- Pre-built Python virtual environment\n")
        f.write("- All required Python packages\n")
        f.write("- Ready for offline installation\n\n")
        f.write("Created: " + str(Path().cwd()) + "\n")
        f.write("Python version: " + sys.version + "\n")
        f.write("Bundle size: " + str(get_dir_size(bundle_dir)) + " bytes\n")
    
    print("\n" + "=" * 60)
    print("Offline Bundle Created Successfully!")
    print("=" * 60)
    print(f"Bundle location: {bundle_dir}")
    print(f"Bundle size: {get_dir_size(bundle_dir)} bytes")
    print("\nNext steps:")
    print("1. Build the installer using: installer-windows-offline.iss")
    print("2. Test the bundle with: test-bundle.bat")
    print("3. Distribute the installer to clients")

def get_dir_size(path):
    """Get the total size of a directory in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

if __name__ == "__main__":
    try:
        create_offline_bundle()
    except Exception as e:
        print(f"Error creating bundle: {e}")
        sys.exit(1) 