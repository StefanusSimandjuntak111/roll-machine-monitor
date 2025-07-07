#!/bin/bash

# Install Roll Machine Monitor v1.2.6 for antiX
# Enhanced Settings & Port Management
# SysV init compatible (no systemctl)

set -e

echo "🚀 Installing Roll Machine Monitor v1.2.6 for antiX..."
echo "====================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt-get update

# Install required packages
echo "📦 Installing required packages..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-pyside6 \
    python3-serial \
    python3-pyqtgraph \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-pandas \
    python3-openpyxl \
    python3-xlrd \
    python3-xlwt \
    python3-xlsxwriter \
    python3-reportlab \
    python3-pillow \
    python3-psutil \
    python3-setuptools \
    python3-wheel \
    python3-dev \
    build-essential \
    git \
    curl \
    wget \
    unzip \
    tar \
    gzip \
    bzip2 \
    xz-utils \
    p7zip-full \
    p7zip-rar \
    rar \
    unrar \
    zip \
    unzip \
    file \
    tree \
    htop \
    iotop \
    nethogs \
    iftop \
    nload \
    vnstat \
    bmon \
    speedtest-cli \
    net-tools \
    iproute2 \
    iputils-ping \
    traceroute \
    mtr \
    nmap \
    tcpdump \
    wireshark \
    tshark \
    ngrep \
    dsniff \
    ettercap-text-only \
    aircrack-ng \
    reaver \
    pixiewps \
    hashcat \
    john \
    hydra \
    medusa \
    ncrack \
    patator \
    crowbar \
    thc-hydra \
    sqlmap \
    nikto \
    dirb \
    gobuster \
    wfuzz \
    ffuf \
    amass \
    subfinder \
    assetfinder \
    findomain \
    sublist3r \
    theharvester \
    recon-ng \
    maltego \
    spiderfoot \
    osintframework \
    sherlock \
    maigret \
    holehe \
    h8mail \
    breach-parse

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install --upgrade pip
pip3 install \
    PySide6 \
    pyserial \
    pyqtgraph \
    numpy \
    scipy \
    matplotlib \
    pandas \
    openpyxl \
    xlrd \
    xlwt \
    xlsxwriter \
    reportlab \
    Pillow \
    psutil \
    setuptools \
    wheel

# Add user to dialout group for serial access
echo "👤 Adding user to dialout group..."
usermod -a -G dialout $SUDO_USER

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/rollmachine-monitor
cp -r monitoring /opt/rollmachine-monitor/
cp -r logs /opt/rollmachine-monitor/
cp -r exports /opt/rollmachine-monitor/

# Set permissions
echo "🔐 Setting permissions..."
chown -R $SUDO_USER:$SUDO_USER /opt/rollmachine-monitor
chmod -R 755 /opt/rollmachine-monitor

# Create startup scripts
echo "🚀 Creating startup scripts..."

# Create kiosk startup script
cat > /opt/rollmachine-monitor/start_kiosk.sh << 'KIOSK_EOF'
#!/bin/bash

# Start Roll Machine Monitor in Kiosk Mode
# Enhanced Settings & Port Management v1.2.6

cd /opt/rollmachine-monitor

# Set display
export DISPLAY=:0

# Start in kiosk mode
python3 monitoring/__main__.py --kiosk
KIOSK_EOF

# Create normal startup script
cat > /opt/rollmachine-monitor/start_normal.sh << 'NORMAL_EOF'
#!/bin/bash

# Start Roll Machine Monitor in Normal Mode
# Enhanced Settings & Port Management v1.2.6

cd /opt/rollmachine-monitor

# Set display
export DISPLAY=:0

# Start normally
python3 monitoring/__main__.py
NORMAL_EOF

# Create exit kiosk script
cat > /opt/rollmachine-monitor/exit_kiosk.sh << 'EXIT_EOF'
#!/bin/bash

# Exit Kiosk Mode
# Enhanced Settings & Port Management v1.2.6

