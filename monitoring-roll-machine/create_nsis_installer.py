#!/usr/bin/env python3
"""
Create Windows Installer for Roll Machine Monitor v1.3.4 using NSIS
Alternative installer creation method
"""

import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Configuration
APP_NAME = "RollMachineMonitor"
VERSION = "1.3.4"
BUILD_DIR = "build"
DIST_DIR = "dist"
INSTALLER_NAME = f"{APP_NAME}-v{VERSION}-Setup.exe"

def clean_build_dirs():
    """Clean build and dist directories."""
    print("🧹 Cleaning build directories...")
    for dir_name in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

def build_executable():
    """Build executable using PyInstaller."""
    print("🔨 Building executable...")
    
    try:
        # Run PyInstaller directly
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", f"{APP_NAME}-v{VERSION}",
            "--distpath", DIST_DIR,
            "--workpath", BUILD_DIR,
            "--specpath", BUILD_DIR,
            "run_app.py"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Executable built successfully!")
            return True
        else:
            print(f"   ❌ Build failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Build error: {e}")
        return False

def create_nsis_script():
    """Create NSIS script for installer."""
    print("📝 Creating NSIS script...")
    
    nsis_script = f'''!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{VERSION}"
!define APP_PUBLISHER "Textilindo Team"
!define APP_URL "https://github.com/StefanusSimandjuntak111/roll-machine-monitor"
!define APP_EXE "{APP_NAME}-v{VERSION}.exe"

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

Name "${{APP_NAME}}"
OutFile "installer\\{INSTALLER_NAME}"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKLM "Software\\${{APP_NAME}}" "Install_Dir"

RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "monitoring\\ui\\assets\\icon.ico"
!define MUI_UNICON "monitoring\\ui\\assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Indonesian"

Section "Main Application" SecMain
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    File "{DIST_DIR}\\${{APP_EXE}}"
    File "README.md"
    File "requirements.txt"
    
    SetOutPath "$INSTDIR\\scripts"
    File /r "scripts\\*.bat"
    File /r "scripts\\*.ps1"
    
    SetOutPath "$INSTDIR\\windows"
    File /r "windows\\*.bat"
    
    SetOutPath "$INSTDIR\\tools"
    File /r "tools\\*.py"
    
    SetOutPath "$INSTDIR\\monitoring"
    File "monitoring\\config.json"
    
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "Version" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\${{APP_NAME}}" "InstallDate" "${{__DATE__}}"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
        CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
        CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END
    
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" '"$INSTDIR\\uninstall.exe"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\${{APP_EXE}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoRepair" 1
    
    # Create update checker
    FileOpen $0 "$INSTDIR\\check-updates.bat" w
    FileWrite $0 '@echo off$\r$\n'
    FileWrite $0 'echo Checking for updates...$\r$\n'
    FileWrite $0 'powershell -Command "try { $response = Invoke-RestMethod -Uri ''https://api.github.com/repos/StefanusSimandjuntak111/roll-machine-monitor/releases/latest'' -Method Get; $latest = $response.tag_name.TrimStart(''v''); if ($latest -ne ''{VERSION}'') { Write-Host ''Update available: '' + $latest; exit 1 } else { Write-Host ''No updates available''; exit 0 } } catch { Write-Host ''Error checking for updates''; exit 1 }"$\r$\n'
    FileClose $0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
        CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
        CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
SectionEnd

Section "Auto Start" SecAutoStart
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${{APP_NAME}}" "$INSTDIR\\${{APP_EXE}}"
SectionEnd

Section "Uninstall"
    !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\check-updates.bat"
    Delete "$INSTDIR\\uninstall.exe"
    
    RMDir /r "$INSTDIR\\scripts"
    RMDir /r "$INSTDIR\\windows"
    RMDir /r "$INSTDIR\\tools"
    RMDir /r "$INSTDIR\\monitoring"
    
    Delete "$SMPROGRAMS\\$MUI_TEMP\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\$MUI_TEMP\\Uninstall.lnk"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    RMDir "$SMPROGRAMS\\$MUI_TEMP"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\${{APP_NAME}}"
    DeleteRegValue HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${{APP_NAME}}"
    
    RMDir "$INSTDIR"
SectionEnd

Function .onInit
    # Check if already installed
    ReadRegStr $R0 HKLM "Software\\${{APP_NAME}}" "Install_Dir"
    StrCmp $R0 "" done
    
    ReadRegStr $R1 HKLM "Software\\${{APP_NAME}}" "Version"
    StrCmp $R1 "${{APP_VERSION}}" 0 update
        MessageBox MB_OK|MB_ICONINFORMATION "${{APP_NAME}} v${{APP_VERSION}} is already installed. Setup will now exit."
        Abort
    update:
        MessageBox MB_YESNO|MB_ICONQUESTION "An older version of ${{APP_NAME}} is already installed. Do you want to update to v${{APP_VERSION}}?" IDYES done
        Abort
    done:
FunctionEnd

Function .onInstSuccess
    MessageBox MB_YESNO "Installation completed successfully. Would you like to run ${{APP_NAME}} now?" IDNO NoRun
        Exec "$INSTDIR\\${{APP_EXE}}"
    NoRun:
FunctionEnd
'''
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print("   Created installer.nsi")

