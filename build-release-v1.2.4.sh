#!/bin/bash

# =============================================================================
# Roll Machine Monitor v1.2.4 - Release Builder for antiX
# =============================================================================
# Script to create versioned release package for antiX deployment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[RELEASE]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
VERSION="1.2.4"
RELEASE_NAME="rollmachine-monitor-v${VERSION}"
PACKAGE_NAME="${RELEASE_NAME}-antix"
OUTPUT_DIR="releases"
TEMP_DIR="/tmp/rollmachine-build-$$"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create temporary build directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

log "Building Roll Machine Monitor v${VERSION} for antiX deployment"

# Create package directory
mkdir -p "$PACKAGE_NAME"

# Copy main application
log "Copying main application..."
cp -r "$(dirname "$0")/monitoring-roll-machine" "$PACKAGE_NAME/"

# Copy antiX specific scripts
log "Copying antiX deployment scripts..."
cp "$(dirname "$0")/antix-init.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/antix-kiosk-setup.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/antix-startup.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/antix-watchdog.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/kiosk-startup.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/rollmachine-init.sh" "$PACKAGE_NAME/" 2>/dev/null || true

# Copy service files
log "Copying service configuration files..."
cp "$(dirname "$0")/rollmachine-kiosk.service" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/rollmachine-smart.service" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/rollmachine-watchdog.service" "$PACKAGE_NAME/" 2>/dev/null || true

# Copy watchdog scripts
log "Copying watchdog and management scripts..."
cp "$(dirname "$0")/smart-watchdog.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/smart-watchdog-sysv.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/watchdog.sh" "$PACKAGE_NAME/" 2>/dev/null || true

# Copy installation scripts
log "Copying installation scripts..."
cp "$(dirname "$0")/install-rollmachine.sh" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/fix-multiple-instance-offline.sh" "$PACKAGE_NAME/" 2>/dev/null || true

# Copy configuration files
log "Copying configuration files..."
cp "$(dirname "$0")/config.json" "$PACKAGE_NAME/" 2>/dev/null || true

# Copy documentation
log "Copying documentation..."
cp "$(dirname "$0")/README.md" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/DEPLOYMENT_SUMMARY_v1.2.4.md" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/RELEASE_NOTES_v1.2.4.md" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/CLIENT_UPDATE_GUIDE.md" "$PACKAGE_NAME/" 2>/dev/null || true
cp "$(dirname "$0")/LICENSE" "$PACKAGE_NAME/" 2>/dev/null || true

# Create installation script for antiX
log "Creating antiX installation script..."
cat > "$PACKAGE_NAME/install-antix.sh" << 'EOF'
#!/bin/bash
# Roll Machine Monitor v1.2.4 - antiX Installation Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INSTALL]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
   exit 1
fi

log "Installing Roll Machine Monitor v1.2.4 on antiX..."

# Install system dependencies
info "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv python3-tk python3-serial git

