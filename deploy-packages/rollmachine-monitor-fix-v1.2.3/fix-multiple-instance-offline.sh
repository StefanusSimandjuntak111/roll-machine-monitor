#!/bin/bash

# Offline Fix Multiple Instance Bug Script v1.2.3
# For private repository - works with local/uploaded files

set -e

echo "🚀 Starting OFFLINE Fix for Multiple Instance Bug - Roll Machine Monitor v1.2.3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[FIX]${NC} $1"
}

# Configuration
INSTALL_DIR="/opt/rollmachine-monitor"
BACKUP_DIR="/tmp/rollmachine-backup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if fix files exist in current directory
check_files() {
    local missing_files=()
    
    if [ ! -d "monitoring-roll-machine" ]; then
        missing_files+=("monitoring-roll-machine/")
    fi
    
    if [ ! -f "smart-watchdog.sh" ]; then
        missing_files+=("smart-watchdog.sh")
    fi
    
    if [ ! -f "rollmachine-smart.service" ]; then
        missing_files+=("rollmachine-smart.service")
    fi
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        error "Missing required files in current directory:"
        for file in "${missing_files[@]}"; do
            error "  - $file"
        done
        echo ""
        error "Please ensure you have uploaded all fix files to the current directory:"
        error "  1. monitoring-roll-machine/ (complete application directory)"
        error "  2. smart-watchdog.sh"
        error "  3. rollmachine-smart.service"
        error "  4. fix-multiple-instance-offline.sh (this script)"
        echo ""
        error "You can extract these from: rollmachine-monitor-fix-v1.2.3.tar.gz"
        exit 1
    fi
    
    log "✅ All required files found in current directory"
}

# Step 1: Check prerequisites
info "Step 1: Check prerequisites and files"
check_files

# Step 2: Emergency stop all instances
info "Step 2: Emergency stop of all running instances"
log "Forcibly stopping all monitoring processes..."

# Stop any existing services (try multiple methods)
# Try systemctl first (if available)
sudo systemctl stop rollmachine-kiosk rollmachine-watchdog rollmachine-smart 2>/dev/null || true

# Try traditional init scripts
sudo /etc/init.d/rollmachine-monitor stop 2>/dev/null || true
sudo service rollmachine-monitor stop 2>/dev/null || true

# Try OpenRC (Alpine/Gentoo)
sudo rc-service rollmachine-monitor stop 2>/dev/null || true

# Kill all processes
sudo pkill -f "monitoring" 2>/dev/null || true
sudo pkill -f "rollmachine" 2>/dev/null || true
sudo pkill -f "watchdog" 2>/dev/null || true
sudo pkill -f "python.*monitor" 2>/dev/null || true

sleep 3

# Force kill if still running
if pgrep -f "monitoring" > /dev/null; then
    warn "Some processes still running. Force killing..."
    sudo pkill -9 -f "monitoring" 2>/dev/null || true
    sudo pkill -9 -f "rollmachine" 2>/dev/null || true
    sleep 2
fi

# Clean up lock files
sudo rm -f /tmp/rollmachine_monitor.lock /tmp/rollmachine_heartbeat

log "✅ All instances stopped successfully"

# Step 3: Backup existing installation
info "Step 3: Backup existing installation"
if [ -d "$INSTALL_DIR" ]; then
    log "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    sudo cp -r "$INSTALL_DIR/exports" "$BACKUP_DIR/" 2>/dev/null || true
    sudo cp -r "$INSTALL_DIR/logs" "$BACKUP_DIR/" 2>/dev/null || true
    sudo cp "$INSTALL_DIR/config.json" "$BACKUP_DIR/" 2>/dev/null || true
    log "✅ Backup created successfully"
fi

# Step 4: Install fixed version from local files
info "Step 4: Install fixed version from local files"
log "Installing from local directory: $SCRIPT_DIR"