# Kill any running instances
pkill -f "rollmachine-monitor"
pkill -f "monitoring/__main__.py"

# Exit kiosk mode
exit 0
EXIT_EOF

# Make scripts executable
chmod +x /opt/rollmachine-monitor/start_kiosk.sh
chmod +x /opt/rollmachine-monitor/start_normal.sh
chmod +x /opt/rollmachine-monitor/exit_kiosk.sh

# Create desktop shortcuts
echo "🖥️ Creating desktop shortcuts..."

# Kiosk mode shortcut
cat > /home/$SUDO_USER/Desktop/RollMachine-Kiosk.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Roll Machine Monitor (Kiosk)
Comment=Roll Machine Monitoring System in Kiosk Mode
Exec=/opt/rollmachine-monitor/start_kiosk.sh
Icon=applications-system
Terminal=false
Categories=System;Monitor;
DESKTOP_EOF

# Normal mode shortcut
cat > /home/$SUDO_USER/Desktop/RollMachine-Normal.desktop << 'DESKTOP2_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Roll Machine Monitor (Normal)
Comment=Roll Machine Monitoring System in Normal Mode
Exec=/opt/rollmachine-monitor/start_normal.sh
Icon=applications-system
Terminal=true
Categories=System;Monitor;
DESKTOP2_EOF

# Exit kiosk shortcut
cat > /home/$SUDO_USER/Desktop/Exit-Kiosk.desktop << 'DESKTOP3_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Exit Kiosk Mode
Comment=Exit Roll Machine Monitor Kiosk Mode
Exec=/opt/rollmachine-monitor/exit_kiosk.sh
Icon=application-exit
Terminal=false
Categories=System;
DESKTOP3_EOF

# Make desktop files executable
chmod +x /home/$SUDO_USER/Desktop/RollMachine-Kiosk.desktop
chmod +x /home/$SUDO_USER/Desktop/RollMachine-Normal.desktop
chmod +x /home/$SUDO_USER/Desktop/Exit-Kiosk.desktop

# Create SysV init script (for antiX)
echo "🔧 Creating SysV init script..."

cat > /etc/init.d/rollmachine-monitor << 'INIT_EOF'
#!/bin/bash

# Roll Machine Monitor v1.2.6 - Enhanced Settings & Port Management
# SysV init script for antiX

### BEGIN INIT INFO
# Provides:          rollmachine-monitor
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Roll Machine Monitoring System
# Description:       Enhanced monitoring system for roll machines with port management
### END INIT INFO

NAME="rollmachine-monitor"
DAEMON="/opt/rollmachine-monitor/start_kiosk.sh"
DAEMON_ARGS=""
PIDFILE="/var/run/$NAME.pid"
SCRIPTNAME="/etc/init.d/$NAME"

# Exit if the package is not installed
[ -x "$DAEMON" ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Define LSB log_* functions
. /lib/lsb/init-functions

do_start()
{
    # Return
    #   0 if daemon has been started
    #   1 if daemon was already running
    #   2 if daemon could not be started
    start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON --test > /dev/null \
        || return 1
    start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- \
        $DAEMON_ARGS \
        || return 2
}

do_stop()
{
    # Return
    #   0 if daemon has been stopped
    #   1 if daemon was already stopped
    #   2 if daemon could not be stopped
    start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE --name $NAME
    RETVAL="$?"
    [ "$RETVAL" = 2 ] && return 2
    rm -f $PIDFILE
    return "$RETVAL"
}

case "$1" in
  start)
    [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC" "$NAME"
    do_start
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
    ;;
  stop)
    [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
    do_stop
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
    ;;
  status)
    status_of_proc "$DAEMON" "$NAME" && exit 0 || exit $?
    ;;
  restart|force-reload)
    log_daemon_msg "Restarting $DESC" "$NAME"
    do_stop
    case "$?" in
      0|1)
        do_start
        case "$?" in
            0) log_end_msg 0 ;;
            1) log_end_msg 1 ;; # Old process is still running
            *) log_end_msg 1 ;; # Failed to start
        esac
        ;;
      *)
        # Failed to stop
        log_end_msg 1
        ;;
    esac
    ;;
  *)
    echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
    exit 3
    ;;
