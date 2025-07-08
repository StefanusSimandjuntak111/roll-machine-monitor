# Roll Machine Monitor - Complete Windows Installer System v1.3.0

This document describes the comprehensive Windows installer system that provides a seamless, all-in-one installation experience.

## 🎯 Overview

The Windows installer system provides everything needed for effortless deployment:

- **Single-click installation**: Complete setup with zero technical knowledge required
- **Offline support**: Works without internet connection
- **Professional installer**: Built with Inno Setup for Windows standards compliance
- **Automatic Python setup**: Installs Python 3.11 if not present
- **Windows service**: Auto-start functionality with proper service management
- **Kiosk mode**: Fullscreen operation with taskbar control
- **Update mechanism**: Preserves settings during updates
- **Complete uninstaller**: Clean removal with no leftover files

## 📁 System Components

### Core Files

```
monitoring-roll-machine/
├── installer-windows.iss           # Inno Setup script (main installer)
├── build-windows-complete.bat      # Build script
├── create-offline-windows-bundle.py # Offline bundle creator
└── windows/                        # Windows-specific files
    ├── setup-environment.bat       # Python environment setup
    ├── start-rollmachine.bat       # Regular launcher
    ├── start-rollmachine-kiosk.bat # Kiosk mode launcher
    ├── rollmachine-service.py      # Windows service implementation
    ├── install-service.bat         # Service installer
    ├── uninstall-service.bat       # Service remover
    └── update-rollmachine.bat      # Update mechanism
```

### Generated Files

```
releases/windows/
├── RollMachineMonitor-v1.3.0-Windows-Complete/
│   ├── RollMachineMonitor-v1.3.0-Windows-Installer.exe  # Main installer
│   ├── RollMachineMonitor-v1.3.0-Windows-Offline.zip   # Offline bundle
│   ├── INSTALLATION_GUIDE.md                           # User guide
│   ├── VERSION                                         # Version info
│   └── CHECKSUMS.txt                                   # File verification
```

## 🔧 Build Process

### Prerequisites

1. **Inno Setup 6.0+**: Download from https://jrsoftware.org/isinfo.php
2. **Python 3.9+**: For bundle creation
3. **Internet connection**: For downloading dependencies (build-time only)

### Building the Installer

#### Option 1: Automated Build (Recommended)

```batch
# Run the complete build script
build-windows-complete.bat
```

This script:
1. ✅ Creates offline dependency bundle
2. ✅ Downloads Python installer
3. ✅ Creates installer assets
4. ✅ Builds Inno Setup installer
5. ✅ Packages everything for distribution
6. ✅ Generates checksums and documentation

#### Option 2: Manual Build

```batch
# Create offline bundle
python create-offline-windows-bundle.py

# Build installer with Inno Setup
iscc installer-windows.iss
```

## 📦 Installation Types

### 1. Online Installation (Recommended)

**File**: `RollMachineMonitor-v1.3.0-Windows-Installer.exe`

- Single executable installer
- Downloads Python if needed
- Internet required during installation
- Smallest download size (~2-5 MB)

### 2. Offline Installation

**File**: `RollMachineMonitor-v1.3.0-Windows-Offline.zip`

- Complete package with all dependencies
- No internet required on target machine
- Includes Python installer
- Larger size (~200-300 MB)

## 🚀 Installation Process

### For End Users

1. **Download** the installer from releases
2. **Run as Administrator**: `RollMachineMonitor-v1.3.0-Windows-Installer.exe`
3. **Follow wizard** - select components and options
4. **Wait for completion** - typically 2-5 minutes
5. **Launch application** from Desktop shortcut

### Installation Components

| Component | Description | Required |
|-----------|-------------|----------|
| Core Application | Main monitoring software | ✅ Required |
| Python 3.11 | Python runtime (if not installed) | ⚠️ Auto-detected |
| Windows Service | Auto-start functionality | 🔧 Optional |
| Desktop Shortcuts | Desktop and Start menu icons | 🔧 Optional |
| Start Menu Entries | Start menu integration | ✅ Recommended |

### Installation Options

| Task | Description | Default |
|------|-------------|---------|
| Desktop Icon | Create desktop shortcut | ❌ Unchecked |
| Auto-start | Start with Windows | ✅ Checked |
| Firewall Exception | Add Windows Firewall rule | ✅ Checked |

## 🏃‍♂️ Runtime Features

### Launch Options

1. **Regular Mode**: `Roll Machine Monitor`
   - Normal windowed operation
   - Access to all menus and settings
   - Ideal for configuration and monitoring

