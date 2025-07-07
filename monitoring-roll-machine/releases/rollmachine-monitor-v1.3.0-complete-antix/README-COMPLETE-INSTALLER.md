# Roll Machine Monitor v1.3.0 - Complete All-in-One Installer

🎉 **The Ultimate Installation Experience for antiX Linux!**

This package provides a **complete automated installer** that sets up everything in a single command. No more manual dependency installation, configuration, or setup steps!

## 🚀 What Makes This Special?

### ✅ **ONE COMMAND INSTALLS EVERYTHING**
```bash
sudo ./install-complete-antix.sh
```

### ✅ **ZERO MANUAL CONFIGURATION**
- Automatically installs all system dependencies
- Creates Python virtual environment with all requirements
- Sets up desktop shortcuts (regular + kiosk mode)
- Configures SysV init scripts (antiX compatible, no systemd)
- Creates dedicated kiosk user
- Sets up automatic monitoring and restart

### ✅ **OFFLINE INSTALLATION SUPPORT**
- Can create offline installation packages
- No internet required on target machines
- All dependencies bundled

### ✅ **UPDATE-SAFE**
- Preserves your settings and data during updates
- Automatic backup and restore of configuration

## 📦 Package Contents

```
rollmachine-monitor-v1.3.0-complete-antix/
├── install-complete-antix.sh          # 🎯 MAIN INSTALLER (run this!)
├── install-offline-bundle.sh          # 📦 Creates offline package
├── deploy-to-antix.sh                 # 🚀 Simple deployment helper
├── monitoring-roll-machine/           # 📱 Complete application
│   ├── monitoring/                    # Core application code
│   ├── requirements.txt               # Python dependencies
│   └── run_app.py                     # Application launcher
├── logs/                              # 📝 System logs directory
├── exports/                           # 💾 Data exports directory
├── README.md                          # 📖 Application documentation
├── INSTALL_GUIDE.md                   # 📋 Installation guide
├── RELEASE_NOTES_v1.3.0.md           # 📄 Release notes
└── VERSION                            # 🏷️ Version information
```

## 🏁 Quick Start (3 Steps)

### 1. **Transfer to antiX System**
Copy this entire folder to your antiX machine.

### 2. **Run Installer**
```bash
cd rollmachine-monitor-v1.3.0-complete-antix
sudo ./install-complete-antix.sh
```

### 3. **Done!**
The application is installed and ready to use with:
- Desktop shortcuts
- Auto-start service
- Kiosk mode available

## 🔄 Installation Options

### 🆕 **Fresh Installation** (Default)
```bash
sudo ./install-complete-antix.sh
```
Installs everything from scratch.

### 🔄 **Update Existing Installation**
```bash
sudo ./install-complete-antix.sh --update
```
Updates application while preserving your settings and data.

### 📦 **Offline Installation**
```bash
# On a machine WITH internet - create offline package
./install-offline-bundle.sh

# Transfer the created package to target machine
# Extract and install offline
tar -xzf rollmachine-monitor-v1.3.0-offline-antix.tar.gz
cd rollmachine-monitor-v1.3.0-offline-antix
sudo ./install-offline.sh
```

## ✨ What Gets Installed Automatically

### 🔧 **System Level**
- All required Linux packages (Python, Qt, serial libraries, etc.)
- SysV init scripts (perfect for antiX - no systemd dependency)
- Auto-start service configuration
- System users and permissions

### 🐍 **Python Environment**
- Isolated virtual environment in `/opt/rollmachine-monitor/venv/`
- All Python dependencies (PySide6, pyserial, etc.)
- No conflicts with system Python

### 🖥️ **Desktop Integration**
- Application shortcuts on all user desktops
- Menu entries for easy access
- Separate shortcuts for regular and kiosk modes
- Professional application icon

### 👤 **Kiosk Mode Setup**
- Dedicated `kiosk` user (username: kiosk, password: kiosk123)
- Auto-login configuration
- Fullscreen kiosk mode
- Auto-start on kiosk user login

### 🔄 **Monitoring & Reliability**
- Watchdog process (monitors and restarts if crashed)
- Cron-based monitoring (every minute)
- Comprehensive logging
- Automatic error recovery

## 🖥️ After Installation

### **Starting the Application**

