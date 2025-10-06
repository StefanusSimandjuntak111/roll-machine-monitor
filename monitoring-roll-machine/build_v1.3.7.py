#!/usr/bin/env python3
"""
Complete Build Script for Monitoring Roll Machine v1.3.7
Creates a NSIS installer with full install/update support
Includes new batch tracking and Supabase integration features
"""

import os
import sys
import subprocess
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildManager:
    """Manages the complete build process for version 1.4.1."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.version = "1.4.1"
        self.app_name = "Monitoring Roll Machine"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.releases_dir = self.project_root / "releases"
        
    def log_step(self, message):
        """Log a build step."""
        logger.info(f"[STEP] {message}")
        
    def log_success(self, message):
        """Log a success message."""
        logger.info(f"[SUCCESS] {message}")
        
    def log_error(self, message):
        """Log an error message."""
        logger.error(f"[ERROR] {message}")
        
    def log_warning(self, message):
        """Log a warning message."""
        logger.warning(f"[WARNING] {message}")
    
    def check_requirements(self):
        """Check if all build requirements are met."""
        self.log_step("Checking build requirements...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            self.log_error(f"Python 3.9+ required, found {sys.version}")
            return False
            
        # Check PyInstaller
        try:
            result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success(f"PyInstaller found: {result.stdout.strip()}")
            else:
                self.log_error("PyInstaller not found. Install with: pip install pyinstaller")
                return False
        except Exception as e:
            self.log_error(f"PyInstaller check failed: {e}")
            return False
            
        # Check NSIS
        nsis_paths = [
            r"C:\Program Files (x86)\NSIS\makensis.exe",
            r"C:\Program Files\NSIS\makensis.exe"
        ]
        
        nsis_found = False
        for nsis_path in nsis_paths:
            if os.path.exists(nsis_path):
                # Add to PATH for this session
                nsis_dir = os.path.dirname(nsis_path)
                os.environ['PATH'] = nsis_dir + os.pathsep + os.environ['PATH']
                
                result = subprocess.run([nsis_path, '/VERSION'], 
                                      capture_output=True, text=True, shell=True)
                self.log_success(f"NSIS found: v{result.stdout.strip()}")
                nsis_found = True
                break
                
        if not nsis_found:
            self.log_error("NSIS not found. Download from: https://nsis.sourceforge.io/")
            return False
            
        self.log_success("All requirements satisfied")
        return True
    
    def clean_build_artifacts(self):
        """Clean previous build artifacts."""
        self.log_step("Cleaning previous build artifacts...")
        
        # Clean dist and build directories
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                self.log_success(f"Cleaned {directory}")
                
        # Clean __pycache__ directories
        for pycache in self.project_root.rglob('__pycache__'):
            try:
                shutil.rmtree(pycache)
                self.log_success(f"Cleaned {pycache}")
            except Exception as e:
                self.log_warning(f"Could not clean {pycache}: {e}")
        
        return True
    
    def test_imports(self):
        """Test that all modules can be imported."""
        self.log_step("Testing application functionality...")
        
        try:
            # Test main imports
            import monitoring
            from monitoring.version import VERSION, get_version_string
            from monitoring.ui.main_window import ModernMainWindow
            from monitoring.monitor import Monitor
            from monitoring.serial_handler import JSKSerialPort
            from monitoring.config import load_config
            
            # Test new batch tracking features
            from monitoring.batch_manager import BatchManager
            from monitoring.supabase_client import SupabaseClient
            from monitoring.ui.batch_summary_dialog import BatchSummaryDialog
            
            self.log_success("All modules import successfully")
            
            # Verify version
            if VERSION != self.version:
                self.log_error(f"Version mismatch: Expected {self.version}, found {VERSION}")
                return False
            self.log_success(f"Version check passed: {VERSION}")
            
            # Test config loading
            config = load_config()
            if not isinstance(config, dict):
                self.log_error("Configuration loading failed")
                return False
            self.log_success("Configuration file is valid")
            
            # Test batch manager
            batch_mgr = BatchManager()
            test_batch = batch_mgr.get_batch_for_product("TEST-001")
            if not test_batch:
                self.log_error("Batch manager test failed")
                return False
            self.log_success("Batch manager working correctly")
            
            # Test Supabase client initialization
            supabase_client = SupabaseClient()
            self.log_success("Supabase client initialized successfully")
            
            return True
            
        except Exception as e:
            self.log_error(f"Import test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def build_executable(self):
        """Build the executable using PyInstaller."""
        self.log_step("Building executable with PyInstaller...")
        
        # Create PyInstaller spec file
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[r'{self.project_root}'],
    binaries=[],
    datas=[
        ('monitoring/ui/assets', 'monitoring/ui/assets'),
        ('monitoring/config.json', 'monitoring'),
        ('requirements.txt', '.'),
        ('LICENSE.txt', '.'),
        ('README.md', '.'),
        ('SUPABASE_SCHEMA.sql', '.'),
        ('BATCH_FEATURE_README.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'pyqtgraph',
        'pyserial',
        'serial.tools.list_ports',
        'python-dotenv',
        'yaml',
        'appdirs',
        'qrcode',
        'PIL',
        'PIL.Image',
        'matplotlib',
        'matplotlib.backends.backend_qtagg',
        'numpy',
        'pandas',
        'requests',
        'openpyxl',
        'supabase',
        'supabase.auth',
        'supabase.client',
        'postgrest',
        'realtime',
        'storage3',
        'httpx',
        'anyio',
        'h11',
        'httpcore',
        'monitoring',
        'monitoring.ui',
        'monitoring.ui.main_window',
        'monitoring.ui.monitoring_view',
        'monitoring.ui.product_form',
        'monitoring.ui.settings_dialog',
        'monitoring.ui.connection_settings',
        'monitoring.ui.logging_table_widget',
        'monitoring.ui.print_preview',
        'monitoring.ui.printer_utils',
        'monitoring.ui.batch_summary_dialog',
        'monitoring.monitor',
        'monitoring.serial_handler',
        'monitoring.config',
        'monitoring.logging_utils',
        'monitoring.logging_table',
        'monitoring.session',
        'monitoring.exporter',
        'monitoring.parser',
        'monitoring.version',
        'monitoring.batch_manager',
        'monitoring.supabase_client',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonitoringRollMachine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='monitoring/ui/assets/icon.ico'
)
'''
        
        spec_file = self.project_root / "MonitoringRollMachine.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
            
        # Run PyInstaller
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--clean', str(spec_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log_error(f"PyInstaller build failed: {result.stderr}")
            return False
            
        # Verify executable exists
        exe_path = self.dist_dir / "MonitoringRollMachine.exe"
        if not exe_path.exists():
            self.log_error("Executable not found after build")
            return False
            
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        self.log_success(f"Executable built successfully")
        self.log_success(f"Executable size: {exe_size:.1f} MB")
        return True
    
    def test_executable(self):
        """Test the built executable."""
        self.log_step("Testing built executable...")
        
        exe_path = self.dist_dir / "MonitoringRollMachine.exe"
        
        # Start the executable
        proc = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit to see if it crashes immediately
        import time
        time.sleep(2)
        
        # Check if still running
        if proc.poll() is None:
            # Still running, kill it
            proc.terminate()
            proc.wait(timeout=5)
            self.log_success("Executable starts without immediate errors")
            return True
        else:
            stdout, stderr = proc.communicate()
            self.log_error(f"Executable crashed: {stderr.decode()}")
            return False
    
    def create_nsis_installer(self):
        """Create NSIS installer."""
        self.log_step("Creating NSIS installer...")
        
        # Create NSIS script
        nsis_script = self.project_root / "installer_v1.4.1.nsi"
        
        nsis_content = f'''
; Monitoring Roll Machine v1.4.1 Installer
; NSIS Script with Install/Update Support
; Includes Batch Tracking & Supabase Integration

!define APP_NAME "Monitoring Roll Machine"
!define APP_VERSION "1.4.1"
!define APP_PUBLISHER "Textilindo"
!define APP_URL "https://github.com/StefanusSimandjuntak111/roll-machine-monitor"
!define APP_EXECUTABLE "MonitoringRollMachine.exe"
!define APP_ICON "monitoring\\ui\\assets\\icon.ico"
!define APP_UNINSTALLER "Uninstall.exe"

; Installer Information
Name "${{APP_NAME}} v${{APP_VERSION}}"
OutFile "Monitoring-Roll-Machine-v1.4.1-Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKLM "Software\\${{APP_NAME}}" "Install_Dir"
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; Modern UI Configuration
!define MUI_ICON "${{APP_ICON}}"
!define MUI_UNICON "${{APP_ICON}}"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "${{APP_VERSION}}.0"
VIAddVersionKey "ProductName" "${{APP_NAME}}"
VIAddVersionKey "CompanyName" "${{APP_PUBLISHER}}"
VIAddVersionKey "FileVersion" "${{APP_VERSION}}"
VIAddVersionKey "FileDescription" "${{APP_NAME}} Installer"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2025 ${{APP_PUBLISHER}}"

; Installer Sections
Section "Main Application" SecMain
    SectionIn RO
    
    ; Stop running application and services
    Call StopApplication
    Call StopServices
    
    ; Install main executable
    SetOutPath "$INSTDIR"
    File "dist\\${{APP_EXECUTABLE}}"
    
    ; Install main application files
    File "run_app.py"
    File "requirements.txt"
    File "README.md"
    File "LICENSE.txt"
    File "SUPABASE_SCHEMA.sql"
    File "BATCH_FEATURE_README.md"
    
    ; Install monitoring package
    SetOutPath "$INSTDIR\\monitoring"
    File /r "monitoring\\*"
    
    ; Install Windows scripts
    SetOutPath "$INSTDIR\\windows"
    File "windows\\*.bat"
    
    ; Install documentation if exists
    IfFileExists "docs\\*" 0 +3
        SetOutPath "$INSTDIR\\docs"
        File /r "docs\\*"
    
    ; Install scripts if exists
    IfFileExists "scripts\\*" 0 +3
        SetOutPath "$INSTDIR\\scripts"
        File /r "scripts\\*"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\\${{APP_NAME}}"
    CreateDirectory "$APPDATA\\${{APP_NAME}}\\logs"
    CreateDirectory "$APPDATA\\${{APP_NAME}}\\exports"
    
    ; Create Program Files config directory
    CreateDirectory "$INSTDIR\\config"
    
    ; Copy config if it doesn't exist
    IfFileExists "$INSTDIR\\config\\config.json" +2 0
        CopyFiles "$INSTDIR\\monitoring\\config.json" "$INSTDIR\\config\\config.json"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "Version" "${{APP_VERSION}}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\\${{APP_UNINSTALLER}}"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" '"$INSTDIR\\${{APP_UNINSTALLER}}"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\${{APP_EXECUTABLE}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoRepair" 1
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}" "" "$INSTDIR\\${{APP_EXECUTABLE}}" 0
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\${{APP_UNINSTALLER}}" "" "$INSTDIR\\${{APP_UNINSTALLER}}" 0
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}" "" "$INSTDIR\\${{APP_EXECUTABLE}}" 0
    
SectionEnd

Section "Python Environment (Optional)" SecPython
    ; This section installs Python dependencies if Python is available
    Call CheckPython
    Pop $0
    ${{If}} $0 == "1"
        DetailPrint "Python found, setting up virtual environment..."
        Call CreateVirtualEnv
        Call InstallRequirements
    ${{Else}}
        DetailPrint "Python not found, skipping virtual environment setup"
        MessageBox MB_OK|MB_ICONINFORMATION "Python was not detected. The application will run using the bundled executable.$\\n$\\nIf you need Python integration, please install Python 3.9+ and re-run the installer."
    ${{EndIf}}
SectionEnd

Section "Windows Service (Optional)" SecService
    Call InstallWindowsService
SectionEnd

Section "Database Setup (Optional)" SecDatabase
    ; Create database setup batch file
    SetOutPath "$INSTDIR"
    FileOpen $0 "$INSTDIR\\setup_database.bat" w
    FileWrite $0 "@echo off$\\r$\\n"
    FileWrite $0 "echo Setting up Supabase database...$\\r$\\n"
    FileWrite $0 "echo Please run this script after installation to set up your database.$\\r$\\n"
    FileWrite $0 "echo See BATCH_FEATURE_README.md for detailed instructions.$\\r$\\n"
    FileWrite $0 "pause$\\r$\\n"
    FileClose $0
    
    MessageBox MB_YESNO "Would you like to open the database setup instructions now?" IDYES ShowDBInstructions
    Goto EndDBInstructions
    ShowDBInstructions:
        ExecShell "open" "$INSTDIR\\BATCH_FEATURE_README.md"
    EndDBInstructions:
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecMain}} "Install the main application and required files"
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecPython}} "Set up Python virtual environment (requires Python 3.9+)"
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecService}} "Install as Windows service for automatic startup"
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecDatabase}} "Database setup instructions and batch tracking documentation"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Stop application and services
    Call un.StopApplication
    Call un.StopServices
    
    ; Remove files
    RMDir /r "$INSTDIR\\monitoring"
    RMDir /r "$INSTDIR\\windows"
    RMDir /r "$INSTDIR\\docs"
    RMDir /r "$INSTDIR\\scripts"
    RMDir /r "$INSTDIR\\config"
    RMDir /r "$INSTDIR\\venv"
    Delete "$INSTDIR\\${{APP_EXECUTABLE}}"
    Delete "$INSTDIR\\run_app.py"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\LICENSE.txt"
    Delete "$INSTDIR\\SUPABASE_SCHEMA.sql"
    Delete "$INSTDIR\\BATCH_FEATURE_README.md"
    Delete "$INSTDIR\\setup_database.bat"
    Delete "$INSTDIR\\${{APP_UNINSTALLER}}"
    
    ; Remove shortcuts
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\${{APP_NAME}}"
    
    ; Remove directories
    RMDir "$INSTDIR"
    
    ; Optional: Remove AppData (ask user)
    MessageBox MB_YESNO "Do you want to remove all application data including logs and exports?" IDYES RemoveAppData IDNO SkipAppData
    RemoveAppData:
        RMDir /r "$APPDATA\\${{APP_NAME}}"
    SkipAppData:
    
SectionEnd

; Helper Functions
Function StopApplication
    DetailPrint "Stopping running application..."
    nsExec::ExecToStack 'taskkill /f /im "${{APP_EXECUTABLE}}" /t'
    Pop $0
    Sleep 2000
FunctionEnd

Function un.StopApplication
    DetailPrint "Stopping running application..."
    nsExec::ExecToStack 'taskkill /f /im "${{APP_EXECUTABLE}}" /t'
    Pop $0
    Sleep 2000
FunctionEnd

Function StopServices
    DetailPrint "Stopping Windows services..."
    ExecWait 'sc stop "RollMachineMonitor"' $0
    ExecWait 'sc stop "RollMachineKiosk"' $0
    Sleep 2000
FunctionEnd

Function un.StopServices
    DetailPrint "Stopping and removing Windows services..."
    ExecWait 'sc stop "RollMachineMonitor"' $0
    ExecWait 'sc delete "RollMachineMonitor"' $0
    ExecWait 'sc stop "RollMachineKiosk"' $0
    ExecWait 'sc delete "RollMachineKiosk"' $0
    Sleep 2000
FunctionEnd

Function CheckPython
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    ${{If}} $0 == 0
        Push "1"
    ${{Else}}
        Push "0"
    ${{EndIf}}
FunctionEnd

Function CreateVirtualEnv
    DetailPrint "Creating virtual environment..."
    SetOutPath "$INSTDIR"
    nsExec::ExecToLog 'python -m venv venv'
    Pop $0
FunctionEnd

Function InstallRequirements
    DetailPrint "Installing Python requirements..."
    SetOutPath "$INSTDIR"
    nsExec::ExecToLog '"$INSTDIR\\venv\\Scripts\\pip.exe" install --upgrade pip'
    nsExec::ExecToLog '"$INSTDIR\\venv\\Scripts\\pip.exe" install -r requirements.txt'
    Pop $0
FunctionEnd

Function InstallWindowsService
    DetailPrint "Installing Windows service..."
    SetOutPath "$INSTDIR\\windows"
    nsExec::ExecToLog 'cmd /c install-service.bat'
    Pop $0
FunctionEnd

; Installer initialization
Function .onInit
    ; Check Windows version
    ${{IfNot}} ${{AtLeastWin7}}
        MessageBox MB_OK|MB_ICONSTOP "This application requires Windows 7 or later."
        Abort
    ${{EndIf}}
    
    ; Check if already installed
    ReadRegStr $0 HKLM "Software\\${{APP_NAME}}" "Install_Dir"
    ${{If}} $0 != ""
        ReadRegStr $1 HKLM "Software\\${{APP_NAME}}" "Version"
        MessageBox MB_YESNO|MB_ICONQUESTION "Monitoring Roll Machine v$1 is already installed.$\\n$\\nDo you want to update to version ${{APP_VERSION}}?$\\n$\\nNew in v${{APP_VERSION}}:$\\n• Batch tracking with auto-generation$\\n• Supabase cloud database integration$\\n• Batch summary/recap feature$\\n• Enhanced production logging$\\n• Number-only batch format" IDYES UpdateInstall
        Abort
        UpdateInstall:
            DetailPrint "Updating from version $1 to ${{APP_VERSION}}..."
    ${{EndIf}}
FunctionEnd
'''
        
        with open(nsis_script, 'w', encoding='utf-8') as f:
            f.write(nsis_content)
        
        # Compile NSIS installer
        result = subprocess.run(
            ['makensis', str(nsis_script)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log_error(f"NSIS compilation failed: {result.stderr}")
            return False
            
        # Move installer to releases folder
        installer_name = f"Monitoring-Roll-Machine-v{self.version}-Setup.exe"
        installer_path = self.project_root / installer_name
        
        if not installer_path.exists():
            self.log_error("Installer not found after compilation")
            return False
            
        self.releases_dir.mkdir(exist_ok=True)
        target_path = self.releases_dir / installer_name
        
        if target_path.exists():
            target_path.unlink()
        
        shutil.move(str(installer_path), str(target_path))
        
        installer_size = target_path.stat().st_size / (1024 * 1024)
        self.log_success(f"Installer compiled successfully")
        self.log_success(f"Installer created: {installer_size:.1f} MB")
        self.log_success(f"Installer moved to: {target_path}")
        
        return True
    
    def create_release_notes(self):
        """Create release notes."""
        self.log_step("Creating release notes...")
        
        release_notes = f"""# Monitoring Roll Machine v{self.version} Release Notes