2. **Kiosk Mode**: `Roll Machine Monitor (Kiosk)`
   - Fullscreen operation
   - Hidden taskbar
   - Touch-friendly interface
   - Escape key to exit

### Windows Service

The installer creates a Windows service with these features:

- **Auto-start**: Runs automatically on system boot
- **Crash recovery**: Restarts automatically on failure
- **Proper logging**: Service events logged to Windows Event Log
- **Management commands**:
  ```batch
  # Service status
  sc query RollMachineMonitor
  
  # Start service
  net start RollMachineMonitor
  
  # Stop service
  net stop RollMachineMonitor
  ```

## 📍 Installation Locations

### Program Files
```
C:\Program Files\RollMachineMonitor\
├── monitoring/          # Core application
├── windows/            # Windows-specific scripts
├── venv/              # Python virtual environment
├── logs/              # Application logs
├── exports/           # Data exports
└── assets/            # Application assets
```

### Start Menu
```
Start Menu > Programs > Roll Machine Monitor\
├── Roll Machine Monitor              # Regular launcher
├── Roll Machine Monitor (Kiosk)      # Kiosk launcher
├── Configuration                     # Config file
├── Logs Folder                      # Logs directory
├── Exports Folder                   # Exports directory
└── Uninstall Roll Machine Monitor   # Uninstaller
```

### Registry Entries
```
HKLM\SOFTWARE\RollMachineMonitor\
├── InstallPath    # Installation directory
├── Version        # Installed version
└── Installed      # Installation flag

HKLM\SOFTWARE\Classes\rollmachine\   # URL protocol for updates
```

## 🔄 Update Process

### Automatic Updates

1. **Detection**: Application checks for updates
2. **Download**: New installer downloaded automatically
3. **Backup**: Current settings backed up
4. **Installation**: New version installed over old
5. **Restore**: Settings restored automatically
6. **Cleanup**: Old files removed

### Manual Updates

```batch
# Download new installer
# Run as Administrator - it will detect existing installation
RollMachineMonitor-v1.3.1-Windows-Installer.exe
```

## 🗑️ Uninstallation

### Via Control Panel

1. **Windows Settings** > **Apps** > **Roll Machine Monitor**
2. Click **Uninstall**
3. Confirm removal

### Via Start Menu

1. **Start Menu** > **Roll Machine Monitor** > **Uninstall**
2. Follow uninstall wizard

### What Gets Removed

- ✅ All program files
- ✅ Windows service
- ✅ Registry entries
- ✅ Start menu entries
- ✅ Desktop shortcuts
- ✅ Firewall rules
- ⚠️ Logs and exports preserved (optional removal)

## 🛠️ Troubleshooting

### Common Issues

1. **"Python not found"**
   - Ensure Python component selected during installation
   - Manually install Python 3.11+ if needed

2. **"Service won't start"**
   - Check Windows Event Log for details
   - Run `install-service.bat` as Administrator

3. **"Port access denied"**
   - Run application as Administrator
   - Check Windows Firewall settings

4. **"Application won't launch"**
   - Check logs in installation directory
   - Verify virtual environment integrity

### Log Locations

- **Application logs**: `C:\Program Files\RollMachineMonitor\logs\`
- **Service logs**: Windows Event Log > Applications and Services Logs
- **Installation logs**: `%TEMP%\Setup Log YYYY-MM-DD #NNN.txt`

## 🔐 Security Features

- **Code signing**: Installer digitally signed (planned)
- **Checksum verification**: SHA256 checksums provided
- **Admin privileges**: Required only for installation
- **Firewall integration**: Automatic exception rules
- **Service isolation**: Runs under dedicated service account

## 📊 System Requirements

### Minimum Requirements

- **OS**: Windows 10 x64 or Windows 11
- **RAM**: 4 GB (2 GB minimum)
- **Storage**: 1 GB free space
- **Python**: 3.9+ (auto-installed if missing)
- **Serial Ports**: USB or built-in COM ports

### Recommended Requirements

- **OS**: Windows 11 x64
- **RAM**: 8 GB
- **Storage**: 2 GB free space
- **Python**: 3.11+ (included)
- **Display**: 1920x1080 for optimal kiosk experience

## 🏁 Conclusion

This Windows installer system provides a professional, user-friendly installation experience that meets enterprise deployment standards. Users can install and run the Roll Machine Monitor application without any technical knowledge, while administrators have full control over deployment and management.

The system is designed to be:
- **Foolproof**: Minimal user intervention required
- **Robust**: Handles various system configurations
- **Professional**: Follows Windows installation standards
- **Maintainable**: Easy updates and management
- **Secure**: Proper permissions and isolation

For technical support or advanced configuration, refer to the application documentation or contact the development team. 