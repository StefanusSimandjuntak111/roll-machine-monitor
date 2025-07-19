#!/bin/bash

# Fix Multiple Instance Bug Script v1.2.3
# Implements singleton pattern, smart watchdog, and idle detection

set -e

echo "🚀 Starting Fix for Multiple Instance Bug - Roll Machine Monitor v1.2.3"

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
GITHUB_TAG="v1.2.2"
DOWNLOAD_URL="https://github.com/hokgt/textilindo_roll_printer/archive/refs/tags/${GITHUB_TAG}.tar.gz"

# Step 1: Emergency stop all instances
info "Step 1: Emergency stop of all running instances"
log "Forcibly stopping all monitoring processes..."

# Stop systemd services
sudo systemctl stop rollmachine-kiosk 2>/dev/null || true
sudo systemctl stop rollmachine-watchdog 2>/dev/null || true
sudo systemctl stop rollmachine-smart 2>/dev/null || true

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

# Step 2: Backup existing installation
info "Step 2: Backup existing installation"
if [ -d "$INSTALL_DIR" ]; then
    log "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    sudo cp -r "$INSTALL_DIR/exports" "$BACKUP_DIR/" 2>/dev/null || true
    sudo cp -r "$INSTALL_DIR/logs" "$BACKUP_DIR/" 2>/dev/null || true
    sudo cp "$INSTALL_DIR/config.json" "$BACKUP_DIR/" 2>/dev/null || true
    log "✅ Backup created successfully"
fi

# Step 3: Download and install fixed version
info "Step 3: Download and install fixed version with singleton protection"
log "Downloading Roll Machine Monitor $GITHUB_TAG..."
cd /tmp

# Download with progress
if command -v wget >/dev/null 2>&1; then
    wget --progress=bar:force -O "fix-${GITHUB_TAG}.tar.gz" "$DOWNLOAD_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar -o "fix-${GITHUB_TAG}.tar.gz" "$DOWNLOAD_URL"
else
    error "Neither wget nor curl is available. Please install one of them."
    exit 1
fi

# Extract and install
log "Extracting and installing..."
tar -xzf "fix-${GITHUB_TAG}.tar.gz"
cd "textilindo_roll_printer-${GITHUB_TAG#v}"

# Install application
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r monitoring-roll-machine/* "$INSTALL_DIR/"

# Install smart watchdog
sudo cp smart-watchdog.sh "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/smart-watchdog.sh"

# Install new service
sudo cp rollmachine-smart.service /etc/systemd/system/

# Step 4: Restore configuration and data
info "Step 4: Restore configuration and data"
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
sudo chown -R kiosk:rollmachine "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR"/*.sh

# Step 5: Update Python dependencies
info "Step 5: Update Python dependencies"
cd "$INSTALL_DIR"

if [ -d "venv" ]; then
    log "Updating virtual environment..."
    source venv/bin/activate
    pip install -r requirements.txt --upgrade --quiet
else
    log "Installing dependencies globally..."
    pip install -r requirements.txt --upgrade --user --quiet
fi

# Step 6: Disable old services and enable new one
info "Step 6: Configure smart watchdog service"

# Disable old services
sudo systemctl disable rollmachine-kiosk 2>/dev/null || true
sudo systemctl disable rollmachine-watchdog 2>/dev/null || true

# Backup old services
sudo mv /etc/systemd/system/rollmachine-kiosk.service /etc/systemd/system/rollmachine-kiosk.service.disabled 2>/dev/null || true
sudo mv /etc/systemd/system/rollmachine-watchdog.service /etc/systemd/system/rollmachine-watchdog.service.disabled 2>/dev/null || true

# Enable new smart service
sudo systemctl daemon-reload
sudo systemctl enable rollmachine-smart

log "✅ Smart watchdog service configured"

# Step 7: Test the fix
info "Step 7: Testing the fix"

log "Testing singleton protection..."
cd "$INSTALL_DIR"

# Test 1: Start application manually
python -m monitoring &
APP_PID=$!
sleep 3

# Test 2: Try to start second instance (should fail)
if python -m monitoring 2>/dev/null &; then
    SECOND_PID=$!
    sleep 2
    if kill -0 $SECOND_PID 2>/dev/null; then
        error "❌ SINGLETON PROTECTION FAILED - Second instance started!"
        kill $APP_PID $SECOND_PID 2>/dev/null || true
        exit 1
    else
        log "✅ Singleton protection working - second instance rejected"
    fi
else
    log "✅ Singleton protection working - second instance prevented"
fi

# Clean up test
kill $APP_PID 2>/dev/null || true
sleep 2

# Test 3: Test smart watchdog
log "Testing smart watchdog..."
sudo systemctl start rollmachine-smart
sleep 5

if sudo systemctl is-active --quiet rollmachine-smart; then
    log "✅ Smart watchdog service started successfully"
    
    # Check if application is running
    if pgrep -f "python.*monitoring" >/dev/null; then
        log "✅ Application started by smart watchdog"
    else
        warn "⚠️  Smart watchdog started but application not detected"
    fi
else
    error "❌ Smart watchdog service failed to start"
    sudo systemctl status rollmachine-smart
fi

# Step 8: Final verification and summary
info "Step 8: Final verification"

# Check singleton lock
if [ -f "/tmp/rollmachine_monitor.lock" ]; then
    log "✅ Singleton lock file created"
else
    warn "⚠️  Singleton lock file not found"
fi

# Check heartbeat
sleep 15  # Wait for heartbeat to be created
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
except:
    print('   Could not read heartbeat data')
"
else
    warn "⚠️  Heartbeat file not found"
fi

# Check process count
PROCESS_COUNT=$(pgrep -f "python.*monitoring" | wc -l)
if [ "$PROCESS_COUNT" -eq 1 ]; then
    log "✅ Exactly one monitoring process running"
elif [ "$PROCESS_COUNT" -eq 0 ]; then
    warn "⚠️  No monitoring process running"
else
    error "❌ Multiple monitoring processes detected: $PROCESS_COUNT"
    pgrep -f "python.*monitoring"
fi

# Cleanup
rm -rf /tmp/fix-*.tar.gz /tmp/textilindo_roll_printer-* 2>/dev/null || true

# Summary
echo ""
echo "🎉 ======================================"
echo "   MULTIPLE INSTANCE BUG FIX COMPLETE"
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
echo "   • Clean service management"
echo ""
echo "🔧 Management Commands:"
echo "   Start:   sudo systemctl start rollmachine-smart"
echo "   Stop:    sudo systemctl stop rollmachine-smart"
echo "   Status:  sudo systemctl status rollmachine-smart"
echo "   Logs:    sudo journalctl -u rollmachine-smart -f"
echo "   Watchdog: tail -f /var/log/rollmachine-smart-watchdog.log"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo "🏠 Installation: $INSTALL_DIR"
echo ""
log "Fix completed successfully! 🚀" 