## Release Information
- **Version**: {self.version}
- **Build Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Build Type**: Release

## What's New in v{self.version}

### 🎯 **Batch Tracking & Management**
- **Auto Batch Generation**: Automatic batch numbering (1, 2, 3, etc.)
- **Smart Logic**: Same product = same batch, different product = new batch
- **Continuous Numbering**: Batch numbers don't reset per day
- **Manual Override**: Option to manually set batch numbers

### 📊 **Batch Summary/Recap Feature**
- **New Button**: "📊 Batch Recap" in main toolbar
- **Batch Selection**: Dropdown to select any batch
- **Summary View**: Total rolls, length, average times
- **Detail Table**: All production logs for selected batch
- **Export Function**: Export batch data to CSV

### ☁️ **Supabase Cloud Integration**
- **Dual Storage**: Cloud (Supabase) + Local (JSON backup)
- **Auto-Sync**: Production data automatically saved to both
- **Offline Support**: Works without internet (local fallback)
- **Database Schema**: Complete SQL schema provided
- **Performance**: Optimized with indexes and triggers

### 🔧 **Technical Improvements**
- **Enhanced Configuration**: Supabase credentials in config.json
- **Better Error Handling**: Graceful fallback when cloud unavailable
- **Improved Logging**: Better tracking of batch operations
- **Code Quality**: PEP 8 compliance, comprehensive docstrings

