#!/bin/bash

# Prepare Deployment Package for Private Repository
# Creates self-contained package that can be uploaded to any server

set -e

echo "📦 Preparing Deployment Package for Roll Machine Monitor v1.2.3"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[PACKAGE]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Configuration
PACKAGE_NAME="rollmachine-monitor-fix-v1.2.3"
OUTPUT_DIR="deploy-packages"

# Create output directory
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Create package directory
log "Creating package directory: $PACKAGE_NAME"
mkdir -p "$PACKAGE_NAME"

# Copy all necessary files
log "Copying application files..."
cp -r ../monitoring-roll-machine "$PACKAGE_NAME/"

log "Copying fix scripts..."
cp ../smart-watchdog.sh "$PACKAGE_NAME/" 2>/dev/null || true
cp ../smart-watchdog-sysv.sh "$PACKAGE_NAME/" 2>/dev/null || true
cp ../rollmachine-smart.service "$PACKAGE_NAME/" 2>/dev/null || true
cp ../rollmachine-init.sh "$PACKAGE_NAME/" 2>/dev/null || true
cp ../fix-multiple-instance-offline.sh "$PACKAGE_NAME/"

# Create deployment README
log "Creating deployment documentation..."
cat > "$PACKAGE_NAME/DEPLOYMENT-README.md" << 'EOF'
# Roll Machine Monitor v1.2.3 - Multiple Instance Bug Fix

## 🚨 CRITICAL UPDATE
This package fixes the multiple instance bug that causes application conflicts and resource issues.

## 📦 Package Contents
- `monitoring-roll-machine/` - Complete application with singleton protection
- `smart-watchdog-sysv.sh` - Universal intelligent watchdog (no systemctl needed)
- `rollmachine-init.sh` - SysV/OpenRC init script for auto-start
- `rollmachine-smart.service` - Systemd service (if systemd available)
- `fix-multiple-instance-offline.sh` - Automated installation script

## 🚀 Quick Installation

### Method 1: Automated Install (Recommended)
```bash
# Make script executable
chmod +x fix-multiple-instance-offline.sh

# Run the fix (will backup existing data)
sudo ./fix-multiple-instance-offline.sh
```

### Method 2: Manual Install
```bash
# Stop existing services
sudo systemctl stop rollmachine-kiosk rollmachine-watchdog

# Kill processes
sudo pkill -f "monitoring"

# Backup data
sudo cp -r /opt/rollmachine-monitor/exports /tmp/backup-exports/
sudo cp -r /opt/rollmachine-monitor/logs /tmp/backup-logs/

# Install new version
sudo cp -r monitoring-roll-machine/* /opt/rollmachine-monitor/
sudo cp smart-watchdog.sh /opt/rollmachine-monitor/
sudo cp rollmachine-smart.service /etc/systemd/system/

# Restore data
sudo cp -r /tmp/backup-exports/* /opt/rollmachine-monitor/exports/
sudo cp -r /tmp/backup-logs/* /opt/rollmachine-monitor/logs/

# Configure service
sudo systemctl daemon-reload
sudo systemctl enable rollmachine-smart
sudo systemctl start rollmachine-smart
```

## ✅ Verification
```bash
# Check only one process running
pgrep -f "python.*monitoring" | wc -l  # Should return: 1

# Check service status
sudo systemctl status rollmachine-smart

# Monitor logs
sudo journalctl -u rollmachine-smart -f
```

## 🔧 Management Commands

### If systemd is available:
- Start: `sudo systemctl start rollmachine-smart`
- Stop: `sudo systemctl stop rollmachine-smart`
- Status: `sudo systemctl status rollmachine-smart`

### If using SysV/OpenRC (antiX, Alpine, etc.):
- Start: `sudo /etc/init.d/rollmachine-monitor start`
- Stop: `sudo /etc/init.d/rollmachine-monitor stop`
- Status: `sudo /etc/init.d/rollmachine-monitor status`
- Enable: `sudo /etc/init.d/rollmachine-monitor enable`

