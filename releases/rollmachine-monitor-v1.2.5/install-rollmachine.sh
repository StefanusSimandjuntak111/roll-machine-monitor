#!/bin/bash
# Roll Machine Monitor - Simple Installer Script
# Works on Ubuntu/Debian without requiring .deb format

set -e

# Configuration
APP_NAME="rollmachine-monitor"
VERSION="1.0.0"
INSTALL_DIR="/opt/$APP_NAME"
BIN_FILE="/usr/local/bin/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Roll Machine Monitor Installer v$VERSION"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This installer must be run as root"
    echo "   Please run: sudo $0"
    exit 1
fi

echo "📋 Checking system requirements..."

# Check if this is Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "❌ This installer requires Ubuntu/Debian (apt-get not found)"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python 3..."
    apt update
    apt install -y python3 python3-pip python3-venv python3-dev
fi

echo "📦 Installing system dependencies..."
apt update
apt install -y \
    python3 python3-pip python3-venv python3-dev \
    libgl1-mesa-glx libglib2.0-0 \
    libxkbcommon-x11-0 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libfontconfig1 \
    libdbus-1-3 \
    libxcb-cursor0 libxcb-cursor-dev \
    qtbase5-dev qt5-qmake \
    libxcb1-dev libxcb-glx0-dev \
    libx11-xcb1 libxcb-util1 \
    libxcb-shape0-dev libxcb-xfixes0-dev \
    libegl1-mesa-dev libdrm2 \
    x11-utils xauth xvfb \
    openbox unclutter x11-xserver-utils

# Try to install kivy-garden, but don't fail if not available
echo "📦 Installing Kivy dependencies..."
apt install -y kivy-garden 2>/dev/null || echo "⚠️  kivy-garden not available in repository - will install via pip"

# Install clipboard tools for Kivy
echo "📦 Installing clipboard tools..."
apt install -y xclip xsel 2>/dev/null || echo "⚠️  xclip/xsel not available - clipboard may not work"

# Stop any running instances
echo "🛑 Stopping any running instances..."
pkill -f "$APP_NAME" || true

# Remove old installation
if [ -d "$INSTALL_DIR" ]; then
    echo "🗑️  Removing old installation..."
    rm -rf "$INSTALL_DIR"
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Check if monitoring-roll-machine directory exists
if [ ! -d "$SCRIPT_DIR/monitoring-roll-machine" ]; then
    echo "❌ Application files not found!"
    echo "   Please ensure this script is in the same directory as 'monitoring-roll-machine' folder"
    exit 1
fi

# Copy application files
echo "📦 Copying application files..."
cp -r "$SCRIPT_DIR/monitoring-roll-machine" "$INSTALL_DIR/"

# Copy config files if they exist
if [ -f "$SCRIPT_DIR/config.json" ]; then
    cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"
    echo "   Copied config.json"
fi

# Create requirements.txt
echo "📄 Creating requirements.txt..."
cat > "$INSTALL_DIR/requirements.txt" << 'EOF'
# PRIMARY UI Framework (PySide6 - Stable & Perfect Design)
PySide6>=6.6.0
pyqtgraph>=0.13.3

# Serial Communication
pyserial>=3.5

# Config & Environment
python-dotenv>=1.0.0
pyyaml>=6.0.1
appdirs>=1.4.4

# Web requests and QR code
requests>=2.31.0
qrcode>=7.4.2
Pillow>=10.0.0

# Alternative UI Framework (Optional - May Fail on Some Systems)
Kivy>=2.1.0
KivyMD>=1.1.1
kivy-garden>=0.1.5
EOF

# Create virtual environment and install dependencies
echo "🐍 Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install dependencies - PySide6 FIRST (priority)
echo "📦 Installing core Python dependencies (PySide6 - primary UI)..."
pip install PySide6>=6.6.0 pyqtgraph>=0.13.3 pyserial>=3.5 python-dotenv>=1.0.0 pyyaml>=6.0.1 appdirs>=1.4.4 requests>=2.31.0 qrcode>=7.4.2 Pillow>=10.0.0

# Install remaining requirements with fallback
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt || {
    echo "⚠️  Some optional packages failed, continuing with core functionality..."
    
    # Try Kivy packages separately (optional only)
    echo "📦 Installing Kivy packages (optional for alternative UI)..."
    pip install Kivy>=2.1.0 || echo "ℹ️  Kivy not installed - using PySide6 (recommended)"
    pip install KivyMD>=1.1.1 || echo "ℹ️  KivyMD not installed - using PySide6 (recommended)"
    pip install kivy-garden>=0.1.5 || echo "ℹ️  kivy-garden not installed - not needed for PySide6"
}