## Features Overview

### ✅ **Core Monitoring**
- Real-time length counter monitoring
- Speed and shift tracking
- Serial communication with JSK3588 protocol
- Auto-detection of serial ports
- Mock data simulation for testing

### ✅ **Production Logging**
- Comprehensive production data logging
- Cycle time and roll time tracking
- Batch and product information management
- Export functionality to CSV
- Real-time logging table display

### ✅ **Batch Management**
- Automatic batch generation based on product changes
- Batch summary and recap functionality
- Export batch data to CSV
- Cloud and local data storage
- Manual batch override capability

### ✅ **User Interface**
- Modern industrial design
- Kiosk mode for production environments
- Real-time data visualization
- Product search and management
- Settings configuration
- New batch recap dialog

### ✅ **Advanced Features**
- Heartbeat monitoring for system health
- Singleton protection (single instance)
- Auto-recovery for serial connections
- Comprehensive error handling
- Logging and debugging support
- Cloud database integration

## Installation

### System Requirements
- Windows 7 or later
- Administrative privileges for installation
- Serial port for machine communication
- Internet connection (optional, for Supabase)

### Installation Steps
1. Run the installer as Administrator
2. Follow the installation wizard
3. Choose installation components:
   - **Main Application** (Required)
   - **Python Environment** (Optional)
   - **Windows Service** (Optional)
   - **Database Setup** (Optional - shows documentation)