# Create application directory
INSTALL_DIR="/opt/rollmachine-monitor"
log "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy application files
log "Copying application files..."
cp -r monitoring-roll-machine/* "$INSTALL_DIR/"

# Create virtual environment
log "Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
log "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy configuration files
log "Setting up configuration..."
cp ../config.json "$INSTALL_DIR/" 2>/dev/null || true

# Copy service scripts
log "Installing service scripts..."
cp ../rollmachine-init.sh /etc/init.d/rollmachine-monitor 2>/dev/null || true
cp ../antix-init.sh /etc/init.d/rollmachine-monitor 2>/dev/null || true
cp ../smart-watchdog-sysv.sh "$INSTALL_DIR/" 2>/dev/null || true
cp ../antix-watchdog.sh "$INSTALL_DIR/" 2>/dev/null || true

# Make scripts executable
chmod +x /etc/init.d/rollmachine-monitor 2>/dev/null || true
chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true

# Create systemd service (if systemd is available)
if command -v systemctl >/dev/null 2>&1; then
    log "Installing systemd service..."
    cp ../rollmachine-smart.service /etc/systemd/system/ 2>/dev/null || true
    systemctl daemon-reload
    systemctl enable rollmachine-smart
fi

# Setup SysV init (for antiX)
if [ -f /etc/init.d/rollmachine-monitor ]; then
    log "Setting up SysV init script..."
    update-rc.d rollmachine-monitor defaults 2>/dev/null || true
fi

# Create desktop entry
log "Creating desktop entry..."
cat > /usr/share/applications/rollmachine-monitor.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Name=Roll Machine Monitor
Comment=JSK3588 Roll Machine Monitoring System
Exec=/opt/rollmachine-monitor/venv/bin/python -m monitoring
Icon=/opt/rollmachine-monitor/monitoring/ui/icon.png
Terminal=false
Type=Application
Categories=Utility;System;
DESKTOP_EOF

# Create logs directory
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/exports"

# Set proper permissions
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Create startup script
log "Creating startup script..."
cat > "$INSTALL_DIR/start-monitor.sh" << 'START_EOF'
#!/bin/bash
cd /opt/rollmachine-monitor
source venv/bin/activate
python -m monitoring "$@"
START_EOF

chmod +x "$INSTALL_DIR/start-monitor.sh"

log "Installation completed successfully!"
info "Application installed to: $INSTALL_DIR"
info "Start the monitor: sudo systemctl start rollmachine-smart"
info "Or manually: cd $INSTALL_DIR && ./start-monitor.sh"
info "For kiosk mode: cd $INSTALL_DIR && ./start-monitor.sh --kiosk"

warn "Remember to:"
warn "1. Configure the serial port in config.json (default: AUTO)"
warn "2. Add your user to the 'dialout' group for serial access"
warn "3. Check that the JSK3588 device is connected"

log "Installation complete!"
EOF

# Create README for deployment
log "Creating deployment README..."
cat > "$PACKAGE_NAME/README-DEPLOYMENT.md" << 'README_EOF'
# Roll Machine Monitor v1.2.4 - antiX Deployment Package

## 🎯 Overview
This package contains everything needed to deploy Roll Machine Monitor v1.2.4 on antiX Linux systems.

## ✨ Key Features (v1.2.4)
- **Automatic Serial Port Detection**: No manual configuration needed
- **Cross-platform Compatibility**: Works on antiX, Ubuntu, and other Linux distributions
- **Enhanced Connection Settings**: Smart port detection with manual override
- **Improved Validation**: Fixed port selection validation issues
- **Kiosk Mode Support**: Full-screen monitoring interface

## 📦 Package Contents
```
rollmachine-monitor-v1.2.4-antix/
├── monitoring-roll-machine/      # Main application
├── install-antix.sh              # Automated installation script
├── antix-*.sh                    # antiX-specific scripts
├── rollmachine-*.service         # Service files
├── smart-watchdog*.sh           # Watchdog scripts
├── config.json                  # Default configuration
├── README-DEPLOYMENT.md         # This file
├── DEPLOYMENT_SUMMARY_v1.2.4.md # Detailed deployment info
└── LICENSE                      # License file
```

## 🚀 Quick Installation

### Method 1: Automated Installation (Recommended)
```bash
# Extract the package
tar -xzf rollmachine-monitor-v1.2.4-antix.tar.gz
cd rollmachine-monitor-v1.2.4-antix

# Run the installation script
sudo ./install-antix.sh
```

### Method 2: Manual Installation
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv python3-tk python3-serial

# Create installation directory
sudo mkdir -p /opt/rollmachine-monitor

# Copy application files
sudo cp -r monitoring-roll-machine/* /opt/rollmachine-monitor/

# Create virtual environment and install dependencies
cd /opt/rollmachine-monitor
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Copy configuration
sudo cp ../config.json /opt/rollmachine-monitor/

# Set up service (choose one)
# For systemd:
sudo cp rollmachine-smart.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rollmachine-smart

# For SysV init (antiX):
sudo cp antix-init.sh /etc/init.d/rollmachine-monitor
sudo chmod +x /etc/init.d/rollmachine-monitor
sudo update-rc.d rollmachine-monitor defaults
```

## 🔧 Configuration

### Default Configuration
The application comes with AUTO port detection enabled:
```json
{
    "serial_port": "AUTO",
    "baudrate": 19200,
    "timeout": 1.0,
    "use_mock_data": false
}
```

### Manual Port Configuration
If you need to specify a port manually:
```json
{
    "serial_port": "/dev/ttyUSB0",
    "baudrate": 19200
}
```

## 🎮 Running the Application

### Start as Service
```bash
# With systemd
sudo systemctl start rollmachine-smart

# With SysV init
sudo /etc/init.d/rollmachine-monitor start
```

### Start Manually
```bash
# Regular mode
cd /opt/rollmachine-monitor
source venv/bin/activate
python -m monitoring

# Kiosk mode (full-screen)
python -m monitoring --kiosk
```

## 🔍 Troubleshooting

### Serial Port Issues
```bash
# Check available ports
ls /dev/tty*

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Check device connections
lsusb | grep -i ch340
```

### Service Issues
```bash
# Check service status
sudo systemctl status rollmachine-smart

# Check logs
sudo journalctl -u rollmachine-smart -f

# Manual restart
sudo systemctl restart rollmachine-smart
```

### Permission Issues
```bash
# Fix permissions
sudo chown -R root:root /opt/rollmachine-monitor
sudo chmod -R 755 /opt/rollmachine-monitor
```

## 📊 Verification

### Check Installation
```bash
# Verify application installed
ls -la /opt/rollmachine-monitor/

# Check service is running
sudo systemctl status rollmachine-smart

# Test application
cd /opt/rollmachine-monitor
source venv/bin/activate
python -c "import monitoring; print('Installation OK')"
```

### Check Serial Connection
```bash
# Test serial port detection
cd /opt/rollmachine-monitor
source venv/bin/activate
python -c "from monitoring.serial_handler import auto_detect_serial_ports; print(auto_detect_serial_ports())"
```

## 📝 Logs and Data

### Log Files
- Application logs: `/opt/rollmachine-monitor/logs/`
- Service logs: `sudo journalctl -u rollmachine-smart`
- Watchdog logs: `/var/log/rollmachine-smart-watchdog.log`

### Export Data
- CSV exports: `/opt/rollmachine-monitor/exports/`
- Session data: Automatically saved during monitoring

## 🆘 Support

### Common Issues
1. **Port not detected**: Check USB connection and drivers
2. **Permission denied**: Add user to dialout group
3. **Service won't start**: Check logs and dependencies
4. **UI won't show**: Ensure X11 forwarding or run locally

### Getting Help
Check the logs first, then refer to the detailed deployment summary for troubleshooting steps.

---

**Roll Machine Monitor v1.2.4**  
*Auto-detection enabled - Zero configuration needed*  
*Ready for antiX deployment*
README_EOF

# Create version file
log "Creating version file..."
cat > "$PACKAGE_NAME/VERSION" << EOF
ROLL_MACHINE_MONITOR_VERSION=1.2.4
BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')
BUILD_FOR=antiX
FEATURES=auto_detection,enhanced_ui,fixed_validation
EOF

# Make all shell scripts executable
log "Setting executable permissions..."
find "$PACKAGE_NAME" -name "*.sh" -exec chmod +x {} \;

# Create checksums
log "Creating checksums..."
find "$PACKAGE_NAME" -type f -exec sha256sum {} \; > "$PACKAGE_NAME/checksums.sha256"

# Create compressed packages
log "Creating compressed packages..."

# Create tar.gz
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# Create zip for Windows compatibility
if command -v zip >/dev/null 2>&1; then
    zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_NAME" >/dev/null
    info "Created ZIP package: ${PACKAGE_NAME}.zip"
fi

# Move to output directory
mv "${PACKAGE_NAME}.tar.gz" "$(dirname "$0")/$OUTPUT_DIR/"
if [ -f "${PACKAGE_NAME}.zip" ]; then
    mv "${PACKAGE_NAME}.zip" "$(dirname "$0")/$OUTPUT_DIR/"
fi

# Cleanup
cd "$(dirname "$0")"
rm -rf "$TEMP_DIR"

# Show results
log "Release package created successfully!"
info "Package: $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
info "Size: $(du -h "$OUTPUT_DIR/${PACKAGE_NAME}.tar.gz" | cut -f1)"
if [ -f "$OUTPUT_DIR/${PACKAGE_NAME}.zip" ]; then
    info "ZIP: $OUTPUT_DIR/${PACKAGE_NAME}.zip"
    info "ZIP Size: $(du -h "$OUTPUT_DIR/${PACKAGE_NAME}.zip" | cut -f1)"
fi

echo ""
log "Ready for deployment to antiX!"
info "Extract and run: sudo ./install-antix.sh"
echo "" 