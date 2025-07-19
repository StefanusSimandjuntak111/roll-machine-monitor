# Roll Machine Monitor Windows Installer

This directory contains the Inno Setup script for creating a Windows installer for the Roll Machine Monitor application.

## How to Compile the Installer

### Method 1: Using the Batch File (Recommended)
1. Simply run `compile-installer.bat` in this directory
2. The script will automatically find your Inno Setup installation and compile the installer
3. The compiled installer will be placed in `../releases/windows/`

### Method 2: Using Inno Setup Compiler Directly
1. Open `installer-windows.iss` in Inno Setup Compiler
2. Click "Compile" or press F9
3. The compiled installer will be placed in `../releases/windows/`

## Python Installation (Automatic)
- **Python 3.11** will be **downloaded and installed otomatis** jika belum ada di komputer target.
- Installer akan mendeteksi Python, jika tidak ada akan otomatis download dari python.org dan install secara silent.
- **Koneksi internet diperlukan** untuk proses ini.
- Setelah Python terinstall, installer akan melanjutkan instalasi aplikasi dan dependensi.

## Recent Fixes

The installer script has been updated to fix several issues:

1. **Path Corrections**: All file paths now use `../` to correctly reference files from the build-scripts directory
2. **Optional Files**: Added `optional` flag to files that might not exist:
   - Python installer
   - Assets directory
   - Offline bundle
3. **Icon References**: Removed icon references that might cause compilation errors
4. **DirExists Function**: Added a proper implementation of the DirExists function
5. **Python Download**: Now the installer will download Python automatically if not present.

## Installer Features

- ✅ Python installation (if needed, auto-download)
- ✅ Virtual environment creation
- ✅ All Python requirements installation
- ✅ Desktop shortcuts
- ✅ Windows service setup
- ✅ Start menu entries
- ✅ Automatic updates support
- ✅ Uninstaller
- ✅ Silent installation support
- ✅ Offline installation support (except Python download)

## Silent Installation

To perform a silent installation, run:
```
RollMachineMonitor-v1.3.0-Windows-Installer.exe /SILENT
```

Or for completely silent (no UI):
```
RollMachineMonitor-v1.3.0-Windows-Installer.exe /VERYSILENT
```

## Troubleshooting

If you encounter any issues during compilation:

1. **File Not Found Errors**: Check if the referenced file exists in the correct location
2. **Syntax Errors**: Ensure all sections and directives are properly formatted
3. **Inno Setup Version**: Make sure you're using Inno Setup 6.x (preferably 6.2+)

For more help, refer to the Inno Setup documentation: https://jrsoftware.org/ishelp/ 