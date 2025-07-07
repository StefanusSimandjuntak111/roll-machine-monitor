# Roll Machine Monitor v1.2.6 for antiX
## Enhanced Settings & Port Management

### 🎉 New Features in v1.2.6

#### **Enhanced Settings Dialog**
- **Tabbed Interface**: Port Settings, Page Settings, Port Management
- **Decimal Format Selection**: #, #.#, #.##
- **Length Tolerance**: Configurable percentage (default: 3%)
- **Rounding Method**: UP/DOWN options
- **Conversion Factor Preview**: Real-time preview

#### **Port Management Tab** 🆕
- **Kill/Close Port**: Force close stuck connections
- **Auto Connect**: Automatically connect to available ports
- **Disconnect**: Safely disconnect from current port
- **Auto Reconnect**: Automatic reconnection on disconnect
- **Connection Status**: Real-time status with color coding

### 🚀 Installation

#### **1. Extract Package**
```bash
tar -xzf rollmachine-monitor-v1.2.6-antix.tar.gz
cd rollmachine-monitor-v1.2.6-antix
```

#### **2. Install Dependencies**
```bash
sudo ./install-rollmachine.sh
```

#### **3. Reboot (Important!)**
```bash
sudo reboot
```

### 🎯 Usage

#### **Start Application**

**Kiosk Mode (Recommended for Production):**
```bash
/opt/rollmachine-monitor/start_kiosk.sh
```

**Normal Mode (For Development):**
```bash
/opt/rollmachine-monitor/start_normal.sh
```

**Using SysV init (antiX):**
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

#### **Desktop Shortcuts**
After installation, you'll find these shortcuts on your desktop:
- **Roll Machine Monitor (Kiosk)**: Start in kiosk mode
- **Roll Machine Monitor (Normal)**: Start in normal mode
- **Exit Kiosk Mode**: Exit kiosk mode

### ⚙️ Settings Configuration

#### **Access Settings**
1. Click **Settings** button in main window
2. Choose appropriate tab:
   - **Port Settings**: Serial connection configuration
   - **Page Settings**: Display configuration
   - **Port Management**: Port connection control

#### **Port Management Features**
1. **Auto Connect**: Click to automatically connect
2. **Kill Port**: If port is stuck, click to force close
3. **Disconnect**: Safely disconnect from current port
4. **Auto Reconnect**: Enable for automatic reconnection

### 🔧 Configuration Files

#### **config.json**
```json
{
    "serial_port": "COM6",
    "baudrate": 19200,
    "length_tolerance": 3.0,
    "decimal_points": 1,
    "rounding": "UP"
}
```

### 🐛 Troubleshooting

#### **Port Not Found**
```bash
# Check available ports
ls /dev/tty*

# Check user permissions
groups $USER
```

#### **Permission Denied**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot
sudo reboot
```

#### **Service Not Starting**
```bash
# Check service status
sudo /etc/init.d/rollmachine-monitor status

# Check logs
tail -f /opt/rollmachine-monitor/logs/watchdog.log
```

### 📊 Log Files

#### **Application Logs**
```bash
tail -f /opt/rollmachine-monitor/logs/monitoring.log
```

#### **Watchdog Logs**
```bash
tail -f /opt/rollmachine-monitor/logs/watchdog.log
```

#### **System Logs**
```bash
dmesg | grep tty
```

### 🔄 Auto-Start Configuration

#### **Enable Auto-Start (SysV)**
```bash
# Enable service to start on boot
sudo update-rc.d rollmachine-monitor defaults

# Disable auto-start
sudo update-rc.d rollmachine-monitor remove
```

### 🆘 Support

For issues or questions:
1. Check log files in `/opt/rollmachine-monitor/logs/`
2. Verify user is in dialout group: `groups $USER`
3. Check service status: `sudo /etc/init.d/rollmachine-monitor status`
4. Restart service: `sudo /etc/init.d/rollmachine-monitor restart`

### 📝 Changelog v1.2.6

- ✨ Added Port Management tab with kill/close, auto connect, disconnect features
- ✨ Enhanced settings dialog with tabbed interface
- ✨ Added decimal format selection (#, #.#, #.##)
- ✨ Added length tolerance and rounding settings
- ✨ Added conversion factor preview
- 🔧 Fixed all settings dialog buttons functionality
- 🔧 Improved error handling and validation
- 🧪 Added comprehensive test scripts
- 📚 Updated documentation and release notes

---

**Ready for Production Use on antiX! 🚀** 