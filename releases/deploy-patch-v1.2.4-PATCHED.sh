#!/bin/bash

# Roll Machine Monitor v1.2.4-PATCHED Deployment Script
# CRITICAL FIX: Missing signal connection and port validation issues

set -e

echo "=========================================="
echo "Roll Machine Monitor v1.2.4-PATCHED"
echo "CRITICAL BUG FIX DEPLOYMENT"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Stop existing service
echo "🛑 Stopping existing service..."
systemctl stop rollmachine-kiosk 2>/dev/null || true
systemctl stop rollmachine-monitor 2>/dev/null || true

# Backup existing installation
echo "💾 Creating backup..."
if [ -d "/opt/rollmachine-monitor" ]; then
    cp -r /opt/rollmachine-monitor /opt/rollmachine-monitor.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created: /opt/rollmachine-monitor.backup.*"
fi

# Extract and deploy patched files
echo "📦 Deploying patched files..."
cd /tmp
rm -rf rollmachine-monitor-v1.2.4-PATCHED
unzip -q /path/to/rollmachine-monitor-v1.2.4-PATCHED.zip

# Deploy to /opt
echo "🚀 Installing to /opt/rollmachine-monitor..."
rm -rf /opt/rollmachine-monitor
cp -r rollmachine-monitor-v1.2.4-PATCHED/monitoring-roll-machine /opt/rollmachine-monitor

# Set permissions
echo "🔐 Setting permissions..."
chown -R root:root /opt/rollmachine-monitor
chmod -R 755 /opt/rollmachine-monitor
chmod +x /opt/rollmachine-monitor/*.sh

# Ensure user is in dialout group
echo "👥 Adding user to dialout group..."
usermod -a -G dialout $SUDO_USER 2>/dev/null || true

# Install service files
echo "⚙️ Installing service files..."
cp rollmachine-monitor-v1.2.4-PATCHED/*.service /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload

# Start service
echo "▶️ Starting service..."
systemctl enable rollmachine-kiosk
systemctl start rollmachine-kiosk

# Verify installation
echo "✅ Verifying installation..."
sleep 3
if systemctl is-active --quiet rollmachine-kiosk; then
    echo "✅ Service is running successfully!"
else
    echo "⚠️ Service may not be running. Check logs:"
    echo "   journalctl -u rollmachine-kiosk -f"
fi

echo ""
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "CRITICAL FIXES APPLIED:"
echo "✅ Fixed missing start_monitoring signal connection"
echo "✅ Removed blocking port validation"
echo "✅ Disabled all demo mode fallbacks"
echo "✅ Force real serial connection only"
echo ""
echo "Expected Results:"
echo "✅ 'Start Monitoring' button now works"
echo "✅ No more 'Please select a serial port' errors"
echo "✅ Shows '✅ REAL Connection (/dev/ttyUSB0)'"
echo "✅ Displays actual JSK3588 data (not simulation)"
echo ""
echo "To test:"
echo "1. Check service status: systemctl status rollmachine-kiosk"
echo "2. View logs: journalctl -u rollmachine-kiosk -f"
echo "3. Manual test: cd /opt/rollmachine-monitor && python -m monitoring"
echo ""
echo "If issues persist:"
echo "1. Check device: ls -la /dev/ttyUSB0"
echo "2. Check permissions: groups $USER | grep dialout"
echo "3. Check USB: lsusb | grep -i ch340"
echo ""
echo "==========================================" 