# Create startup script
echo "📝 Creating startup script..."
cat > "$BIN_FILE" << EOF
#!/bin/bash
# Roll Machine Monitor startup script

INSTALL_DIR="$INSTALL_DIR"
VENV_PYTHON="\$INSTALL_DIR/venv/bin/python"
APP_DIR="\$INSTALL_DIR/monitoring-roll-machine"

# Check if virtual environment exists
if [ ! -d "\$INSTALL_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please reinstall the application."
    exit 1
fi

# Check if application directory exists
if [ ! -d "\$APP_DIR" ]; then
    echo "❌ Application directory not found. Please reinstall the application."
    exit 1
fi

# Change to application directory and run
cd "\$APP_DIR"
exec "\$VENV_PYTHON" -m monitoring
EOF

chmod +x "$BIN_FILE"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Roll Machine Monitor
Comment=Fabric Roll Machine Monitoring Application
Icon=applications-engineering
Exec=$BIN_FILE
Categories=Office;Engineering;
Terminal=false
StartupNotify=true
Keywords=monitoring;machine;textile;fabric;roll;
EOF

# Set permissions
echo "🔐 Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod +x "$BIN_FILE"

# Make config files writable by all users
chmod 666 "$INSTALL_DIR/monitoring-roll-machine/monitoring/config.json" 2>/dev/null || true
chmod 777 "$INSTALL_DIR/monitoring-roll-machine/logs" 2>/dev/null || true
chmod 777 "$INSTALL_DIR/monitoring-roll-machine/exports" 2>/dev/null || true

# Create a rollmachine group and add users to it
groupadd -f rollmachine
if [ -n "$SUDO_USER" ]; then
    usermod -a -G rollmachine "$SUDO_USER"
fi

# Set group ownership for writable directories
chgrp -R rollmachine "$INSTALL_DIR/monitoring-roll-machine/monitoring" 2>/dev/null || true
chgrp -R rollmachine "$INSTALL_DIR/monitoring-roll-machine/logs" 2>/dev/null || true  
chgrp -R rollmachine "$INSTALL_DIR/monitoring-roll-machine/exports" 2>/dev/null || true
chmod -R g+w "$INSTALL_DIR/monitoring-roll-machine/monitoring" 2>/dev/null || true
chmod -R g+w "$INSTALL_DIR/monitoring-roll-machine/logs" 2>/dev/null || true
chmod -R g+w "$INSTALL_DIR/monitoring-roll-machine/exports" 2>/dev/null || true

# Add user to dialout group for serial access
echo "👤 Adding users to dialout group..."
if [ -n "$SUDO_USER" ]; then
    usermod -a -G dialout "$SUDO_USER" || true
    echo "   User $SUDO_USER added to dialout group"
else
    echo "   Run manually: sudo usermod -a -G dialout \$USER"
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

# Ask if user wants kiosk mode setup
echo
read -p "🖥️  Do you want to setup KIOSK MODE? (y/N): " -r setup_kiosk
echo

if [[ $setup_kiosk =~ ^[Yy]$ ]]; then
    echo "🔧 Setting up KIOSK MODE..."
    
    # Create kiosk user if doesn't exist
    if ! id "kiosk" &>/dev/null; then
        echo "👤 Creating kiosk user..."
        useradd -m -s /bin/bash kiosk
        usermod -a -G rollmachine,dialout kiosk
    fi
    
    # Copy kiosk scripts to install directory
    if [ -f "$SCRIPT_DIR/kiosk-startup.sh" ]; then
        cp "$SCRIPT_DIR/kiosk-startup.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/kiosk-startup.sh"
    fi
    
    if [ -f "$SCRIPT_DIR/watchdog.sh" ]; then
        cp "$SCRIPT_DIR/watchdog.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/watchdog.sh"
    fi
    
    if [ -f "$SCRIPT_DIR/antix-startup.sh" ]; then
        cp "$SCRIPT_DIR/antix-startup.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/antix-startup.sh"
    fi
    
    if [ -f "$SCRIPT_DIR/antix-init.sh" ]; then
        cp "$SCRIPT_DIR/antix-init.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/antix-init.sh"
    fi
    
    if [ -f "$SCRIPT_DIR/antix-watchdog.sh" ]; then
        cp "$SCRIPT_DIR/antix-watchdog.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/antix-watchdog.sh"
    fi
    
    # Create systemd service files
    echo "⚙️  Creating systemd services..."
    
    # Kiosk service
    cat > "/etc/systemd/system/rollmachine-kiosk.service" << 'EOF'
[Unit]
Description=Roll Machine Monitor Kiosk Mode
Documentation=https://github.com/rollmachine/monitor
After=network.target graphical-session.target
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=kiosk
Group=rollmachine
WorkingDirectory=/opt/rollmachine-monitor
ExecStart=/opt/rollmachine-monitor/kiosk-startup.sh
ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID

# Environment variables
Environment=DISPLAY=:0
Environment=HOME=/home/kiosk
Environment=XDG_RUNTIME_DIR=/run/user/1000

# Restart configuration - NEVER GIVE UP!
Restart=always
RestartSec=3
StartLimitBurst=0

# Security settings for kiosk
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/opt/rollmachine-monitor /var/log /tmp
CapabilityBoundingSet=

# Process settings
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
TimeoutStartSec=60

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rollmachine-kiosk

[Install]
WantedBy=graphical.target
Also=rollmachine-watchdog.service
EOF
    
    # Watchdog service
    cat > "/etc/systemd/system/rollmachine-watchdog.service" << 'EOF'
[Unit]
Description=Roll Machine Monitor Watchdog
Documentation=https://github.com/rollmachine/monitor
After=rollmachine-kiosk.service
BindsTo=rollmachine-kiosk.service

[Service]
Type=simple
User=root
ExecStart=/opt/rollmachine-monitor/watchdog.sh
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rollmachine-watchdog

[Install]
WantedBy=graphical.target
EOF
    
    # Check if systemd is available
    if command -v systemctl >/dev/null 2>&1; then
        echo "⚙️  Enabling systemd services..."
        systemctl daemon-reload
        systemctl enable rollmachine-kiosk.service
        systemctl enable rollmachine-watchdog.service
    else
        echo "⚙️  Setting up AntiX auto-start (no systemd)..."
        
        # Setup init script
        if [ -f "$INSTALL_DIR/antix-init.sh" ]; then
            cp "$INSTALL_DIR/antix-init.sh" "/etc/init.d/rollmachine-monitor"
            chmod +x "/etc/init.d/rollmachine-monitor"
            
            # Add to runlevels
            if command -v update-rc.d >/dev/null 2>&1; then
                update-rc.d rollmachine-monitor defaults
                echo "   Init script enabled for auto-start"
            elif command -v chkconfig >/dev/null 2>&1; then
                chkconfig --add rollmachine-monitor
                chkconfig rollmachine-monitor on
                echo "   Init script enabled for auto-start"
            else
                echo "   Manual: Add to runlevels manually"
            fi
        fi
        
        # Setup cron watchdog
        if [ -f "$INSTALL_DIR/antix-watchdog.sh" ]; then
            echo "⚙️  Setting up cron watchdog..."
            # Add cron job for watchdog (every minute)
            (crontab -l 2>/dev/null; echo "* * * * * /opt/rollmachine-monitor/antix-watchdog.sh >/dev/null 2>&1") | crontab -
            echo "   Cron watchdog enabled (every minute)"
        fi
        
        # Setup user autostart
        echo "⚙️  Setting up user autostart..."
        if [ -n "$SUDO_USER" ]; then
            user_home="/home/$SUDO_USER"
            if [ -d "$user_home" ]; then
                mkdir -p "$user_home/.config/autostart"
                cat > "$user_home/.config/autostart/rollmachine-autostart.desktop" << 'AUTOSTART_EOF'
[Desktop Entry]
Type=Application
Name=Roll Machine Monitor Auto Start
Exec=/etc/init.d/rollmachine-monitor start
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Auto-start Roll Machine Monitor
AUTOSTART_EOF
                chown "$SUDO_USER:$SUDO_USER" "$user_home/.config/autostart/rollmachine-autostart.desktop"
                echo "   User autostart configured"
            fi
        fi
    fi
    
    # Create autostart for antiX
    echo "🚀 Setting up autostart..."
    mkdir -p /home/kiosk/.config/autostart
    cat > "/home/kiosk/.config/autostart/rollmachine-kiosk.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Roll Machine Monitor Kiosk
Exec=sudo systemctl start rollmachine-kiosk
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Start Roll Machine Monitor in kiosk mode
EOF
    chown -R kiosk:kiosk /home/kiosk/.config
    
    # Create sudo rule for kiosk user
    if command -v systemctl >/dev/null 2>&1; then
        echo "kiosk ALL=(ALL) NOPASSWD: /bin/systemctl start rollmachine-kiosk, /bin/systemctl stop rollmachine-kiosk, /bin/systemctl restart rollmachine-kiosk" > /etc/sudoers.d/rollmachine-kiosk
    else
        echo "kiosk ALL=(ALL) NOPASSWD: /opt/rollmachine-monitor/kiosk-startup.sh, /bin/pkill -f rollmachine" > /etc/sudoers.d/rollmachine-kiosk
    fi
    
    echo "✅ KIOSK MODE setup completed!"
    echo
    if command -v systemctl >/dev/null 2>&1; then
        echo "🎯 Kiosk Mode Commands (Systemd):"
        echo "   Start:   sudo systemctl start rollmachine-kiosk"
        echo "   Stop:    sudo systemctl stop rollmachine-kiosk"
        echo "   Status:  sudo systemctl status rollmachine-kiosk"
        echo "   Logs:    sudo journalctl -u rollmachine-kiosk -f"
        echo
        echo "🔄 Auto-start: Services will start automatically on boot"
    else
        echo "🎯 Kiosk Mode Commands (AntiX/Init Script):"
        echo "   Start:   sudo /etc/init.d/rollmachine-monitor start"
        echo "   Stop:    sudo /etc/init.d/rollmachine-monitor stop"
        echo "   Restart: sudo /etc/init.d/rollmachine-monitor restart"
        echo "   Status:  sudo /etc/init.d/rollmachine-monitor status"
        echo "   Logs:    tail -f /var/log/rollmachine-monitor-init.log"
        echo
        echo "🔄 Auto-start: Enabled via init script and cron watchdog"
        echo "   Boot:     Init script will start on boot"
        echo "   Monitor:  Cron watchdog checks every minute"
        echo "   User:     Autostart desktop entry configured"
    fi
    echo
    echo "🖥️  UI Framework: PySide6 (primary, stable, perfect design)"
    echo "   Kiosk features: Fullscreen, cannot close, auto-restart"
    echo
fi

echo
echo "✅ Installation completed successfully!"
echo
echo "📱 To run the application:"
echo "   $APP_NAME"
echo
echo "🖥️  Or find 'Roll Machine Monitor' in your applications menu"
echo
if [[ $setup_kiosk =~ ^[Yy]$ ]]; then
echo "🎯 KIOSK MODE enabled:"
echo "   Start kiosk: sudo systemctl start rollmachine-kiosk"
echo "   View logs:   sudo journalctl -u rollmachine-kiosk -f"
echo "   Auto-start:  Will start automatically on boot"
echo
fi
echo "⚠️  Important: Logout and login again for serial port access"
echo
echo "🔧 Troubleshooting:"
echo "   - Check logs: journalctl -f"
echo "   - Verify serial port: ls /dev/ttyUSB* /dev/ttyACM*"
echo "   - Add user to dialout: sudo usermod -a -G dialout \$USER"
if [[ $setup_kiosk =~ ^[Yy]$ ]]; then
echo "   - Kiosk logs: sudo journalctl -u rollmachine-kiosk -f"
echo "   - Watchdog logs: sudo journalctl -u rollmachine-watchdog -f"
fi
echo

# Create uninstaller
echo "📄 Creating uninstaller..."
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# Roll Machine Monitor Uninstaller

set -e

APP_NAME="rollmachine-monitor"
INSTALL_DIR="/opt/$APP_NAME"
BIN_FILE="/usr/local/bin/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"

echo "🗑️  Uninstalling Roll Machine Monitor..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Stop running instances
pkill -f "$APP_NAME" || true

# Stop and disable kiosk services
systemctl stop rollmachine-kiosk.service 2>/dev/null || true
systemctl stop rollmachine-watchdog.service 2>/dev/null || true
systemctl disable rollmachine-kiosk.service 2>/dev/null || true
systemctl disable rollmachine-watchdog.service 2>/dev/null || true

# Remove systemd service files
[ -f "/etc/systemd/system/rollmachine-kiosk.service" ] && rm -f "/etc/systemd/system/rollmachine-kiosk.service"
[ -f "/etc/systemd/system/rollmachine-watchdog.service" ] && rm -f "/etc/systemd/system/rollmachine-watchdog.service"

# Remove kiosk autostart
[ -f "/home/kiosk/.config/autostart/rollmachine-kiosk.desktop" ] && rm -f "/home/kiosk/.config/autostart/rollmachine-kiosk.desktop"

# Remove sudo rule
[ -f "/etc/sudoers.d/rollmachine-kiosk" ] && rm -f "/etc/sudoers.d/rollmachine-kiosk"

# Reload systemd
systemctl daemon-reload 2>/dev/null || true

# Remove files
[ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR"
[ -f "$BIN_FILE" ] && rm -f "$BIN_FILE"
[ -f "$DESKTOP_FILE" ] && rm -f "$DESKTOP_FILE"

# Update desktop database
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database /usr/share/applications || true

echo "✅ Uninstallation completed!"
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"

echo "📄 Uninstaller created at: $INSTALL_DIR/uninstall.sh"
echo "   To uninstall: sudo $INSTALL_DIR/uninstall.sh"
echo

exit 0 