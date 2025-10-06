#!/usr/bin/env python3
"""
Release script for Roll Machine Monitor
Handles versioning, building, and creating release packages
"""

import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

def get_current_version():
    """Get current version from version.py."""
    try:
        import monitoring.version
        return monitoring.version.VERSION
    except ImportError:
        return "1.3.4"

def update_version(new_version):
    """Update version in version.py."""
    version_file = "monitoring/version.py"
    
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version
    content = content.replace(f'VERSION = "{get_current_version()}"', f'VERSION = "{new_version}"')
    
    # Update build date
    today = datetime.now().strftime('%Y-%m-%d')
    content = content.replace('BUILD_DATE = "2024-12-19"', f'BUILD_DATE = "{today}"')
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated version to {new_version}")

def create_release_notes(version, changes=None):
    """Create release notes."""
    if changes is None:
        changes = [
            "Bug fixes and performance improvements",
            "Enhanced installer package",
            "Updated dependencies",
            "Improved error handling"
        ]
    
    release_notes = f"""# Roll Machine Monitor v{version} - Release Notes

## Release Date
{datetime.now().strftime('%Y-%m-%d')}

## What's New

"""
    
    for change in changes:
        release_notes += f"- {change}\n"
    
    release_notes += f"""
## Installation

1. Download the installer package: `RollMachineMonitor-v{version}-Windows-Installer.zip`
2. Extract the package
3. Run `install.bat` as administrator
4. Follow the installation prompts

## Files Included

- `RollMachineMonitor-v{version}.exe` - Main application executable
- `install.bat` - Automatic installer script
- `uninstall.bat` - Uninstaller script
- `INSTALLER_README.md` - Installation instructions
- Additional scripts and utilities

## System Requirements

- Windows 7/8/10/11 (64-bit)
- .NET Framework 4.5 or later
- Administrator privileges for installation

## Support

For support and updates, visit:
https://github.com/StefanusSimandjuntak111/roll-machine-monitor

## Previous Versions

- v1.3.3 - Previous stable release
- v1.3.2 - Bug fixes and improvements
- v1.3.1 - Initial release with core features
"""
    
    return release_notes

def create_release_package(version):
    """Create complete release package."""
    print(f"📦 Creating release package for v{version}...")
    
    # Create releases directory if it doesn't exist
    releases_dir = "releases"
    os.makedirs(releases_dir, exist_ok=True)
    
    # Create version-specific release directory
    release_dir = f"{releases_dir}/v{version}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copy installer files
    installer_dir = f"RollMachineMonitor-v{version}-Windows-Installer"
    if os.path.exists(installer_dir):
        shutil.copytree(installer_dir, f"{release_dir}/installer")
        print(f"   Copied installer to {release_dir}/installer/")
    
    # Copy executable
    exe_name = f"RollMachineMonitor-v{version}.exe"
    exe_path = f"dist/{exe_name}"
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, release_dir)
        print(f"   Copied executable to {release_dir}/")
    
    # Create release notes
    release_notes = create_release_notes(version)
    with open(f"{release_dir}/RELEASE_NOTES_v{version}.md", 'w', encoding='utf-8') as f:
        f.write(release_notes)
    print(f"   Created release notes: {release_dir}/RELEASE_NOTES_v{version}.md")
    
    # Create checksum file
    checksum_content = f"""# Checksums for Roll Machine Monitor v{version}

## Files

"""
    
    for file in os.listdir(release_dir):
        if file.endswith('.exe') or file.endswith('.zip'):
            file_path = os.path.join(release_dir, file)
            if os.path.isfile(file_path):
                # Calculate file size
                size = os.path.getsize(file_path)
                checksum_content += f"- {file}: {size:,} bytes\n"
    
    with open(f"{release_dir}/CHECKSUMS_v{version}.txt", 'w', encoding='utf-8') as f:
        f.write(checksum_content)
    print(f"   Created checksums: {release_dir}/CHECKSUMS_v{version}.txt")
    
    # Create ZIP of release
    release_zip = f"{releases_dir}/RollMachineMonitor-v{version}-Release.zip"
    shutil.make_archive(f"{releases_dir}/RollMachineMonitor-v{version}-Release", 'zip', '.', release_dir)
    print(f"   Created release ZIP: {release_zip}")
    
    return release_dir

def commit_and_tag(version):
    """Commit changes and create git tag."""
    print(f"📝 Committing changes for v{version}...")
    
    try:
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit
        commit_message = f"release: Roll Machine Monitor v{version}\n\n- Updated version to {version}\n- Built installer package\n- Created release notes\n- Added automatic installation scripts"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("   ✅ Changes committed")
        
        # Create tag
        tag_message = f"Roll Machine Monitor v{version}\n\nRelease {version} with installer package and improvements"
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", tag_message], check=True)
        print(f"   ✅ Tag v{version} created")
        
        # Push changes and tag
        subprocess.run(["git", "push"], check=True)
        subprocess.run(["git", "push", "--tags"], check=True)
        print("   ✅ Changes and tags pushed to remote")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git operation failed: {e}")
        return False

def main():
    """Main release process."""
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Ask for new version
    print("\nEnter new version (or press Enter to use current):")
    new_version = input().strip()
    
    if not new_version:
        new_version = current_version
    
    print(f"\n🚀 Creating release v{new_version}")
    print("=" * 50)
    
    # Update version
    if new_version != current_version:
        update_version(new_version)
    
    # Build installer
    print("\n🔨 Building installer...")
    subprocess.run([sys.executable, "build_installer.py"], check=True)
    
    # Create release package
    release_dir = create_release_package(new_version)
    
    # Commit and tag
    if commit_and_tag(new_version):
        print(f"\n🎉 Release v{new_version} created successfully!")
        print(f"📁 Release files: {release_dir}/")
        print(f"📦 Installer: RollMachineMonitor-v{new_version}-Windows-Installer.zip")
        print("\nNext steps:")
        print("1. Test the installer on a clean system")
        print("2. Upload release files to GitHub releases")
        print("3. Update documentation if needed")
    else:
        print(f"\n⚠️  Release v{new_version} created but git operations failed")
        print("Please manually commit and push the changes")

if __name__ == "__main__":
    main() 