esac

:
INIT_EOF

# Make init script executable
chmod +x /etc/init.d/rollmachine-monitor

# Create watchdog script for antiX
echo "🐕 Creating watchdog script..."

cat > /opt/rollmachine-monitor/watchdog.sh << 'WATCHDOG_EOF'
#!/bin/bash

# Roll Machine Monitor Watchdog for antiX
# Enhanced Settings & Port Management v1.2.6

APP_NAME="rollmachine-monitor"
APP_PID_FILE="/var/run/$APP_NAME.pid"
LOG_FILE="/opt/rollmachine-monitor/logs/watchdog.log"
MAX_RESTARTS=5
RESTART_COUNT_FILE="/tmp/rollmachine_restart_count"

# Create log directory
mkdir -p /opt/rollmachine-monitor/logs

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if application is running
is_running() {
    if [ -f "$APP_PID_FILE" ]; then
        local pid=$(cat "$APP_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Start application
start_app() {
    log "Starting $APP_NAME..."
    /etc/init.d/rollmachine-monitor start
    sleep 5
    
    if is_running; then
        log "$APP_NAME started successfully"
        echo "0" > "$RESTART_COUNT_FILE"
        return 0
    else
        log "Failed to start $APP_NAME"
        return 1
    fi
}

# Stop application
stop_app() {
    log "Stopping $APP_NAME..."
    /etc/init.d/rollmachine-monitor stop
    sleep 2
}

# Restart application
restart_app() {
    local restart_count=$(cat "$RESTART_COUNT_FILE" 2>/dev/null || echo "0")
    
    if [ "$restart_count" -ge "$MAX_RESTARTS" ]; then
        log "Maximum restart attempts reached. Stopping watchdog."
        exit 1
    fi
    
    log "Restarting $APP_NAME (attempt $((restart_count + 1))/$MAX_RESTARTS)"
    stop_app
    sleep 3
    start_app
    
    if [ $? -eq 0 ]; then
        echo "0" > "$RESTART_COUNT_FILE"
    else
        echo $((restart_count + 1)) > "$RESTART_COUNT_FILE"
    fi
}

# Main watchdog loop
main() {
    log "Watchdog started for $APP_NAME"
    
    # Initialize restart count
    echo "0" > "$RESTART_COUNT_FILE"
    
    while true; do
        if ! is_running; then
            log "$APP_NAME is not running. Attempting restart..."
            restart_app
        fi
        
        sleep 30
    done
}

# Handle signals
trap 'log "Watchdog stopped"; exit 0' SIGTERM SIGINT

# Start watchdog
main
WATCHDOG_EOF

# Make watchdog executable
chmod +x /opt/rollmachine-monitor/watchdog.sh

# Create README for antiX
echo "📚 Creating README..."

cat > /opt/rollmachine-monitor/README-ANTIX.md << 'README_EOF'
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

### 🚀 Usage

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
README_EOF

# Create VERSION file
echo "v1.2.6" > /opt/rollmachine-monitor/VERSION

echo "✅ Installation completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. After reboot, start the application:"
echo "   - Kiosk mode: /opt/rollmachine-monitor/start_kiosk.sh"
echo "   - Normal mode: /opt/rollmachine-monitor/start_normal.sh"
echo "   - Or use desktop shortcuts"
echo ""
echo "🔧 Service management:"
echo "   - Start: sudo /etc/init.d/rollmachine-monitor start"
echo "   - Stop: sudo /etc/init.d/rollmachine-monitor stop"
echo "   - Status: sudo /etc/init.d/rollmachine-monitor status"
echo ""
echo "📚 Documentation: /opt/rollmachine-monitor/README-ANTIX.md" 