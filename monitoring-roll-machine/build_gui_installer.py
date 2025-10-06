#!/usr/bin/env python3
"""
GUI Windows Installer for Roll Machine Monitor v1.3.4
Creates a professional GUI installer using Inno Setup
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
RELEASES_DIR = "releases"

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

def check_inno_setup():
    """Check if Inno Setup is installed."""
    print("🔍 Checking for Inno Setup...")
    
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
    print("   Please install Inno Setup from: https://jrsoftware.org/isinfo.php")
    return None

def create_license_file():
    """Create license file for installer."""
    print("📄 Creating license file...")
    
    license_content = """MIT License

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
"""
    
    with open("LICENSE.txt", 'w', encoding='utf-8') as f:
        f.write(license_content)
    
    print("   ✅ Created LICENSE.txt")

def create_inno_setup_script():
    """Create Inno Setup script for GUI installer."""
    print("📝 Creating Inno Setup script...")
    
    # Create the Inno Setup script with proper GUID format
    inno_script = f"""[Setup]
AppId={{8F4E5A2B-1C3D-4E6F-9A8B-7C2D3E4F5A6B}}
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
OutputDir=releases
OutputBaseFilename={APP_NAME}-v{VERSION}-Windows-GUI-Installer
SetupIconFile=monitoring\\ui\\main_window.py
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

[Files]
Source: "dist\\{APP_NAME}-v{VERSION}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "monitoring\\config.json"; DestDir: "{{app}}\\monitoring"; Flags: ignoreversion
Source: "scripts\\*.bat"; DestDir: "{{app}}\\scripts"; Flags: ignoreversion
Source: "scripts\\*.ps1"; DestDir: "{{app}}\\scripts"; Flags: ignoreversion
Source: "windows\\*.bat"; DestDir: "{{app}}\\windows"; Flags: ignoreversion
Source: "tools\\*.py"; DestDir: "{{app}}\\tools"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"
Name: "{{group}}\\Uninstall {APP_NAME}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Tasks: quicklaunchicon

[Registry]
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{{app}}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "Version"; ValueData: "{VERSION}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\\{APP_NAME}"; ValueType: string; ValueName: "InstallDate"; ValueData: "{datetime.now().strftime('%Y-%m-%d')}"; Flags: uninsdeletekey

[Run]
Filename: "{{app}}\\{APP_NAME}-v{VERSION}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeWizard(): Boolean;
begin
  Result := True;
end;
"""
    
    with open("installer.iss", 'w', encoding='utf-8') as f:
        f.write(inno_script)
    
    print("   ✅ Created installer.iss")

def build_installer(inno_path):
    """Build the installer using Inno Setup."""
    print("🔨 Building GUI installer...")
    
    try:
        cmd = [inno_path, "installer.iss"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ GUI installer built successfully!")
            return True
        else:
            print(f"   ❌ Build failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Build error: {e}")
        return False

def create_releases_structure():
    """Create releases directory structure."""
    print("📁 Creating releases directory structure...")
    
    # Create releases directory if it doesn't exist
    if not os.path.exists(RELEASES_DIR):
        os.makedirs(RELEASES_DIR)
        print(f"   Created {RELEASES_DIR}/")
    
    # Create windows subdirectory
    windows_dir = os.path.join(RELEASES_DIR, "windows")
    if not os.path.exists(windows_dir):
        os.makedirs(windows_dir)
        print(f"   Created {windows_dir}/")

def copy_installer_to_releases():
    """Copy the installer to releases directory."""
    print("📁 Copying installer to releases directory...")
    
    installer_name = f"{APP_NAME}-v{VERSION}-Windows-GUI-Installer.exe"
    source_path = os.path.join("releases", installer_name)
    dest_path = os.path.join(RELEASES_DIR, "windows", installer_name)
    
    if os.path.exists(source_path):
        shutil.copy2(source_path, dest_path)
        print(f"   ✅ Copied installer to: {dest_path}")
        
        # Also copy to root releases directory
        root_dest_path = os.path.join(RELEASES_DIR, installer_name)
        shutil.copy2(source_path, root_dest_path)
        print(f"   ✅ Copied installer to: {root_dest_path}")
        
        return True
    else:
        print(f"   ❌ Installer not found: {source_path}")
        return False

def cleanup():
    """Clean up temporary files."""
    print("🧹 Cleaning up temporary files...")
    
    temp_files = [
        "installer.iss",
        "LICENSE.txt"
    ]
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   Removed {file_path}")

def main():
    """Main installer creation process."""
    print(f"🚀 Creating GUI Windows Installer for {APP_NAME} v{VERSION}")
    print("=" * 60)
    
    # Check Inno Setup
    inno_path = check_inno_setup()
    if not inno_path:
        print("\n❌ Inno Setup not found! Please install it first.")
        sys.exit(1)
    
    # Create releases structure
    create_releases_structure()
    
    # Build process
    clean_build_dirs()
    
    if build_executable():
        create_license_file()
        create_inno_setup_script()
        
        if build_installer(inno_path):
            if copy_installer_to_releases():
                cleanup()
                
                print("\n" + "=" * 60)
                print("🎉 GUI Windows Installer created successfully!")
                print(f"📁 Releases directory: {RELEASES_DIR}/")
                print(f"📁 Windows directory: {RELEASES_DIR}/windows/")
                print(f"📦 Installer: {APP_NAME}-v{VERSION}-Windows-GUI-Installer.exe")
                print("\nFeatures:")
                print("✅ Professional GUI installer")
                print("✅ Multi-language support (English & Indonesian)")
                print("✅ Modern wizard interface")
                print("✅ Desktop and Start Menu shortcuts")
                print("✅ Registry integration")
                print("✅ Programs and Features integration")
                print("✅ Automatic update detection")
                print("✅ Admin privileges handling")
                print("\nNext steps:")
                print("1. Test the installer on a clean system")
                print("2. Distribute the installer to clients")
                print("3. Upload to GitHub releases")
            else:
                print("\n❌ Failed to copy installer to releases directory!")
        else:
            print("\n❌ GUI installer build failed!")
    else:
        print("\n❌ Executable build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 