### Manual control:
- Start: `cd /opt/rollmachine-monitor && ./smart-watchdog-sysv.sh start`
- Stop: `cd /opt/rollmachine-monitor && ./smart-watchdog-sysv.sh stop`
- Status: `cd /opt/rollmachine-monitor && ./smart-watchdog-sysv.sh status`

### Logs:
- Watchdog: `tail -f /var/log/rollmachine-smart-watchdog.log`

## 🚨 Key Features
- Prevents multiple instances with file locking
- Only restarts on crash or >1 hour idle
- Smart health monitoring every 60 seconds
- Automatic backup and restore of user data

## 📞 Support
If you encounter issues, check the logs and ensure all prerequisites are met.
EOF

# Create checksum file
log "Creating checksums..."
find "$PACKAGE_NAME" -type f -exec sha256sum {} \; > "$PACKAGE_NAME/checksums.sha256"

# Create compressed package
log "Creating compressed package..."
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# Create ZIP for Windows compatibility  
if command -v zip >/dev/null 2>&1; then
    log "Creating ZIP package for Windows compatibility..."
    zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_NAME" >/dev/null
fi

# Generate deployment instructions
log "Generating deployment instructions..."
cat > "DEPLOYMENT-INSTRUCTIONS.txt" << EOF
🚀 DEPLOYMENT INSTRUCTIONS - Roll Machine Monitor v1.2.3
=======================================================

📦 PACKAGE READY: ${PACKAGE_NAME}.tar.gz ($(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1))

🔄 DEPLOYMENT METHODS:

Method 1: SCP/SSH Upload
------------------------
# Upload package to server
scp ${PACKAGE_NAME}.tar.gz user@server-ip:/tmp/

# SSH to server and install
ssh user@server-ip
cd /tmp
tar -xzf ${PACKAGE_NAME}.tar.gz
cd ${PACKAGE_NAME}
sudo ./fix-multiple-instance-offline.sh

Method 2: USB/Physical Transfer  
-------------------------------
# Copy to USB drive
cp ${PACKAGE_NAME}.tar.gz /media/usb/

# On target machine
cd /media/usb/
tar -xzf ${PACKAGE_NAME}.tar.gz
cd ${PACKAGE_NAME}
sudo ./fix-multiple-instance-offline.sh

Method 3: Temporary Web Server
------------------------------
# On development machine (this machine)
cd $(pwd)
python3 -m http.server 8000

# On client machine
wget http://dev-machine-ip:8000/${PACKAGE_NAME}.tar.gz
tar -xzf ${PACKAGE_NAME}.tar.gz
cd ${PACKAGE_NAME}
sudo ./fix-multiple-instance-offline.sh

Method 4: Cloud Storage Upload
------------------------------
# Upload to Google Drive, Dropbox, or other cloud storage
# Download on client machine and extract

⚠️  IMPORTANT NOTES:
- Package is self-contained (no GitHub access needed)
- Automatic backup of existing data before installation
- Works offline completely
- Compatible with all Linux distributions
- Includes comprehensive verification and testing

✅ PACKAGE VERIFICATION:
- Total files: $(find "$PACKAGE_NAME" -type f | wc -l)
- Package size: $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)
- Checksum: $(sha256sum "${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)

🎯 RECOMMENDED: Use Method 1 (SCP/SSH) for fastest deployment
EOF

# Show summary
echo ""
info "============================================"
info "  DEPLOYMENT PACKAGE READY!"
info "============================================"
info "📁 Location: $(pwd)"
info "📦 Package: ${PACKAGE_NAME}.tar.gz ($(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1))"
if [ -f "${PACKAGE_NAME}.zip" ]; then
    info "📦 ZIP: ${PACKAGE_NAME}.zip ($(du -h "${PACKAGE_NAME}.zip" | cut -f1))"
fi
info "📋 Files included: $(find "$PACKAGE_NAME" -type f | wc -l)"
info "🔐 Checksum: $(sha256sum "${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)"
echo ""
info "📖 Read DEPLOYMENT-INSTRUCTIONS.txt for upload methods"
echo ""
log "Package preparation completed! 🎉"
EOF 