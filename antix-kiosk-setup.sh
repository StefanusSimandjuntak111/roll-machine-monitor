#!/bin/bash
# AntiX Kiosk Setup for Roll Machine Monitor
# Specialized setup for antiX Linux systems

set -e

echo "========================================"
echo "AntiX Kiosk Setup for Roll Machine Monitor"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "   Please run: sudo $0"
    exit 1
fi

# Check if this is antiX
if ! grep -q "antiX" /etc/os-release 2>/dev/null; then
    echo "⚠️  This script is optimized for antiX Linux"
    echo "   It may work on other Debian-based systems"
fi

echo "🔧 Setting up AntiX Kiosk Mode..."

# Install antiX-specific dependencies
echo "📦 Installing antiX dependencies..."
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
    openbox unclutter x11-xserver-utils \
    fluxbox icewm 2>/dev/null || true

# Create kiosk user if doesn't exist
if ! id "kiosk" &>/dev/null; then
    echo "👤 Creating kiosk user..."
    useradd -m -s /bin/bash kiosk
    usermod -a -G dialout kiosk
    echo "kiosk:kiosk123" | chpasswd
    echo "   Created kiosk user with password: kiosk123"
fi

# Setup antiX autostart
echo "🚀 Setting up antiX autostart..."
mkdir -p /home/kiosk/.config/autostart
mkdir -p /home/kiosk/.fluxbox
mkdir -p /home/kiosk/.icewm

# Create fluxbox startup script
cat > "/home/kiosk/.fluxbox/startup" << 'EOF'
#!/bin/bash
# Fluxbox startup script for kiosk mode

# Disable screen saver
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 1 -root &

# Start roll machine monitor
sleep 2
/opt/rollmachine-monitor/kiosk-startup.sh &

# Keep fluxbox running
exec fluxbox
EOF

# Create icewm startup script
cat > "/home/kiosk/.icewm/startup" << 'EOF'
#!/bin/bash
# IceWM startup script for kiosk mode

# Disable screen saver
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 1 -root &

# Start roll machine monitor
sleep 2
/opt/rollmachine-monitor/kiosk-startup.sh &

# Keep icewm running
exec icewm
EOF

# Create autostart entry
cat > "/home/kiosk/.config/autostart/rollmachine-kiosk.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Roll Machine Monitor Kiosk
Exec=/opt/rollmachine-monitor/kiosk-startup.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Start Roll Machine Monitor in kiosk mode
EOF

# Set permissions
chown -R kiosk:kiosk /home/kiosk/.config
chown -R kiosk:kiosk /home/kiosk/.fluxbox
chown -R kiosk:kiosk /home/kiosk/.icewm
chmod +x /home/kiosk/.fluxbox/startup
chmod +x /home/kiosk/.icewm/startup

# Create systemd service for antiX
echo "⚙️  Creating systemd services..."
cat > "/etc/systemd/system/rollmachine-antix.service" << 'EOF'
[Unit]
Description=Roll Machine Monitor AntiX Kiosk
Documentation=https://github.com/rollmachine/monitor
After=network.target
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=kiosk
Group=kiosk
WorkingDirectory=/opt/rollmachine-monitor
ExecStartPre=/bin/bash -c "startx /opt/rollmachine-monitor/kiosk-startup.sh -- :99 -screen 0 1920x1080x24 -ac +extension GLX +extension RANDR +extension RENDER"
ExecStart=/opt/rollmachine-monitor/kiosk-startup.sh
ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID

# Environment variables
Environment=DISPLAY=:99
Environment=HOME=/home/kiosk
Environment=XDG_RUNTIME_DIR=/run/user/1000

# Restart configuration
Restart=always
RestartSec=5
StartLimitBurst=0

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/opt/rollmachine-monitor /var/log /tmp /home/kiosk
CapabilityBoundingSet=

# Process settings
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
TimeoutStartSec=60

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rollmachine-antix

[Install]
WantedBy=multi-user.target
EOF

# Create simple startup script for antiX
cat > "/opt/rollmachine-monitor/antix-startup.sh" << 'EOF'
#!/bin/bash
# AntiX-specific startup script

set -e

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
VENV_PYTHON="/opt/rollmachine-monitor/venv/bin/python"
LOG_FILE="/var/log/rollmachine-antix.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ANTIX] $1" | tee -a "$LOG_FILE"
}

# Setup display
export DISPLAY=${DISPLAY:-:99}
export QT_QPA_PLATFORM=xcb

# Disable screen saver
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

# Hide cursor
unclutter -idle 1 -root &>/dev/null &

log_message "Starting AntiX kiosk mode..."

cd "$APP_DIR"

# Run the application with fallback
if [ -f "$VENV_PYTHON" ]; then
    # Try Kivy kiosk first
    if python3 -c "import kivy" 2>/dev/null; then
        log_message "Using Kivy kiosk mode"
        exec "$VENV_PYTHON" -c "
import sys
import os
sys.path.insert(0, os.getcwd())

from kivy.config import Config
Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'resizable', '0')

from monitoring.ui.kiosk_ui import MonitoringKioskApp
MonitoringKioskApp().run()
"
    else
        # Fallback to PySide6
        log_message "Using PySide6 fallback mode"
        exec "$VENV_PYTHON" -m monitoring
    fi
else
    log_message "ERROR: Python virtual environment not found"
    exit 1
fi
EOF

chmod +x "/opt/rollmachine-monitor/antix-startup.sh"

# Enable services
systemctl daemon-reload
systemctl enable rollmachine-antix.service

# Create sudo rule
echo "kiosk ALL=(ALL) NOPASSWD: /bin/systemctl start rollmachine-antix, /bin/systemctl stop rollmachine-antix, /bin/systemctl restart rollmachine-antix" > /etc/sudoers.d/rollmachine-antix

echo "✅ AntiX Kiosk setup completed!"
echo
echo "🎯 AntiX Kiosk Commands:"
echo "   Start:   sudo systemctl start rollmachine-antix"
echo "   Stop:    sudo systemctl stop rollmachine-antix"
echo "   Status:  sudo systemctl status rollmachine-antix"
echo "   Logs:    sudo journalctl -u rollmachine-antix -f"
echo
echo "🖥️  Manual start:"
echo "   su - kiosk"
echo "   startx /opt/rollmachine-monitor/antix-startup.sh -- :99"
echo
echo "🔄 Auto-start: Service will start automatically on boot"
echo
echo "📝 Notes:"
echo "   - Kiosk user password: kiosk123"
echo "   - Uses virtual display :99 for headless operation"
echo "   - Compatible with Fluxbox and IceWM"
echo 