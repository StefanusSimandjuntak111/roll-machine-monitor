#!/bin/bash

# ===============================================
# Roll Machine Monitor Offline Bundle Creator
# Creates offline installation package with all dependencies
# ===============================================

set -e

VERSION="1.3.0"
BUNDLE_NAME="rollmachine-monitor-${VERSION}-offline-antix"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo
    echo "================================================="
    echo -e "${BLUE}📦 Roll Machine Monitor Offline Bundle Creator${NC}"
    echo "================================================="
    echo
}

create_offline_bundle() {
    log_step "Creating offline bundle directory..."
    
    # Clean previous bundle
    rm -rf "$BUNDLE_NAME"
    mkdir -p "$BUNDLE_NAME"
    
    # Copy application files
    log_info "Copying application files..."
    cp -r monitoring "$BUNDLE_NAME/"
    cp requirements.txt "$BUNDLE_NAME/" 2>/dev/null || true
    cp run_app.py "$BUNDLE_NAME/" 2>/dev/null || true
    cp README.md "$BUNDLE_NAME/" 2>/dev/null || true
    
    # Copy installer
    cp install-complete-antix.sh "$BUNDLE_NAME/"
    
    # Create offline installer
    cat > "$BUNDLE_NAME/install-offline.sh" << 'OFFLINE_EOF'
#!/bin/bash

# Offline installer for Roll Machine Monitor
# Uses pre-downloaded Python packages

set -e

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if pip packages directory exists
if [ ! -d "$CURRENT_DIR/pip-packages" ]; then
    echo "❌ Offline packages not found!"
    echo "   Please run this installer from the bundle directory"
    exit 1
fi

# Run main installer with offline flag
export PIP_FIND_LINKS="$CURRENT_DIR/pip-packages"
export PIP_NO_INDEX=1

# Modify the main installer to use offline packages
sed 's/pip install/pip install --find-links "$PIP_FIND_LINKS" --no-index/g' install-complete-antix.sh > install-complete-antix-offline.sh
chmod +x install-complete-antix-offline.sh

echo "🚀 Starting offline installation..."
sudo ./install-complete-antix-offline.sh "$@"
OFFLINE_EOF

    chmod +x "$BUNDLE_NAME/install-offline.sh"
    
    log_step "Offline bundle structure created"
}

download_python_packages() {
    log_step "Downloading Python packages for offline installation..."
    
    cd "$BUNDLE_NAME"
    
    # Create virtual environment for downloading
    python3 -m venv temp_venv
    source temp_venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Create packages directory
    mkdir -p pip-packages
    
    # Download packages with dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Downloading from requirements.txt..."
        pip download -r requirements.txt -d pip-packages
    else
        log_info "Downloading essential packages..."
        pip download -d pip-packages \
            PySide6>=6.6.0 \
            pyqtgraph>=0.13.3 \
            pyserial>=3.5 \
            python-dotenv>=1.0.0 \
            pyyaml>=6.0.1 \
            appdirs>=1.4.4 \
            qrcode>=7.4.2 \
            Pillow>=10.0.0
    fi
    
    # Clean up temporary venv
    deactivate
    rm -rf temp_venv
    
    cd ..
    
    log_step "Python packages downloaded successfully"
}