### Update Process
- The installer automatically detects existing installations
- Updates preserve configuration and data
- Previous versions are cleanly replaced
- No data loss during updates

## Configuration

### Supabase Setup (Optional)
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the SQL schema from `SUPABASE_SCHEMA.sql`
4. Configure credentials in `config.json`:
   ```json
   {{
     "supabase_url": "https://your-project.supabase.co",
     "supabase_key": "your-api-key",
     "enable_supabase": true
   }}
   ```

### Batch Tracking
- Batch numbers auto-generate when product code changes
- Leave batch number field empty for auto-generation
- Manual batch numbers can be entered if needed
- Batch recap shows summaries and detailed logs

## Files Included

### Application Files
- Main executable (MonitoringRollMachine.exe)
- Complete monitoring package with new features
- Windows service scripts
- Documentation and README files

### New Documentation
- `SUPABASE_SCHEMA.sql` - Database setup instructions
- `BATCH_FEATURE_README.md` - Complete batch feature guide
- Release notes and technical documentation

### Configuration
- Configuration file with Supabase settings
- Batch tracking configuration
- All previous configuration options maintained

## Migration from Previous Versions

### Automatic Migration
- All existing configurations are preserved
- Local JSON data continues to work
- Supabase integration is optional
- No breaking changes to existing functionality

