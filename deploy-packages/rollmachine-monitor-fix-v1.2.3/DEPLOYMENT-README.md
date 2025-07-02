# Roll Machine Monitor v1.2.3 - Multiple Instance Bug Fix

## 🚨 CRITICAL UPDATE
This package fixes the multiple instance bug that causes application conflicts and resource issues.

## 📦 Package Contents
- `monitoring-roll-machine/` - Complete application with singleton protection
- `smart-watchdog.sh` - Intelligent watchdog with idle detection  
- `rollmachine-smart.service` - Systemd service configuration
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
- Start: `sudo systemctl start rollmachine-smart`
- Stop: `sudo systemctl stop rollmachine-smart`  
- Status: `sudo systemctl status rollmachine-smart`
- Logs: `tail -f /var/log/rollmachine-smart-watchdog.log`

## 🚨 Key Features
- Prevents multiple instances with file locking
- Only restarts on crash or >1 hour idle
- Smart health monitoring every 60 seconds
- Automatic backup and restore of user data

## 📞 Support
If you encounter issues, check the logs and ensure all prerequisites are met.