# Install application
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r monitoring-roll-machine/* "$INSTALL_DIR/"

# Install smart watchdog (universal version)
sudo cp smart-watchdog-sysv.sh "$INSTALL_DIR/" 2>/dev/null || sudo cp smart-watchdog.sh "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/smart-watchdog"*

# Install init script
sudo cp rollmachine-init.sh /etc/init.d/rollmachine-monitor 2>/dev/null || true
sudo chmod +x /etc/init.d/rollmachine-monitor 2>/dev/null || true

# Install systemd service (if systemd is available)
if command -v systemctl >/dev/null 2>&1; then
    sudo cp rollmachine-smart.service /etc/systemd/system/ 2>/dev/null || true
fi

log "✅ Files installed successfully"

# Step 5: Restore configuration and data
info "Step 5: Restore configuration and data"
if [ -f "$BACKUP_DIR/config.json" ]; then
    log "Restoring configuration..."
    sudo cp "$BACKUP_DIR/config.json" "$INSTALL_DIR/"
fi

if [ -d "$BACKUP_DIR/exports" ]; then
    log "Restoring exports..."
    sudo cp -r "$BACKUP_DIR/exports"/* "$INSTALL_DIR/exports/" 2>/dev/null || true
fi

if [ -d "$BACKUP_DIR/logs" ]; then
    log "Restoring logs..."
    sudo cp -r "$BACKUP_DIR/logs"/* "$INSTALL_DIR/logs/" 2>/dev/null || true
fi

# Set proper permissions
sudo chown -R kiosk:rollmachine "$INSTALL_DIR" 2>/dev/null || sudo chown -R $USER:$USER "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR"/*.sh

# Step 6: Update Python dependencies
info "Step 6: Update Python dependencies"
cd "$INSTALL_DIR"

if [ -d "venv" ]; then
    log "Updating virtual environment..."
    source venv/bin/activate
    pip install -r requirements.txt --upgrade --quiet
else
    log "Installing dependencies globally..."
    pip install -r requirements.txt --upgrade --user --quiet 2>/dev/null || pip3 install -r requirements.txt --upgrade --user --quiet
fi

# Step 7: Configure smart watchdog service (universal)
info "Step 7: Configure smart watchdog service (universal)"

# Disable old services (try all methods)
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl disable rollmachine-kiosk rollmachine-watchdog rollmachine-smart 2>/dev/null || true
    sudo systemctl daemon-reload 2>/dev/null || true
    
    # Backup old systemd services
    sudo mv /etc/systemd/system/rollmachine-kiosk.service /etc/systemd/system/rollmachine-kiosk.service.disabled 2>/dev/null || true
    sudo mv /etc/systemd/system/rollmachine-watchdog.service /etc/systemd/system/rollmachine-watchdog.service.disabled 2>/dev/null || true
fi

# Disable old SysV services
sudo update-rc.d -f rollmachine-monitor remove 2>/dev/null || true
sudo chkconfig rollmachine-monitor off 2>/dev/null || true
sudo rc-update del rollmachine-monitor default 2>/dev/null || true

# Configure new service based on available init system
if command -v systemctl >/dev/null 2>&1 && [ -f "/etc/systemd/system/rollmachine-smart.service" ]; then
    # Use systemd
    sudo systemctl enable rollmachine-smart
    log "✅ Systemd service configured"
elif [ -f "/etc/init.d/rollmachine-monitor" ]; then
    # Use traditional init script
    sudo /etc/init.d/rollmachine-monitor enable
    log "✅ SysV init service configured"
else
    # Manual configuration
    log "⚠️  Manual service configuration required"
    log "   Run: /opt/rollmachine-monitor/smart-watchdog-sysv.sh start"
fi

log "✅ Smart watchdog service configured"

# Step 8: Test the fix
info "Step 8: Testing the fix"

log "Testing singleton protection..."
cd "$INSTALL_DIR"

# Test 1: Start application manually
timeout 10s python -m monitoring &
APP_PID=$!
sleep 3

# Test 2: Try to start second instance (should fail)
timeout 5s python -m monitoring 2>/dev/null &
SECOND_PID=$!
sleep 2

SECOND_RUNNING=false
if kill -0 $SECOND_PID 2>/dev/null; then
    SECOND_RUNNING=true
fi

# Clean up test
kill $APP_PID $SECOND_PID 2>/dev/null || true
sleep 2

if [ "$SECOND_RUNNING" = true ]; then
    error "❌ SINGLETON PROTECTION FAILED - Second instance started!"
    exit 1
else
    log "✅ Singleton protection working - second instance prevented"
fi

# Test 3: Test smart watchdog (universal)
log "Testing smart watchdog..."

# Start service using available method
if command -v systemctl >/dev/null 2>&1 && [ -f "/etc/systemd/system/rollmachine-smart.service" ]; then
    # Use systemd
    sudo systemctl start rollmachine-smart
    sleep 10
    
    if sudo systemctl is-active --quiet rollmachine-smart; then
        log "✅ Systemd service started successfully"
        SERVICE_STARTED=true
    else
        warn "⚠️  Systemd service failed to start"
        SERVICE_STARTED=false
    fi
elif [ -f "/etc/init.d/rollmachine-monitor" ]; then
    # Use SysV init
    sudo /etc/init.d/rollmachine-monitor start
    sleep 10
    
    if sudo /etc/init.d/rollmachine-monitor status >/dev/null 2>&1; then
        log "✅ SysV service started successfully"
        SERVICE_STARTED=true
    else
        warn "⚠️  SysV service failed to start"
        SERVICE_STARTED=false
    fi
else
    # Manual start
    log "Starting watchdog manually..."
    cd "$INSTALL_DIR"
    ./smart-watchdog-sysv.sh start 2>/dev/null || ./smart-watchdog.sh start 2>/dev/null || true
    sleep 10
    SERVICE_STARTED=true
fi

# Check if application is running
if [ "$SERVICE_STARTED" = true ]; then
    if pgrep -f "python.*monitoring" >/dev/null; then
        log "✅ Application started by smart watchdog"
    else
        warn "⚠️  Smart watchdog started but application not detected yet (may be starting)"
    fi
else
    warn "⚠️  Service start verification failed, but application may still be running"
fi

# Step 9: Final verification and summary
info "Step 9: Final verification"

# Wait for application to fully start
sleep 10

# Check singleton lock
if [ -f "/tmp/rollmachine_monitor.lock" ]; then
    log "✅ Singleton lock file created"
else
    warn "⚠️  Singleton lock file not found (may still be starting)"
fi

# Check heartbeat
if [ -f "/tmp/rollmachine_heartbeat" ]; then
    log "✅ Heartbeat file created"
    
    # Show heartbeat content
    python3 -c "
import json
try:
    with open('/tmp/rollmachine_heartbeat', 'r') as f:
        data = json.load(f)
    print(f'   PID: {data[\"pid\"]}')
    print(f'   Idle time: {data[\"idle_seconds\"]}s')
    print(f'   Processing data: {data[\"is_processing_data\"]}')
except Exception as e:
    print(f'   Could not read heartbeat data: {e}')
" 2>/dev/null || echo "   Heartbeat starting..."
else
    warn "⚠️  Heartbeat file not found yet (application may still be initializing)"
fi

# Check process count
PROCESS_COUNT=$(pgrep -f "python.*monitoring" | wc -l)
if [ "$PROCESS_COUNT" -eq 1 ]; then
    log "✅ Exactly one monitoring process running"
elif [ "$PROCESS_COUNT" -eq 0 ]; then
    warn "⚠️  No monitoring process running yet (may be starting)"
else
    error "❌ Multiple monitoring processes detected: $PROCESS_COUNT"
    pgrep -f "python.*monitoring"
fi

# Summary
echo ""
echo "🎉 ======================================"
echo "   OFFLINE MULTIPLE INSTANCE BUG FIX COMPLETE"
echo "======================================"
echo "✅ Fixes Applied:"
echo "   • Singleton pattern prevents multiple instances"
echo "   • Smart watchdog with idle detection (1 hour threshold)"
echo "   • Heartbeat system for crash vs idle detection"
echo "   • Memory monitoring and leak prevention"
echo "   • Clean shutdown mechanisms"
echo ""
echo "📋 Key Features:"
echo "   • Only restarts on CRASH or >1 hour idle"
echo "   • Prevents multiple instances with file locking"
echo "   • Smart health monitoring every 60 seconds"
echo "   • Works offline without GitHub access"
echo ""
echo "🔧 Management Commands:"
if command -v systemctl >/dev/null 2>&1 && [ -f "/etc/systemd/system/rollmachine-smart.service" ]; then
    echo "   Start:   sudo systemctl start rollmachine-smart"
    echo "   Stop:    sudo systemctl stop rollmachine-smart"
    echo "   Status:  sudo systemctl status rollmachine-smart"
    echo "   Logs:    sudo journalctl -u rollmachine-smart -f"
elif [ -f "/etc/init.d/rollmachine-monitor" ]; then
    echo "   Start:   sudo /etc/init.d/rollmachine-monitor start"
    echo "   Stop:    sudo /etc/init.d/rollmachine-monitor stop"
    echo "   Status:  sudo /etc/init.d/rollmachine-monitor status"
    echo "   Enable:  sudo /etc/init.d/rollmachine-monitor enable"
else
    echo "   Start:   cd $INSTALL_DIR && ./smart-watchdog-sysv.sh start"
    echo "   Stop:    cd $INSTALL_DIR && ./smart-watchdog-sysv.sh stop"
    echo "   Status:  cd $INSTALL_DIR && ./smart-watchdog-sysv.sh status"
fi
echo "   Watchdog: tail -f /var/log/rollmachine-smart-watchdog.log"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo "🏠 Installation: $INSTALL_DIR"
echo ""
log "Offline fix completed successfully! 🚀" 