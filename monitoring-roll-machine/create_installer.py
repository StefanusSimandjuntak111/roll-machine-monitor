#!/usr/bin/env python3
"""
Create Windows Installer for Roll Machine Monitor v1.3.4
Creates a proper .exe installer using Inno Setup
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

def create_inno_setup_script():
    """Create Inno Setup script for installer."""
    print("📝 Creating Inno Setup script...")
    
    inno_script = f'''[Setup]
AppId={{8F4E8C2A-1B3D-4E5F-9A7B-2C8D9E0F1A2B}}
AppName={APP_NAME}
AppVersion={VERSION}
AppVerName={APP_NAME} v{VERSION}
AppPublisher=Textilindo Team
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppSupportURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppUpdatesURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
DefaultDirName={{autopf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename={INSTALLER_NAME}
SetupIconFile=monitoring\\ui\\assets\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "indonesian"; MessagesFile: "compiler:Languages\\Indonesian.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupicon"; Description: "Start automatically when Windows starts"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
Source: "{DIST_DIR}\\{APP_NAME}-v{VERSION}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "scripts\\*.bat"; DestDir: "{{app}}\\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "scripts\\*.ps1"; DestDir: "{{app}}\\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "windows\\*.bat"; DestDir: "{{app}}\\windows"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tools\\*.py"; DestDir: "{{app}}\\tools"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "monitoring\\config.json"; DestDir: "{{app}}\\monitoring"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"
Name: "{{group}}\\Uninstall {APP_NAME}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Tasks: quicklaunchicon

[Registry]
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "{APP_NAME}"; ValueData: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Flags: uninsdeletevalue; Tasks: startupicon
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{{app}}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "Version"; ValueData: "{VERSION}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "InstallDate"; ValueData: "{{date}}"; Flags: uninsdeletekey

[Run]
Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  UpdatePage: TOutputMsgWizardPage;
  UpdateAvailable: Boolean;
  CurrentVersion: String;
  LatestVersion: String;

function InitializeSetup(): Boolean;
begin
  // Check if application is already installed
  if RegKeyExists(HKLM, 'SOFTWARE\\{APP_NAME}') then
  begin
    RegQueryStringValue(HKLM, 'SOFTWARE\\{APP_NAME}', 'Version', CurrentVersion);
    if CurrentVersion = '{VERSION}' then
    begin
      MsgBox('{APP_NAME} v{VERSION} is already installed.' + #13#10 + 'Setup will now exit.', mbInformation, MB_OK);
      Result := False;
      exit;
    end
    else
    begin
      UpdateAvailable := True;
      LatestVersion := '{VERSION}';
    end;
  end;
  
  Result := True;
end;

procedure InitializeWizard();
begin
  if UpdateAvailable then
  begin
    UpdatePage := CreateOutputMsgPage(wpWelcome,
      'Update Available', 'A newer version is available.',
      'Current version: ' + CurrentVersion + #13#10 +
      'New version: ' + LatestVersion + #13#10#13#10 +
      'Click Next to update the application.');
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if UpdateAvailable and (CurPageID = UpdatePage.ID) then
  begin
    // Backup current installation
    if DirExists(ExpandConstant('{{app}}')) then
    begin
      CreateDir(ExpandConstant('{{app}}\\backup'));
      FileCopy(ExpandConstant('{{app}}\\{APP_NAME}-v' + CurrentVersion + '.exe'),
               ExpandConstant('{{app}}\\backup\\{APP_NAME}-v' + CurrentVersion + '.exe'), False);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create update checker
    SaveStringToFile(ExpandConstant('{{app}}\\check-updates.bat'),
      '@echo off' + #13#10 +
      'echo Checking for updates...' + #13#10 +
      'powershell -Command "try { $response = Invoke-RestMethod -Uri ''https://api.github.com/repos/StefanusSimandjuntak111/roll-machine-monitor/releases/latest'' -Method Get; $latest = $response.tag_name.TrimStart(''v''); if ($latest -ne ''{VERSION}'') { Write-Host ''Update available: '' + $latest; exit 1 } else { Write-Host ''No updates available''; exit 0 } } catch { Write-Host ''Error checking for updates''; exit 1 }"',
      False);
  end;
end;
'''
    
    with open('installer.iss', 'w', encoding='utf-8') as f:
        f.write(inno_script)
    
    print("   Created installer.iss")

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

def check_inno_setup():
    """Check if Inno Setup is installed."""
    print("🔍 Checking Inno Setup installation...")
    
    # Common Inno Setup installation paths
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    for path in inno_paths:
        if os.path.exists(path):
            print(f"   ✅ Found Inno Setup: {path}")
            return path
    
    print("   ❌ Inno Setup not found!")
    print("   Please download and install Inno Setup from:")
    print("   https://jrsoftware.org/isinfo.php")
    return None

def build_installer(inno_path):
    """Build installer using Inno Setup."""
    print("🔨 Building installer...")
    
    try:
        # Create installer directory
        os.makedirs("installer", exist_ok=True)
        
        # Run Inno Setup Compiler
        cmd = [inno_path, "installer.iss"]
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
    dist_dir = f"{APP_NAME}-v{VERSION}-Distribution"
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
    readme_content = f'''# Roll Machine Monitor v{VERSION} - Installer

## Installation

1. Run `{INSTALLER_NAME}` as administrator
2. Follow the installation wizard
3. The application will be installed to `%ProgramFiles%\\{APP_NAME}\\`

## Update

1. Run `update-installer.bat` as administrator
2. The script will check for existing installation and update if needed

## Features

- ✅ Automatic installation with wizard
- ✅ Desktop and Start Menu shortcuts
- ✅ Registry entries for system integration
- ✅ Automatic update detection
- ✅ Backup creation before updates
- ✅ Uninstall support
- ✅ Windows service support (optional)

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
    print(f"🚀 Creating Windows Installer for {APP_NAME} v{VERSION}")
    print("=" * 60)
    
    # Check Inno Setup
    inno_path = check_inno_setup()
    if not inno_path:
        print("\n❌ Inno Setup is required to create the installer!")
        print("Please install Inno Setup and try again.")
        sys.exit(1)
    
    # Build process
    clean_build_dirs()
    
    if build_executable():
        create_inno_setup_script()
        create_license_file()
        
        if build_installer(inno_path):
            create_update_installer()
            dist_dir = create_distribution_package()
            
            print("\n" + "=" * 60)
            print("🎉 Installer created successfully!")
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