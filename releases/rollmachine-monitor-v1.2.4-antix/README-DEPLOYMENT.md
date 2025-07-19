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
unzip rollmachine-monitor-v1.2.4-antix.zip
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