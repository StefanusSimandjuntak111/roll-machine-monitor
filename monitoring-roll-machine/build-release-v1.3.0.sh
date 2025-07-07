#!/bin/bash

# ===============================================
# Build Complete Release v1.3.0 for antiX
# All-in-One Installer with Offline Capabilities
# ===============================================

set -e

VERSION="v1.3.0"
PACKAGE_NAME="rollmachine-monitor-${VERSION}-complete-antix"
BUILD_DIR="releases/${PACKAGE_NAME}"
CURRENT_DIR=$(pwd)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo
    echo "======================================================="
    echo -e "${BLUE}🚀 Building Complete Release ${VERSION} for antiX${NC}"
    echo "======================================================="
    echo
}

clean_previous_build() {
    if [ -d "$BUILD_DIR" ]; then
        log_info "Cleaning previous build..."
        rm -rf "$BUILD_DIR"
    fi
}

create_build_directories() {
    log_step "Creating build directories..."
    mkdir -p "$BUILD_DIR"
    mkdir -p "$BUILD_DIR/monitoring-roll-machine"
}

copy_core_files() {
    log_step "Copying core application files..."
    
    # Copy main application
    cp -r monitoring "$BUILD_DIR/monitoring-roll-machine/"
    
    # Copy essential files
    [ -f requirements.txt ] && cp requirements.txt "$BUILD_DIR/monitoring-roll-machine/"
    [ -f run_app.py ] && cp run_app.py "$BUILD_DIR/monitoring-roll-machine/"
    [ -f README.md ] && cp README.md "$BUILD_DIR/"
    
    # Create necessary directories
    mkdir -p "$BUILD_DIR/logs"
    mkdir -p "$BUILD_DIR/exports"
    mkdir -p "$BUILD_DIR/monitoring-roll-machine/logs"
    mkdir -p "$BUILD_DIR/monitoring-roll-machine/exports"
}

copy_installers() {
    log_step "Copying installer scripts..."
    
    # Copy main installer
    cp install-complete-antix.sh "$BUILD_DIR/"
    
    # Copy offline bundle creator
    cp install-offline-bundle.sh "$BUILD_DIR/"
    
    # Make executable
    chmod +x "$BUILD_DIR/install-complete-antix.sh"
    chmod +x "$BUILD_DIR/install-offline-bundle.sh"
}

