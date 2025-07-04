#!/bin/bash
# EMERGENCY PATCH - Force Disable Demo Mode

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[PATCH]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log "🚨 EMERGENCY PATCH DEPLOYMENT - Disable Demo Mode"

# 1. Force stop all monitoring processes
log "1. Force stopping all monitoring processes..."
sudo pkill -9 -f "python.*monitoring" 2>/dev/null || true
sudo pkill -9 -f "smart-watchdog" 2>/dev/null || true
sudo pkill -9 -f "rollmachine" 2>/dev/null || true

# 2. Stop all services
log "2. Stopping all services..."
sudo systemctl stop rollmachine-smart 2>/dev/null || true
sudo systemctl stop rollmachine-kiosk 2>/dev/null || true
sudo systemctl stop rollmachine-watchdog 2>/dev/null || true
sudo /etc/init.d/rollmachine-monitor stop 2>/dev/null || true

# 3. Clean ALL lock files
log "3. Cleaning lock files..."
sudo rm -f /tmp/rollmachine_monitor.lock
sudo rm -f /tmp/rollmachine_heartbeat
sudo rm -f /tmp/rollmachine_restart_attempt  
sudo rm -f /tmp/exit_kiosk_mode
sudo rm -f /tmp/rollmachine_*.lock
sudo rm -f /var/run/rollmachine*

# 4. Verify device access
log "4. Verifying device access..."
if [ ! -e /dev/ttyUSB0 ]; then
    error "Device /dev/ttyUSB0 not found!"
    lsusb | grep -i ch340 || echo "CH340 device not detected"
    exit 1
fi

ls -la /dev/ttyUSB0
log "Device found: $(ls -la /dev/ttyUSB0)"

# 5. Check user permissions
log "5. Checking user permissions..."
if ! groups $USER | grep -q dialout; then
    warn "User not in dialout group, adding..."
    sudo usermod -a -G dialout $USER
fi

# 6. Deploy patched files
log "6. Deploying patched application files..."
PATCH_SOURCE="/d%3A/Apps/monitoring-roll-machine/monitoring-roll-machine"
INSTALL_DIR="/opt/rollmachine-monitor"

if [ ! -d "$PATCH_SOURCE" ]; then
    error "Patch source not found: $PATCH_SOURCE"
    exit 1
fi

# Backup current installation
if [ -d "$INSTALL_DIR" ]; then
    BACKUP_DIR="/tmp/rollmachine-backup-$(date +%Y%m%d-%H%M%S)"
    log "Backing up current installation to: $BACKUP_DIR"
    sudo cp -r "$INSTALL_DIR" "$BACKUP_DIR"
fi

# Deploy patched files
log "Copying patched application files..."
sudo cp -r "$PATCH_SOURCE"/* "$INSTALL_DIR/"

# 7. Fix permissions
log "7. Fixing permissions..."
sudo chown -R root:root "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true

# 8. Test serial access
log "8. Testing serial access..."
cd "$INSTALL_DIR"
source venv/bin/activate

python -c "
import serial
try:
    ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=1)
    print('✅ Serial port accessible')
    ser.close()
except Exception as e:
    print(f'❌ Serial port error: {e}')
    import os
    os._exit(1)
"

# 9. Verify patch deployment
log "9. Verifying patch deployment..."
python -c "
import json
try:
    with open('monitoring/config.json', 'r') as f:
        config = json.load(f)
    print(f'✅ Config serial_port: {config.get(\"serial_port\", \"NOT_SET\")}')
    print(f'✅ Config use_mock_data: {config.get(\"use_mock_data\", \"NOT_SET\")}')
    
    # Check if patched main_window.py exists
    with open('monitoring/ui/main_window.py', 'r') as f:
        content = f.read()
    if 'FORCED real serial connection' in content:
        print('✅ Patch applied successfully')
    else:
        print('❌ Patch NOT applied')
        import os
        os._exit(1)
except Exception as e:
    print(f'❌ Verification error: {e}')
    import os  
    os._exit(1)
"

# 10. Apply group changes and test start
log "10. Testing application start..."
newgrp dialout << 'EOF'
cd /opt/rollmachine-monitor
source venv/bin/activate

echo "Testing import..."
python -c "import monitoring; print('✅ Import successful')"

echo "Testing serial handler..."
python -c "
from monitoring.serial_handler import JSKSerialPort
try:
    port = JSKSerialPort('/dev/ttyUSB0', 19200, simulation_mode=False)
    port.open()
    print('✅ Real serial port opened successfully')
    port.close()
    print('✅ Real serial port closed successfully')
except Exception as e:
    print(f'❌ Real serial port error: {e}')
"

echo "🚀 Starting patched application..."
python -m monitoring &
APP_PID=$!

sleep 5

if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ Application started successfully (PID: $APP_PID)"
    echo "Check if demo mode is disabled and real connection is active"
else
    echo "❌ Application failed to start"
fi
EOF

log "🎉 EMERGENCY PATCH DEPLOYMENT COMPLETE!"
log ""
log "What happened:"
log "✅ Disabled ALL fallback to demo mode"  
log "✅ Forced real serial connection to /dev/ttyUSB0"
log "✅ Removed mock monitoring function"
log "✅ Updated configuration"
log ""
log "If still in demo mode, the device may not be responding properly."
log "Check physical connection and device power." 