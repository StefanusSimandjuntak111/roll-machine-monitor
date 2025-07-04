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

# Backup existing installation if it exists
if [ -d "$INSTALL_DIR" ] && [ "$(ls -A $INSTALL_DIR)" ]; then
    BACKUP_DIR="/opt/rollmachine-monitor-backup-$(date +%Y%m%d-%H%M%S)"
    warn "Existing installation found. Backing up to: $BACKUP_DIR"
    cp -r "$INSTALL_DIR" "$BACKUP_DIR"
fi

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
if [ -f ../config.json ]; then
    cp ../config.json "$INSTALL_DIR/"
fi

# Copy service scripts
log "Installing service scripts..."
if [ -f ../rollmachine-init.sh ]; then
    cp ../rollmachine-init.sh /etc/init.d/rollmachine-monitor
    chmod +x /etc/init.d/rollmachine-monitor
fi

if [ -f ../antix-init.sh ]; then
    cp ../antix-init.sh /etc/init.d/rollmachine-monitor
    chmod +x /etc/init.d/rollmachine-monitor
fi

if [ -f ../smart-watchdog-sysv.sh ]; then
    cp ../smart-watchdog-sysv.sh "$INSTALL_DIR/"
fi

if [ -f ../antix-watchdog.sh ]; then
    cp ../antix-watchdog.sh "$INSTALL_DIR/"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true

# Create systemd service (if systemd is available)
if command -v systemctl >/dev/null 2>&1; then
    log "Installing systemd service..."
    if [ -f ../rollmachine-smart.service ]; then
        cp ../rollmachine-smart.service /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable rollmachine-smart
    fi
fi

# Setup SysV init (for antiX)
if [ -f /etc/init.d/rollmachine-monitor ]; then
    log "Setting up SysV init script..."
    update-rc.d rollmachine-monitor defaults 2>/dev/null || true
fi

# Create desktop entry
log "Creating desktop entry..."
cat > /usr/share/applications/rollmachine-monitor.desktop << 'EOF'
[Desktop Entry]
Name=Roll Machine Monitor
Comment=JSK3588 Roll Machine Monitoring System
Exec=/opt/rollmachine-monitor/venv/bin/python -m monitoring
Icon=/opt/rollmachine-monitor/monitoring/ui/icon.png
Terminal=false
Type=Application
Categories=Utility;System;
EOF

# Create logs directory
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/exports"

# Set proper permissions
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Create startup script
log "Creating startup script..."
cat > "$INSTALL_DIR/start-monitor.sh" << 'EOF'
#!/bin/bash
cd /opt/rollmachine-monitor
source venv/bin/activate
python -m monitoring "$@"
EOF

chmod +x "$INSTALL_DIR/start-monitor.sh"

# Create kiosk startup script
log "Creating kiosk startup script..."
cat > "$INSTALL_DIR/start-kiosk.sh" << 'EOF'
#!/bin/bash
cd /opt/rollmachine-monitor
source venv/bin/activate
python -m monitoring --kiosk
EOF

chmod +x "$INSTALL_DIR/start-kiosk.sh"

log "Installation completed successfully!"
info "Application installed to: $INSTALL_DIR"

# Give instructions based on available init system
if command -v systemctl >/dev/null 2>&1; then
    info "Start the monitor: sudo systemctl start rollmachine-smart"
    info "Enable auto-start: sudo systemctl enable rollmachine-smart"
else
    info "Start the monitor: sudo /etc/init.d/rollmachine-monitor start"
    info "Enable auto-start: sudo update-rc.d rollmachine-monitor enable"
fi

info "Manual start: cd $INSTALL_DIR && ./start-monitor.sh"
info "Kiosk mode: cd $INSTALL_DIR && ./start-kiosk.sh"

warn "Remember to:"
warn "1. Configure the serial port in config.json (default: AUTO)"
warn "2. Add your user to the 'dialout' group for serial access:"
warn "   sudo usermod -a -G dialout \$USER"
warn "3. Check that the JSK3588 device is connected"
warn "4. Reboot or log out/in for group changes to take effect"

log "Installation complete!" 