create_release_notes() {
    log_step "Creating release notes..."
    
    cat > "$BUILD_DIR/RELEASE_NOTES_${VERSION}.md" << 'RELEASE_EOF'
# Roll Machine Monitor v1.3.0 Release Notes

## 🎉 Major New Features: Complete All-in-One Installer

This release focuses on providing the ultimate installation experience for antiX Linux with **everything automated in a single script**.

### ✨ New Features

#### 🔧 All-in-One Installer
- **Single Command Installation**: Everything installs with one command
- **Automatic Dependency Management**: All system and Python packages installed automatically
- **Offline Installation Support**: Can install without internet connection
- **Update Mechanism**: Preserves settings during updates

#### 🐧 Enhanced antiX Linux Support
- **SysV Init Scripts**: Full support for antiX's init system (no systemd)
- **Lightweight Dependencies**: Optimized package selection for minimal systems
- **Multi-Window Manager Support**: Works with FluxBox, IceWM, OpenBox

#### 🖥️ Desktop Integration
- **Automatic Desktop Shortcuts**: Created for all users
- **Application Menu Integration**: Shows up in system application menu
- **Kiosk Mode Shortcuts**: Separate shortcut for kiosk operation

#### 👤 Kiosk User Management
- **Dedicated Kiosk User**: Automatically created with proper permissions
- **Auto-Login Setup**: Kiosk user can auto-start the application
- **Security Configuration**: Proper isolation and permissions

#### 🔄 Service Management
- **Auto-Start Service**: Application starts automatically on boot
- **Watchdog Process**: Monitors and restarts application if it crashes
- **Cron Integration**: Uses cron for process monitoring (antiX compatible)

#### 📦 Offline Installation Package
- **Complete Bundle**: All dependencies included in package
- **No Internet Required**: Can install on completely offline systems
- **Checksums**: Package integrity verification included

### 🛠️ Installation Methods

#### Method 1: Online Installation (Recommended)
```bash
sudo ./install-complete-antix.sh
```

#### Method 2: Offline Installation
```bash
# Create offline bundle (on system with internet)
./install-offline-bundle.sh

# Transfer and install (on target system)
tar -xzf rollmachine-monitor-v1.3.0-offline-antix.tar.gz
cd rollmachine-monitor-v1.3.0-offline-antix
sudo ./install-offline.sh
```

#### Method 3: Update Existing Installation
```bash
sudo ./install-complete-antix.sh --update
```

### 📁 Installation Structure

```
/opt/rollmachine-monitor/
├── monitoring-roll-machine/     # Application files
│   ├── monitoring/              # Core application
│   ├── logs/                    # Application logs
│   └── exports/                 # Data exports
├── venv/                        # Python virtual environment
├── logs/                        # System logs
├── start-rollmachine.sh         # Regular mode startup
├── start-rollmachine-kiosk.sh   # Kiosk mode startup
└── watchdog.sh                  # Process monitoring

/etc/init.d/rollmachine-monitor  # SysV init script
/usr/share/applications/         # Desktop shortcuts
```

### 🔧 Service Management

```bash
# Start service
sudo /etc/init.d/rollmachine-monitor start

# Stop service
sudo /etc/init.d/rollmachine-monitor stop

# Check status
sudo /etc/init.d/rollmachine-monitor status

# Restart service
sudo /etc/init.d/rollmachine-monitor restart
```

### 👤 User Accounts

#### Regular Users
- Application available via desktop shortcuts
- Can run in normal window mode
- Access to configuration and settings

#### Kiosk User
- **Username**: kiosk
- **Password**: kiosk123
- **Purpose**: Dedicated kiosk mode operation
- **Auto-start**: Application launches automatically on login

### 📋 System Requirements

#### Minimum Requirements
- **OS**: antiX Linux (any version), Debian-based distributions
- **RAM**: 512MB (2GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.7+ (automatically installed)
- **Display**: Any resolution (fullscreen kiosk mode available)

#### Hardware Requirements
- **JSK3588 Roll Machine** with serial/USB interface
- **USB Serial Port** or direct serial connection

### 🔍 Verification & Testing

#### Post-Installation Checks
```bash
# Verify installation
ls -la /opt/rollmachine-monitor/

# Check service status
sudo /etc/init.d/rollmachine-monitor status

# Test application startup
/opt/rollmachine-monitor/start-rollmachine.sh

# View logs
tail -f /opt/rollmachine-monitor/logs/startup.log
```

### 🚀 What Makes This Release Special

1. **Zero Configuration**: No manual setup required
2. **Complete Automation**: From system packages to desktop shortcuts
3. **Offline Capable**: Can install without internet
4. **Update Safe**: Preserves your settings and data
5. **antiX Optimized**: Built specifically for antiX Linux
6. **Kiosk Ready**: Full kiosk mode with dedicated user
7. **Production Ready**: Service management and monitoring included

### 🛡️ Reliability Features

- **Automatic Restarts**: Watchdog monitors and restarts failed processes
- **Crash Recovery**: Service automatically recovers from failures
- **Log Rotation**: Automatic log management prevents disk filling
- **Permission Management**: Proper security and access controls

### 📖 Documentation

- Complete installation guide included
- Troubleshooting documentation
- Service management instructions
- User manual for operation

### 🔄 Upgrade Path

For existing installations:
```bash
# Backup current config (automatic)
sudo ./install-complete-antix.sh --update

# Manual backup (optional)
cp /opt/rollmachine-monitor/monitoring-roll-machine/monitoring/config.json ~/config-backup.json
```

## 🎯 Target Audience

This release is perfect for:
- **Industrial Environments**: Reliable kiosk operation
- **IT Administrators**: Easy deployment and management
- **End Users**: Simple installation and operation
- **Offline Environments**: No internet dependency after installation

## 🔧 Technical Improvements

- Enhanced error handling and logging
- Improved startup reliability
- Better resource management
- Optimized for low-resource systems
- Full SysV init compatibility

---

**Installation**: Run `sudo ./install-complete-antix.sh` for complete automated setup.

**Update**: Run `sudo ./install-complete-antix.sh --update` to update while preserving settings.

**Support**: Check logs in `/opt/rollmachine-monitor/logs/` for troubleshooting.
RELEASE_EOF

    log_step "Release notes created"
}

create_version_file() {
    log_step "Creating version file..."
    
    cat > "$BUILD_DIR/VERSION" << VERSION_EOF
${VERSION}
BUILT: $(date '+%Y-%m-%d %H:%M:%S')
TARGET: antiX Linux (SysV init)
TYPE: Complete All-in-One Release
FEATURES: Offline installation, Desktop integration, Kiosk mode, Service management
VERSION_EOF
}

create_installation_guide() {
    log_step "Creating installation guide..."
    
    cat > "$BUILD_DIR/INSTALL_GUIDE.md" << 'GUIDE_EOF'
# Roll Machine Monitor v1.3.0 - Installation Guide

## 🚀 Quick Start

### For Most Users (Online Installation)
```bash
# Extract the package
tar -xzf rollmachine-monitor-v1.3.0-complete-antix.tar.gz
cd rollmachine-monitor-v1.3.0-complete-antix

# Install everything automatically
sudo ./install-complete-antix.sh
```

That's it! The application is now installed and ready to use.

## 📋 Installation Options

### Option 1: Complete Online Installation (Recommended)
- Downloads and installs all dependencies
- Sets up services and desktop shortcuts
- Creates kiosk user and auto-start
- **Command**: `sudo ./install-complete-antix.sh`

### Option 2: Update Existing Installation
- Preserves your settings and data
- Updates application to latest version
- **Command**: `sudo ./install-complete-antix.sh --update`

### Option 3: Create Offline Installation Package
- For systems without internet connection
- Downloads all dependencies for offline installation
- **Commands**:
  ```bash
  # On system with internet - create offline package
  ./install-offline-bundle.sh
  
  # Transfer the created package to target system
  # Extract and install offline
  tar -xzf rollmachine-monitor-v1.3.0-offline-antix.tar.gz
  cd rollmachine-monitor-v1.3.0-offline-antix
  sudo ./install-offline.sh
  ```

## ✅ What Gets Installed

1. **System Dependencies**: All required Linux packages
2. **Python Environment**: Isolated virtual environment with all Python packages
3. **Application Files**: Complete Roll Machine Monitor application
4. **Service Scripts**: Auto-start service using SysV init (antiX compatible)
5. **Desktop Shortcuts**: Icons for regular and kiosk modes
6. **Kiosk User**: Dedicated user account for kiosk operation
7. **Watchdog**: Monitoring script that restarts application if it crashes

## 🖥️ After Installation

### Starting the Application

#### From Desktop
- Click "Roll Machine Monitor" icon on desktop
- Or click "Roll Machine Monitor (Kiosk)" for fullscreen mode

#### From Command Line
```bash
# Regular mode
/opt/rollmachine-monitor/start-rollmachine.sh

# Kiosk mode
/opt/rollmachine-monitor/start-rollmachine-kiosk.sh
```

#### As System Service
```bash
# Start the service
sudo /etc/init.d/rollmachine-monitor start

# Check if it's running
sudo /etc/init.d/rollmachine-monitor status

# Stop the service
sudo /etc/init.d/rollmachine-monitor stop

# Restart the service
sudo /etc/init.d/rollmachine-monitor restart
```

### Kiosk Mode

A dedicated `kiosk` user is created for kiosk operation:
- **Username**: kiosk
- **Password**: kiosk123
- **Auto-start**: Application automatically starts when kiosk user logs in

To use kiosk mode:
1. Log out of current user
2. Log in as `kiosk` user
3. Application starts automatically in fullscreen mode

## 📁 Installation Locations

- **Main Application**: `/opt/rollmachine-monitor/`
- **Application Code**: `/opt/rollmachine-monitor/monitoring-roll-machine/`
- **Virtual Environment**: `/opt/rollmachine-monitor/venv/`
- **Logs**: `/opt/rollmachine-monitor/logs/`
- **Exports**: `/opt/rollmachine-monitor/exports/`
- **Service Script**: `/etc/init.d/rollmachine-monitor`
- **Desktop Shortcuts**: `/usr/share/applications/` and user desktops

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Check the logs
tail -f /opt/rollmachine-monitor/logs/startup.log
tail -f /opt/rollmachine-monitor/logs/kiosk.log

# Check service status
sudo /etc/init.d/rollmachine-monitor status

# Try restarting
sudo /etc/init.d/rollmachine-monitor restart
```

### Serial Port Issues
```bash
# List available serial ports
ls -la /dev/ttyUSB* /dev/ttyACM*

# Check if user is in dialout group
groups $USER

# Add user to dialout group (logout/login required)
sudo usermod -a -G dialout $USER
```

### Permission Issues
```bash
# Reset permissions
sudo chown -R root:root /opt/rollmachine-monitor
sudo chmod -R 755 /opt/rollmachine-monitor
sudo chmod 777 /opt/rollmachine-monitor/logs
sudo chmod 777 /opt/rollmachine-monitor/exports
```

### Desktop Shortcuts Missing
```bash
# Recreate desktop shortcuts
sudo cp /usr/share/applications/rollmachine-monitor*.desktop ~/Desktop/
chmod +x ~/Desktop/rollmachine-monitor*.desktop
```

## 🔄 Updates

To update while preserving your settings:
```bash
# Download new version
# Extract new package
# Run update command
sudo ./install-complete-antix.sh --update
```

Your configuration and exported data will be automatically backed up and restored.

## 📞 Support

### Log Files
- **Startup**: `/opt/rollmachine-monitor/logs/startup.log`
- **Kiosk Mode**: `/opt/rollmachine-monitor/logs/kiosk.log`
- **Watchdog**: `/opt/rollmachine-monitor/logs/watchdog.log`

### Common Issues
1. **Application won't start**: Check logs and service status
2. **Serial port not detected**: Verify connection and user permissions
3. **Kiosk mode not working**: Check display settings and user login
4. **Service not starting**: Verify init script installation

### Getting Help
1. Check the logs first
2. Verify JSK3588 device connection
3. Ensure proper serial port configuration
4. Test with different users (regular vs kiosk)

## 🏁 Quick Verification

After installation, verify everything works:

1. **Check installation**: `ls -la /opt/rollmachine-monitor/`
2. **Check service**: `sudo /etc/init.d/rollmachine-monitor status`
3. **Test application**: `/opt/rollmachine-monitor/start-rollmachine.sh`
4. **Check desktop shortcuts**: Look for icons on desktop
5. **Verify kiosk user**: `su - kiosk` (password: kiosk123)

If all these work, your installation is successful!
GUIDE_EOF

    log_step "Installation guide created"
}

create_checksums() {
    log_step "Creating package checksums..."
    
    cd releases
    
    # Create compressed package
    tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
    
    # Generate checksums
    sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"
    md5sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.md5"
    
    cd ..
    
    log_step "Package and checksums created"
}

print_build_summary() {
    echo
    echo "======================================================="
    echo -e "${GREEN}🎉 Build Completed Successfully! 🎉${NC}"
    echo "======================================================="
    echo
    echo -e "${BLUE}📦 Package:${NC} releases/${PACKAGE_NAME}.tar.gz"
    echo -e "${BLUE}📁 Size:${NC} $(du -h "releases/${PACKAGE_NAME}.tar.gz" 2>/dev/null | cut -f1 || echo "Unknown")"
    echo -e "${BLUE}🔍 SHA256:${NC} $(cat "releases/${PACKAGE_NAME}.tar.gz.sha256" 2>/dev/null | cut -d' ' -f1 || echo "Not generated")"
    echo
    echo -e "${BLUE}📋 Package Contents:${NC}"
    echo "   ✅ Complete application source code"
    echo "   ✅ All-in-one installer script"
    echo "   ✅ Offline bundle creator"
    echo "   ✅ Desktop shortcuts and integration"
    echo "   ✅ SysV init scripts for antiX"
    echo "   ✅ Kiosk user setup"
    echo "   ✅ Service management and watchdog"
    echo "   ✅ Comprehensive documentation"
    echo
    echo -e "${BLUE}🚀 Installation Instructions:${NC}"
    echo "   1. Transfer package to target antiX system"
    echo "   2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
    echo "   3. Install: cd ${PACKAGE_NAME} && sudo ./install-complete-antix.sh"
    echo
    echo -e "${BLUE}🔄 Update Instructions:${NC}"
    echo "   sudo ./install-complete-antix.sh --update"
    echo
    echo -e "${BLUE}📦 Offline Installation:${NC}"
    echo "   1. Create offline bundle: ./install-offline-bundle.sh"
    echo "   2. Transfer bundle to target system"
    echo "   3. Extract and run: sudo ./install-offline.sh"
    echo
    echo -e "${GREEN}✅ Ready for deployment to antiX systems!${NC}"
    echo
}

# ===============================================
# MAIN BUILD PROCESS
# ===============================================

main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -d "monitoring" ] || [ ! -f "install-complete-antix.sh" ]; then
        echo -e "${RED}❌ Error: Please run this script from the monitoring-roll-machine directory${NC}"
        echo "   Make sure install-complete-antix.sh exists"
        exit 1
    fi
    
    # Build process
    clean_previous_build
    create_build_directories
    copy_core_files
    copy_installers
    create_release_notes
    create_version_file
    create_installation_guide
    create_checksums
    
    # Show summary
    print_build_summary
}

# Run the build
main "$@" 