def create_license_file():
    """Create license file for installer."""
    print("📄 Creating license file...")
    
    license_content = f'''Roll Machine Monitor v{VERSION}

Copyright (c) 2024 Textilindo Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

For more information, visit:
https://github.com/StefanusSimandjuntak111/roll-machine-monitor
'''
    
    with open('LICENSE.txt', 'w', encoding='utf-8') as f:
        f.write(license_content)
    
    print("   Created LICENSE.txt")

def check_nsis():
    """Check if NSIS is installed."""
    print("🔍 Checking NSIS installation...")
    
    # Common NSIS installation paths
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\NSIS\makensis.exe"
    ]
    
    for path in nsis_paths:
        if os.path.exists(path):
            print(f"   ✅ Found NSIS: {path}")
            return path
    
    print("   ❌ NSIS not found!")
    print("   Please download and install NSIS from:")
    print("   https://nsis.sourceforge.io/Download")
    return None

def build_installer(nsis_path):
    """Build installer using NSIS."""
    print("🔨 Building installer...")
    
    try:
        # Create installer directory
        os.makedirs("installer", exist_ok=True)
        
        # Run NSIS Compiler
        cmd = [nsis_path, "installer.nsi"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Installer built successfully!")
            return True
        else:
            print(f"   ❌ Installer build failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Installer build error: {e}")
        return False

def create_update_installer():
    """Create update installer script."""
    print("📝 Creating update installer...")
    
    update_script = f'''@echo off
echo Roll Machine Monitor - Update Installer v{VERSION}
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator...
) else (
    echo Please run this script as administrator
    pause
    exit /b 1
)

REM Check if application is installed
reg query "HKLM\\SOFTWARE\\{APP_NAME}" >nul 2>&1
if %errorLevel% == 0 (
    echo Found existing installation.
    for /f "tokens=3" %%i in ('reg query "HKLM\\SOFTWARE\\{APP_NAME}" /v "Version" 2^>nul ^| find "Version"') do set CURRENT_VERSION=%%i
    echo Current version: %CURRENT_VERSION%
    
    if "%CURRENT_VERSION%"=="{VERSION}" (
        echo Already running the latest version.
        pause
        exit /b 0
    )
    
    echo Updating to version {VERSION}...
    
    REM Create backup
    if exist "%ProgramFiles%\\{APP_NAME}" (
        echo Creating backup...
        if not exist "%ProgramFiles%\\{APP_NAME}\\backup" mkdir "%ProgramFiles%\\{APP_NAME}\\backup"
        copy "%ProgramFiles%\\{APP_NAME}\\{APP_NAME}-v%CURRENT_VERSION%.exe" "%ProgramFiles%\\{APP_NAME}\\backup\\{APP_NAME}-v%CURRENT_VERSION%.exe.backup" >nul
    )
) else (
    echo No existing installation found. Installing fresh copy...
)

REM Run the installer
echo Running installer...
start /wait "" "{INSTALLER_NAME}"

echo.
echo Update completed successfully!
echo.
pause
'''
    
    with open('update-installer.bat', 'w', encoding='utf-8') as f:
        f.write(update_script)
    
    print("   Created update-installer.bat")

def create_distribution_package():
    """Create distribution package with installer and documentation."""
    print("📦 Creating distribution package...")
    
    # Create distribution directory
    dist_dir = f"{APP_NAME}-v{VERSION}-NSIS-Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy installer
    installer_path = f"installer/{INSTALLER_NAME}"
    if os.path.exists(installer_path):
        shutil.copy2(installer_path, dist_dir)
        print(f"   Copied installer: {INSTALLER_NAME}")
    
    # Copy update script
    if os.path.exists("update-installer.bat"):
        shutil.copy2("update-installer.bat", dist_dir)
        print("   Copied update-installer.bat")
    
    # Create README
    readme_content = f'''# Roll Machine Monitor v{VERSION} - NSIS Installer

## Installation

1. Run `{INSTALLER_NAME}` as administrator
2. Follow the installation wizard
3. The application will be installed to `%ProgramFiles%\\{APP_NAME}\\`

## Update

1. Run `update-installer.bat` as administrator
2. The script will check for existing installation and update if needed

## Features

- ✅ Professional installation wizard
- ✅ Desktop and Start Menu shortcuts
- ✅ Registry entries for system integration
- ✅ Automatic update detection
- ✅ Backup creation before updates
- ✅ Uninstall support
- ✅ Windows service support (optional)
- ✅ Multi-language support (English/Indonesian)

## System Requirements

- Windows 7/8/10/11 (64-bit)
- Administrator privileges for installation
- .NET Framework 4.5 or later

## Support

For support and updates, visit:
https://github.com/StefanusSimandjuntak111/roll-machine-monitor

## Version Information

- Version: {VERSION}
- Build Date: {datetime.now().strftime('%Y-%m-%d')}
- Architecture: Windows x64
- Installer: NSIS
'''
    
    with open(f"{dist_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   Created README.md")
    
    # Create ZIP package
    zip_name = f"{dist_dir}.zip"
    shutil.make_archive(dist_dir, 'zip', '.', dist_dir)
    print(f"   Created ZIP package: {zip_name}")
    
    return dist_dir

def main():
    """Main installer creation process."""
    print(f"🚀 Creating NSIS Windows Installer for {APP_NAME} v{VERSION}")
    print("=" * 60)
    
    # Check NSIS
    nsis_path = check_nsis()
    if not nsis_path:
        print("\n❌ NSIS is required to create the installer!")
        print("Please install NSIS and try again.")
        sys.exit(1)
    
    # Build process
    clean_build_dirs()
    
    if build_executable():
        create_nsis_script()
        create_license_file()
        
        if build_installer(nsis_path):
            create_update_installer()
            dist_dir = create_distribution_package()
            
            print("\n" + "=" * 60)
            print("🎉 NSIS Installer created successfully!")
            print(f"📁 Distribution directory: {dist_dir}/")
            print(f"📦 Installer: installer/{INSTALLER_NAME}")
            print(f"📦 ZIP package: {dist_dir}.zip")
            print("\nNext steps:")
            print("1. Test the installer on a clean system")
            print("2. Test the update functionality")
            print("3. Distribute the installer to clients")
            print("4. Upload to GitHub releases")
        else:
            print("\n❌ Installer build failed!")
            sys.exit(1)
    else:
        print("\n❌ Executable build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 