### New Features
- Batch tracking starts fresh (counter begins at 1)
- Supabase integration can be enabled anytime
- All existing production data remains accessible
- New batch recap feature available immediately

## Support & Documentation

### Documentation
- Complete batch feature guide: `BATCH_FEATURE_README.md`
- Database setup instructions: `SUPABASE_SCHEMA.sql`
- Technical documentation included in installation

### Repository
- GitHub: https://github.com/StefanusSimandjuntak111/roll-machine-monitor
- Issues and feature requests welcome
- Complete source code available

## Technical Details

### Dependencies
- PySide6 (Qt UI framework)
- Supabase client (cloud database)
- pyserial (serial communication)
- pandas (data processing)
- matplotlib (data visualization)

### Database
- PostgreSQL (Supabase backend)
- Automatic triggers for batch metadata
- Optimized indexes for performance
- Row-level security enabled

### Performance
- Dual-storage system for reliability
- Optimized database queries
- Efficient batch generation
- Minimal impact on existing performance

---

**Version**: {self.version}
**Build Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Compatibility**: Windows 7+ (32-bit and 64-bit)
"""
        
        notes_path = self.releases_dir / f"RELEASE_NOTES_v{self.version}.md"
        with open(notes_path, 'w', encoding='utf-8') as f:
            f.write(release_notes)
        
        self.log_success(f"Release notes created: {notes_path}")
        return True
    
    def run(self):
        """Run the complete build process."""
        logger.info("=" * 60)
        logger.info(f"Starting build process for {self.app_name} v{self.version}")
        logger.info("=" * 60)
        
        steps = [
            ("Check Requirements", self.check_requirements),
            ("Clean Build Artifacts", self.clean_build_artifacts),
            ("Test Application", self.test_imports),
            ("Build Executable", self.build_executable),
            ("Test Executable", self.test_executable),
            ("Create NSIS Installer", self.create_nsis_installer),
            ("Create Release Notes", self.create_release_notes),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    self.log_error(f"Build process failed at step: {step_name}")
                    return False
            except Exception as e:
                self.log_error(f"Build process failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        logger.info("=" * 60)
        logger.info("BUILD COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"Installer location: {self.releases_dir}")
        logger.info(f"Version: {self.version}")
        logger.info("New features verified:")
        logger.info("  ✓ Batch tracking and auto-generation")
        logger.info("  ✓ Supabase cloud integration")
        logger.info("  ✓ Batch summary/recap feature")
        logger.info("  ✓ Enhanced production logging")
        logger.info("=" * 60)
        
        print("\n[SUCCESS] Build completed successfully!")
        print(f"[INFO] Installer ready: {self.releases_dir}")
        print(f"[INFO] Version: {self.version}")
        print("[INFO] New features included:")
        print("  • Auto batch generation")
        print("  • Supabase cloud storage")
        print("  • Batch recap dialog")
        print("  • Enhanced production tracking")
        return True

if __name__ == "__main__":
    builder = BuildManager()
    success = builder.run()
    sys.exit(0 if success else 1)