create_readme() {
    log_step "Creating installation guide..."
    
    cat > "$BUNDLE_NAME/README-INSTALLATION.md" << 'README_EOF'
# Roll Machine Monitor v1.3.0 - Offline Installation Package

This package contains everything needed to install Roll Machine Monitor on antiX Linux without internet connection.

## 📋 What's Included

- Complete application source code
- All Python dependencies (offline)
- Automated installer for antiX Linux
- Desktop shortcuts and system integration
- SysV init scripts (no systemd required)
- Kiosk mode setup

## 🚀 Installation Instructions

### Option 1: Offline Installation (Recommended)
```bash
# Extract the package
tar -xzf rollmachine-monitor-v1.3.0-offline-antix.tar.gz
cd rollmachine-monitor-v1.3.0-offline-antix

# Run offline installer
sudo ./install-offline.sh
```

### Option 2: Online Installation
```bash
# If you have internet connection
sudo ./install-complete-antix.sh
```

### Option 3: Update Existing Installation
```bash
# To update while preserving settings
sudo ./install-complete-antix.sh --update
```

## ✅ What the Installer Does

1. **System Dependencies**: Installs all required system packages
2. **Python Environment**: Creates isolated virtual environment
3. **Application**: Installs Roll Machine Monitor application
4. **Services**: Sets up auto-start service (SysV init)
5. **Desktop Integration**: Creates desktop shortcuts
6. **Kiosk Mode**: Sets up dedicated kiosk user
7. **Watchdog**: Monitors and restarts application if needed

## 🖥️ After Installation

### Starting the Application
- **Desktop**: Click "Roll Machine Monitor" icon
- **Kiosk Mode**: Click "Roll Machine Monitor (Kiosk)" icon
- **Command Line**: `/opt/rollmachine-monitor/start-rollmachine.sh`

### Service Management
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

### Kiosk User
- **Username**: kiosk
- **Password**: kiosk123
- **Auto-starts**: Roll Machine Monitor on login

## 📁 Installation Locations

- **Application**: `/opt/rollmachine-monitor/`
- **Logs**: `/opt/rollmachine-monitor/logs/`
- **Exports**: `/opt/rollmachine-monitor/exports/`
- **Service**: `/etc/init.d/rollmachine-monitor`

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Check logs
tail -f /opt/rollmachine-monitor/logs/startup.log

# Check service status
sudo /etc/init.d/rollmachine-monitor status

# Restart service
sudo /etc/init.d/rollmachine-monitor restart
```

### Serial Port Issues
```bash
# Check if user is in dialout group
groups $USER

# Add user to dialout group (if needed)
sudo usermod -a -G dialout $USER

# List available serial ports
ls -la /dev/ttyUSB* /dev/ttyACM*
```

### Permission Issues
```bash
# Fix permissions
sudo chown -R root:root /opt/rollmachine-monitor
sudo chmod -R 755 /opt/rollmachine-monitor
sudo chmod 777 /opt/rollmachine-monitor/logs
sudo chmod 777 /opt/rollmachine-monitor/exports
```

## 📞 Support

For issues or questions:
1. Check the logs in `/opt/rollmachine-monitor/logs/`
2. Verify serial port connections
3. Ensure JSK3588 device is properly connected
4. Check application configuration in settings

## 🔄 Updates

To update the application:
```bash
# Download new version and run
sudo ./install-complete-antix.sh --update
```

This preserves your settings and data while updating the application.
README_EOF

    log_step "Installation guide created"
}

create_version_info() {
    log_step "Creating version information..."
    
    cat > "$BUNDLE_NAME/VERSION" << VERSION_EOF
Roll Machine Monitor v${VERSION}
Built: $(date '+%Y-%m-%d %H:%M:%S')
Target: antiX Linux (SysV init)
Type: Offline Installation Bundle

Features:
- Complete offline installation
- All Python dependencies included
- SysV init scripts (no systemd)
- Desktop shortcuts
- Kiosk mode with dedicated user
- Automatic watchdog monitoring
- Serial port communication (JSK3588)
- Data export capabilities
- Real-time monitoring UI

Installation:
  sudo ./install-offline.sh

Update:
  sudo ./install-complete-antix.sh --update

Support:
  Check logs in /opt/rollmachine-monitor/logs/
VERSION_EOF

    log_step "Version information created"
}

package_bundle() {
    log_step "Creating final package..."
    
    # Create compressed archive
    tar -czf "${BUNDLE_NAME}.tar.gz" "$BUNDLE_NAME"
    
    # Calculate checksums
    sha256sum "${BUNDLE_NAME}.tar.gz" > "${BUNDLE_NAME}.tar.gz.sha256"
    md5sum "${BUNDLE_NAME}.tar.gz" > "${BUNDLE_NAME}.tar.gz.md5"
    
    log_step "Package created: ${BUNDLE_NAME}.tar.gz"
}

print_completion() {
    echo
    echo "================================================="
    echo -e "${GREEN}🎉 Offline Bundle Created Successfully! 🎉${NC}"
    echo "================================================="
    echo
    echo -e "${BLUE}📦 Package:${NC} ${BUNDLE_NAME}.tar.gz"
    echo -e "${BLUE}📁 Size:${NC} $(du -h "${BUNDLE_NAME}.tar.gz" | cut -f1)"
    echo -e "${BLUE}🔍 SHA256:${NC} $(cat "${BUNDLE_NAME}.tar.gz.sha256" | cut -d' ' -f1)"
    echo
    echo -e "${BLUE}📋 Installation Instructions:${NC}"
    echo "1. Copy ${BUNDLE_NAME}.tar.gz to target antiX system"
    echo "2. Extract: tar -xzf ${BUNDLE_NAME}.tar.gz"
    echo "3. Install: cd ${BUNDLE_NAME} && sudo ./install-offline.sh"
    echo
    echo -e "${BLUE}🔄 Update Instructions:${NC}"
    echo "   sudo ./install-complete-antix.sh --update"
    echo
    echo -e "${GREEN}✅ Ready for offline deployment!${NC}"
    echo
}

# ===============================================
# MAIN PROCESS
# ===============================================

main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ] && [ ! -d "monitoring" ]; then
        echo "❌ Please run this script from the monitoring-roll-machine directory"
        exit 1
    fi
    
    # Create offline bundle
    create_offline_bundle
    download_python_packages
    create_readme
    create_version_info
    package_bundle
    
    # Show completion info
    print_completion
}

# Run main process
main "$@" 