#### From Desktop
- Look for "Roll Machine Monitor" icon on desktop
- Or "Roll Machine Monitor (Kiosk)" for fullscreen mode

#### From Command Line
```bash
# Regular mode
/opt/rollmachine-monitor/start-rollmachine.sh

# Kiosk mode  
/opt/rollmachine-monitor/start-rollmachine-kiosk.sh
```

#### As System Service
```bash
sudo /etc/init.d/rollmachine-monitor start    # Start
sudo /etc/init.d/rollmachine-monitor stop     # Stop
sudo /etc/init.d/rollmachine-monitor status   # Check status
sudo /etc/init.d/rollmachine-monitor restart  # Restart
```

### **Kiosk Mode**
For dedicated kiosk operation:
1. Log out of current user
2. Log in as `kiosk` (password: kiosk123)
3. Application starts automatically in fullscreen mode

## 📁 Installation Locations

- **Main Installation**: `/opt/rollmachine-monitor/`
- **Application Code**: `/opt/rollmachine-monitor/monitoring-roll-machine/`
- **Python Environment**: `/opt/rollmachine-monitor/venv/`
- **Logs**: `/opt/rollmachine-monitor/logs/`
- **Data Exports**: `/opt/rollmachine-monitor/exports/`
- **Service Script**: `/etc/init.d/rollmachine-monitor`
- **Desktop Shortcuts**: `/usr/share/applications/` and user desktops

## 🔧 Troubleshooting

### **Application Won't Start**
```bash
# Check logs
tail -f /opt/rollmachine-monitor/logs/startup.log

# Check service
sudo /etc/init.d/rollmachine-monitor status

# Restart everything
sudo /etc/init.d/rollmachine-monitor restart
```

### **Serial Port Issues**
```bash
# List available ports
ls -la /dev/ttyUSB* /dev/ttyACM*

# Check user permissions
groups $USER

# Add user to dialout group (logout/login after)
sudo usermod -a -G dialout $USER
```

### **Permission Problems**
```bash
# Reset all permissions
sudo chown -R root:root /opt/rollmachine-monitor
sudo chmod -R 755 /opt/rollmachine-monitor
sudo chmod 777 /opt/rollmachine-monitor/{logs,exports}
```

## 🔍 Verification

After installation, verify everything works:

```bash
# 1. Check installation
ls -la /opt/rollmachine-monitor/

# 2. Check service
sudo /etc/init.d/rollmachine-monitor status

# 3. Test application
/opt/rollmachine-monitor/start-rollmachine.sh

# 4. Check desktop shortcuts
ls -la ~/Desktop/rollmachine-monitor*.desktop

# 5. Test kiosk user
su - kiosk  # password: kiosk123
```

## 🏆 Why This Installer is Better

### **Previous Problems (SOLVED!)**
- ❌ Manual dependency installation
- ❌ Python environment conflicts  
- ❌ Missing desktop shortcuts
- ❌ Complex service setup
- ❌ No offline installation
- ❌ Difficult updates

### **Now With v1.3.0**
- ✅ **Everything automated**
- ✅ **Isolated environment**
- ✅ **Desktop integration**
- ✅ **SysV init scripts**
- ✅ **Offline support**
- ✅ **Safe updates**

## 🎯 Perfect For

- **Industrial Environments**: Reliable kiosk deployment
- **IT Departments**: Easy mass deployment  
- **End Users**: Simple one-command installation
- **Offline Sites**: No internet dependency after setup
- **antiX Users**: Optimized for antiX Linux specifically

## 📞 Support

- **Logs**: Check `/opt/rollmachine-monitor/logs/` first
- **Service**: Use `/etc/init.d/rollmachine-monitor status`
- **Connection**: Verify JSK3588 device and serial port
- **Permissions**: Ensure user is in `dialout` group

---

## 🎉 Ready to Install?

```bash
sudo ./install-complete-antix.sh
```

**That's it!** Everything else is automatic. 

The installer will guide you through the process and show you exactly what it's doing. In just a few minutes, you'll have a fully functional Roll Machine Monitor system with desktop shortcuts, kiosk mode, and automatic monitoring.

**For updates**: `sudo ./install-complete-antix.sh --update`

**For offline installation**: `./install-offline-bundle.sh` (create package first)

---

**🚀 The most complete and user-friendly Roll Machine Monitor installation experience ever created!** 