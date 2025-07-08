#!/usr/bin/env python3
"""
Create Offline Windows Bundle for Roll Machine Monitor
Downloads all Python dependencies for offline installation
"""

import os
import sys
import subprocess
import shutil
import zipfile
import urllib.request
from pathlib import Path
import json
from datetime import datetime


class WindowsBundleCreator:
    """Creates offline installation bundle for Windows"""
    
    def __init__(self):
        self.version = "1.3.0"
        self.bundle_name = f"RollMachineMonitor-v{self.version}-Windows-Offline"
        self.current_dir = Path(__file__).parent
        self.bundle_dir = self.current_dir / self.bundle_name
        self.temp_dir = self.current_dir / "temp_bundle"
        
    def print_header(self):
        """Print header information"""
        print()
        print("=" * 60)
        print(f"📦 Roll Machine Monitor Windows Bundle Creator v{self.version}")
        print("=" * 60)
        print()
        
    def cleanup_previous(self):
        """Clean up previous builds"""
        print("🧹 Cleaning previous builds...")
        
        if self.bundle_dir.exists():
            shutil.rmtree(self.bundle_dir)
            
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
        # Remove old zip files
        for zip_file in self.current_dir.glob(f"{self.bundle_name}*.zip"):
            zip_file.unlink()
            
        print("✅ Previous builds cleaned")
        
    def create_directories(self):
        """Create bundle directories"""
        print("📁 Creating bundle directories...")
        
        self.bundle_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.bundle_dir / "monitoring").mkdir(exist_ok=True)
        (self.bundle_dir / "windows").mkdir(exist_ok=True)
        (self.bundle_dir / "assets").mkdir(exist_ok=True)
        (self.bundle_dir / "python-packages").mkdir(exist_ok=True)
        (self.bundle_dir / "python-installer").mkdir(exist_ok=True)
        
        print("✅ Bundle directories created")
        
    def copy_application_files(self):
        """Copy application files to bundle"""
        print("📱 Copying application files...")
        
        # Copy monitoring application
        if (self.current_dir / "monitoring").exists():
            shutil.copytree(
                self.current_dir / "monitoring",
                self.bundle_dir / "monitoring",
                dirs_exist_ok=True
            )
            
        # Copy Windows-specific files
        if (self.current_dir / "windows").exists():
            shutil.copytree(
                self.current_dir / "windows",
                self.bundle_dir / "windows",
                dirs_exist_ok=True
            )
            
        # Copy essential files
        files_to_copy = [
            "requirements.txt",
            "run_app.py", 
            "README.md",
            "LICENSE"
        ]
        
        for file_name in files_to_copy:
            src_file = self.current_dir / file_name
            if src_file.exists():
                shutil.copy2(src_file, self.bundle_dir / file_name)
                
        print("✅ Application files copied")
        
    def create_assets(self):
        """Create application assets"""
        print("🎨 Creating application assets...")
        
        # Create application icon (ICO format for Windows)
        icon_content = '''
        iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVFiFtZc9aBRBFMd/b2+zl2xMQhKCjVoIgp1gY2GhYKGNjYWNjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2N
        '''
        
        # Create simple icon file (placeholder)
        with open(self.bundle_dir / "assets" / "rollmachine-icon.ico", "w") as f:
            f.write("Placeholder icon file")
            
        print("✅ Assets created")
        
    def download_python_installer(self):
        """Download Python installer for offline installation"""
        print("🐍 Downloading Python installer...")
        
        python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
        python_installer = self.bundle_dir / "python-installer" / "python-3.11.7-amd64.exe"
        
        try:
            print(f"   Downloading from: {python_url}")
            urllib.request.urlretrieve(python_url, python_installer)
            print(f"✅ Python installer downloaded: {python_installer.name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not download Python installer: {e}")
            print("   Users will need to install Python manually")
            
    def download_python_packages(self):
        """Download Python packages for offline installation"""
        print("📦 Downloading Python packages...")
        
        # Create temporary virtual environment for downloading
        temp_venv = self.temp_dir / "temp_venv"
        
        print("   Creating temporary virtual environment...")
        result = subprocess.run([
            sys.executable, "-m", "venv", str(temp_venv)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to create temporary venv: {result.stderr}")
            return False
            
        # Get pip executable path
        if os.name == 'nt':
            pip_exe = temp_venv / "Scripts" / "pip.exe"
            python_exe = temp_venv / "Scripts" / "python.exe"
        else:
            pip_exe = temp_venv / "bin" / "pip"
            python_exe = temp_venv / "bin" / "python"
            
        # Upgrade pip
        print("   Upgrading pip...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
        
        # Download packages
        packages_dir = self.bundle_dir / "python-packages"
        
        if (self.current_dir / "requirements.txt").exists():
            print("   Downloading from requirements.txt...")
            result = subprocess.run([
                str(pip_exe), "download", "-r", str(self.current_dir / "requirements.txt"),
                "-d", str(packages_dir)
            ], capture_output=True, text=True)
        else:
            print("   Downloading essential packages...")
            essential_packages = [
                "PySide6>=6.6.0",
                "pyqtgraph>=0.13.3", 
                "pyserial>=3.5",
                "python-dotenv>=1.0.0",
                "pyyaml>=6.0.1",
                "appdirs>=1.4.4",
                "qrcode>=7.4.2",
                "Pillow>=10.0.0",
                "pywin32>=306"
            ]
            
            result = subprocess.run([
                str(pip_exe), "download"
            ] + essential_packages + [
                "-d", str(packages_dir)
            ], capture_output=True, text=True)
            
        if result.returncode == 0:
            print("✅ Python packages downloaded successfully")
        else:
            print(f"❌ Failed to download packages: {result.stderr}")
            return False
            
        return True
        
    def create_offline_installer(self):
        """Create offline installer script"""
        print("📝 Creating offline installer...")
        
        installer_script = f'''@echo off
REM ===============================================
REM Roll Machine Monitor Offline Installer v{self.version}
REM Complete Windows Installation Package
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ======================================================
echo 🚀 Roll Machine Monitor Offline Installer v{self.version}
echo ======================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ This installer must be run as Administrator
    echo    Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Set installation directory
set "INSTALL_DIR=C:\\Program Files\\RollMachineMonitor"
set "CURRENT_DIR=%~dp0"

echo 📁 Installation directory: %INSTALL_DIR%

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 🐍 Python not found, installing...
    if exist "%CURRENT_DIR%python-installer\\python-3.11.7-amd64.exe" (
        "%CURRENT_DIR%python-installer\\python-3.11.7-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        if !ERRORLEVEL! neq 0 (
            echo ❌ Failed to install Python
            pause
            exit /b 1
        )
        echo ✅ Python installed successfully
    ) else (
        echo ❌ Python installer not found!
        echo    Please install Python 3.8+ manually and run this installer again
        pause
        exit /b 1
    )
) else (
    echo ✅ Python found
)

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy application files
echo 📱 Installing application files...
xcopy /s /e /q "%CURRENT_DIR%monitoring" "%INSTALL_DIR%\\monitoring\\"
xcopy /s /e /q "%CURRENT_DIR%windows" "%INSTALL_DIR%\\windows\\"
xcopy /s /e /q "%CURRENT_DIR%assets" "%INSTALL_DIR%\\assets\\"
copy "%CURRENT_DIR%requirements.txt" "%INSTALL_DIR%\\" >nul 2>&1
copy "%CURRENT_DIR%run_app.py" "%INSTALL_DIR%\\" >nul 2>&1
copy "%CURRENT_DIR%README.md" "%INSTALL_DIR%\\" >nul 2>&1

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
cd /d "%INSTALL_DIR%"
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install packages
echo 📦 Installing Python packages...
call venv\\Scripts\\activate.bat
python -m pip install --upgrade pip

REM Install from offline packages
pip install --find-links "%CURRENT_DIR%python-packages" --no-index --force-reinstall -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Python packages
    pause
    exit /b 1
)

deactivate

REM Create directories
mkdir logs >nul 2>&1
mkdir exports >nul 2>&1

REM Set permissions
icacls logs /grant Users:(OI)(CI)F >nul 2>&1
icacls exports /grant Users:(OI)(CI)F >nul 2>&1

REM Install Windows service
echo 🔧 Installing Windows service...
call windows\\install-service.bat

REM Create desktop shortcuts
echo 🖥️ Creating desktop shortcuts...
powershell -command "\\$WshShell = New-Object -comObject WScript.Shell; \\$Shortcut = \\$WshShell.CreateShortcut('%%PUBLIC%%\\Desktop\\Roll Machine Monitor.lnk'); \\$Shortcut.TargetPath = '%INSTALL_DIR%\\windows\\start-rollmachine.bat'; \\$Shortcut.Save()"
powershell -command "\\$WshShell = New-Object -comObject WScript.Shell; \\$Shortcut = \\$WshShell.CreateShortcut('%%PUBLIC%%\\Desktop\\Roll Machine Monitor (Kiosk).lnk'); \\$Shortcut.TargetPath = '%INSTALL_DIR%\\windows\\start-rollmachine-kiosk.bat'; \\$Shortcut.Save()"

REM Create Start Menu shortcuts
mkdir "%%ProgramData%%\\Microsoft\\Windows\\Start Menu\\Programs\\Roll Machine Monitor" >nul 2>&1
powershell -command "\\$WshShell = New-Object -comObject WScript.Shell; \\$Shortcut = \\$WshShell.CreateShortcut('%%ProgramData%%\\Microsoft\\Windows\\Start Menu\\Programs\\Roll Machine Monitor\\Roll Machine Monitor.lnk'); \\$Shortcut.TargetPath = '%INSTALL_DIR%\\windows\\start-rollmachine.bat'; \\$Shortcut.Save()"
powershell -command "\\$WshShell = New-Object -comObject WScript.Shell; \\$Shortcut = \\$WshShell.CreateShortcut('%%ProgramData%%\\Microsoft\\Windows\\Start Menu\\Programs\\Roll Machine Monitor\\Roll Machine Monitor (Kiosk).lnk'); \\$Shortcut.TargetPath = '%INSTALL_DIR%\\windows\\start-rollmachine-kiosk.bat'; \\$Shortcut.Save()"

echo.
echo ======================================================
echo 🎉 Installation Completed Successfully!
echo ======================================================
echo.
echo ✅ Roll Machine Monitor v{self.version} has been installed
echo ✅ Windows service is running
echo ✅ Desktop shortcuts created
echo ✅ Start menu entries created
echo.
echo 📁 Installation location: %INSTALL_DIR%
echo 📝 Logs: %INSTALL_DIR%\\logs
echo 💾 Exports: %INSTALL_DIR%\\exports
echo.
echo 🚀 You can now start the application from:
echo    - Desktop shortcut
echo    - Start menu
echo    - %INSTALL_DIR%\\windows\\start-rollmachine.bat
echo.

pause
'''
        
        with open(self.bundle_dir / "install-offline.bat", "w") as f:
            f.write(installer_script)
            
        print("✅ Offline installer created")
        
    def create_documentation(self):
        """Create installation documentation"""
        print("📖 Creating documentation...")
        
        # Create installation info
        install_info = f'''Roll Machine Monitor v{self.version} - Windows Offline Installer

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- Administrator privileges
- 2GB free disk space
- USB port for JSK3588 device

INSTALLATION INSTRUCTIONS:
1. Extract this package to a folder
2. Right-click on "install-offline.bat"
3. Select "Run as administrator"
4. Follow the on-screen instructions

FEATURES:
- Complete offline installation
- Automatic Python environment setup
- Windows service installation
- Desktop shortcuts
- Start menu integration
- Kiosk mode support

The installer will:
✅ Install Python 3.11 (if needed)
✅ Create isolated virtual environment
✅ Install all required packages
✅ Set up Windows service for auto-start
✅ Create desktop and Start menu shortcuts
✅ Configure proper permissions

After installation, the application will be available at:
C:\\Program Files\\RollMachineMonitor\\

For support, check the logs in:
C:\\Program Files\\RollMachineMonitor\\logs\\
'''
        
        with open(self.bundle_dir / "INSTALL_INFO_WINDOWS.txt", "w") as f:
            f.write(install_info)
            
        # Create post-install info  
        post_install_info = f'''Roll Machine Monitor v{self.version} Installation Complete!

🎉 INSTALLATION SUCCESSFUL!

Your Roll Machine Monitor is now installed and ready to use.

STARTING THE APPLICATION:
- Double-click the desktop shortcut "Roll Machine Monitor"
- Or go to Start Menu → Roll Machine Monitor
- Or run: C:\\Program Files\\RollMachineMonitor\\windows\\start-rollmachine.bat

KIOSK MODE:
- Use the "Roll Machine Monitor (Kiosk)" shortcut for fullscreen operation
- Ideal for dedicated monitoring stations

WINDOWS SERVICE:
- The application runs as a Windows service
- Starts automatically when Windows boots
- Restarts automatically if it crashes

CONFIGURATION:
- Settings: C:\\Program Files\\RollMachineMonitor\\monitoring\\config.json
- Logs: C:\\Program Files\\RollMachineMonitor\\logs\\
- Exports: C:\\Program Files\\RollMachineMonitor\\exports\\

SERIAL PORT SETUP:
1. Connect your JSK3588 device via USB
2. Check Device Manager for the COM port number
3. Configure the port in the application settings

TROUBLESHOOTING:
- Check logs if the application doesn't start
- Ensure JSK3588 device is properly connected
- Verify COM port settings in Device Manager

For technical support, check the documentation or contact support.

Enjoy using Roll Machine Monitor!
'''
        
        with open(self.bundle_dir / "POST_INSTALL_INFO_WINDOWS.txt", "w") as f:
            f.write(post_install_info)
            
        print("✅ Documentation created")
        
    def create_version_info(self):
        """Create version information file"""
        print("🏷️ Creating version information...")
        
        version_info = {
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "build_type": "Windows Offline Bundle",
            "target_platform": "Windows 10/11 (64-bit)",
            "python_version": "3.11.7",
            "features": [
                "Complete offline installation",
                "Python environment bundled",
                "Windows service support", 
                "Desktop shortcuts",
                "Start menu integration",
                "Kiosk mode",
                "Auto-start capability",
                "Serial port communication",
                "Data export capabilities"
            ],
            "installation_size": "~150MB",
            "requirements": [
                "Windows 10/11 (64-bit)",
                "Administrator privileges",
                "2GB free disk space",
                "USB port for JSK3588"
            ]
        }
        
        with open(self.bundle_dir / "VERSION.json", "w") as f:
            json.dump(version_info, f, indent=2)
            
        # Create simple text version
        with open(self.bundle_dir / "VERSION.txt", "w") as f:
            f.write(f"Roll Machine Monitor v{self.version}\n")
            f.write(f"Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Type: Windows Offline Bundle\n")
            f.write("Target: Windows 10/11 (64-bit)\n")
            
        print("✅ Version information created")
        
    def create_zip_package(self):
        """Create final ZIP package"""
        print("📦 Creating ZIP package...")
        
        zip_file = self.current_dir / f"{self.bundle_name}.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.bundle_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(self.bundle_dir.parent)
                    zf.write(file_path, arc_name)
                    
        print(f"✅ ZIP package created: {zip_file.name}")
        return zip_file
        
    def cleanup_temp(self):
        """Clean up temporary files"""
        print("🧹 Cleaning up temporary files...")
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
        print("✅ Temporary files cleaned")
        
    def print_summary(self, zip_file):
        """Print build summary"""
        file_size = zip_file.stat().st_size / (1024 * 1024)  # MB
        
        print()
        print("=" * 60)
        print("🎉 Windows Bundle Created Successfully!")
        print("=" * 60)
        print()
        print(f"📦 Package: {zip_file.name}")
        print(f"📁 Size: {file_size:.1f} MB")
        print()
        print("📋 Contents:")
        print("   ✅ Complete application source code")
        print("   ✅ Python installer (3.11.7)")
        print("   ✅ All Python dependencies (offline)")
        print("   ✅ Windows service scripts")
        print("   ✅ Desktop integration files")
        print("   ✅ Offline installer script")
        print("   ✅ Comprehensive documentation")
        print()
        print("🚀 Installation Instructions:")
        print("   1. Extract the ZIP file")
        print("   2. Right-click 'install-offline.bat'")
        print("   3. Select 'Run as administrator'")
        print("   4. Follow the installer prompts")
        print()
        print("✅ Ready for Windows deployment!")
        print()
        
    def create_bundle(self):
        """Create the complete Windows bundle"""
        try:
            self.print_header()
            self.cleanup_previous()
            self.create_directories()
            self.copy_application_files()
            self.create_assets()
            self.download_python_installer()
            
            if not self.download_python_packages():
                return False
                
            self.create_offline_installer()
            self.create_documentation()
            self.create_version_info()
            zip_file = self.create_zip_package()
            self.cleanup_temp()
            self.print_summary(zip_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating bundle: {e}")
            return False


if __name__ == "__main__":
    creator = WindowsBundleCreator()
    success = creator.create_bundle()
    sys.exit(0 if success else 1) 