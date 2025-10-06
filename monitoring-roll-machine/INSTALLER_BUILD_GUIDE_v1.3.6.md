# Installer Build Guide v1.3.6

## Overview
This guide explains how to build the Monitoring Roll Machine v1.3.6 installer with Zebra printer fix.

## Prerequisites

### Required Software
1. **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
2. **PyInstaller** - Install with: `pip install pyinstaller`
3. **NSIS (Nullsoft Scriptable Install System)** - Download from [nsis.sourceforge.io](https://nsis.sourceforge.io/)

### Required Files
Make sure these files exist before building:
- `installer_v1.3.6.nsi` - NSIS installer script
- `monitoring/version.py` - Version information
- `LICENSE.txt` - License file
- `requirements.txt` - Python dependencies

## Build Process

### Method 1: Complete Build (Recommended)
Run the complete build script that creates both executable and installer:

```bash
# Windows Command Prompt
build_all_v1.3.6.bat

# PowerShell
.\build_all_v1.3.6.ps1
```

This script will:
1. Update version information
2. Check Python environment
3. Install dependencies
4. Build executable using PyInstaller
5. Build NSIS installer
6. Show build results

### Method 2: Installer Only
If you already have the executable built:

```bash
# Windows Command Prompt
build_installer_v1.3.6.bat

# PowerShell
.\build_installer_v1.3.6.ps1
```

### Method 3: Manual Build
Build the installer manually using NSIS:

```bash
makensis /V2 installer_v1.3.6.nsi
```

## Output Files

After successful build, you'll get:
- `MonitoringRollMachine.exe` - Main application executable
- `Monitoring-Roll-Machine-v1.3.6-Setup.exe` - Windows installer
- `version_info.txt` - Build information

## Installer Features

### v1.3.6 New Features
- ✅ **Fixed Zebra ZD230 printer compatibility**
- ✅ **Enhanced printing system**
- ✅ **Improved error handling**
- ✅ **Update capability from previous versions**

### Installer Capabilities
- **Install**: Fresh installation with all components
- **Update**: Automatic update from previous versions
- **Uninstall**: Complete removal with data cleanup options
- **Service Installation**: Optional Windows service setup
- **Shortcuts**: Desktop and Start Menu shortcuts
- **Configuration**: Automatic config file setup

## Troubleshooting

### Common Issues

#### 1. NSIS Not Found
```
ERROR: NSIS (makensis) is not installed or not in PATH
```
**Solution**: Install NSIS and add it to your system PATH

#### 2. Python Not Found
```
ERROR: Python is not installed or not in PATH
```
**Solution**: Install Python 3.11+ and add it to PATH

#### 3. Executable Not Found
```
ERROR: dist\MonitoringRollMachine.exe not found
```
**Solution**: Run the complete build script first

#### 4. Missing Files
```
ERROR: LICENSE.txt not found
```
**Solution**: Ensure all required files are in the project directory

### Build Logs
Check the console output for detailed error messages. The scripts provide verbose output to help diagnose issues.

## Version Information

- **Version**: 1.3.6
- **Build Date**: 2025-09-30
- **Build Type**: Release
- **Features**: Zebra Printer Fix, Enhanced Printing, Improved Error Handling

## Distribution

The installer file `Monitoring-Roll-Machine-v1.3.6-Setup.exe` can be distributed to users. It includes:

- Complete application with all dependencies
- Automatic update capability
- Windows service installation (optional)
- User-friendly installation wizard
- Uninstaller with data cleanup options

## Testing

After building, test the installer by:
1. Running it on a clean system
2. Testing update from previous version
3. Verifying printer functionality with Zebra ZD230
4. Checking all shortcuts and services

## Support

For issues with the installer build process, check:
1. Console output for error messages
2. Required software versions
3. File permissions
4. System requirements (Windows 7+)
