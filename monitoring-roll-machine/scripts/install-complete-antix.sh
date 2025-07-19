#!/bin/bash

# ===============================================
# Roll Machine Monitor Complete Installer v1.3.0
# All-in-One Installer for antiX Linux
# ===============================================
# 
# This installer does EVERYTHING in one run:
# ✅ Installs all system dependencies
# ✅ Creates Python virtual environment
# ✅ Installs all Python requirements
# ✅ Sets up application directories
# ✅ Creates desktop shortcuts (user + kiosk)
# ✅ Sets up SysV init scripts (no systemd)
# ✅ Configures auto-start and watchdog
# ✅ Supports install and update modes
#
# Usage: sudo ./install-complete-antix.sh [--update]
#

set -e

VERSION="1.3.0"
APP_NAME="Roll Machine Monitor"
INSTALL_DIR="/opt/rollmachine-monitor"
SERVICE_NAME="rollmachine-monitor"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Update mode flag
UPDATE_MODE=false
if [[ "$1" == "--update" ]]; then
    UPDATE_MODE=true
fi

print_header() {
    echo
    echo "================================================="
    echo -e "${BLUE}🚀 ${APP_NAME} Complete Installer v${VERSION}${NC}"
    echo "================================================="
    echo
    if [ "$UPDATE_MODE" = true ]; then
        echo -e "${YELLOW}🔄 UPDATE MODE - Preserving existing configuration${NC}"
    else
        echo -e "${GREEN}📦 FRESH INSTALLATION MODE${NC}"
    fi
    echo
}

log_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This installer must be run as root"
        echo "Please run: sudo $0"
        exit 1
    fi
}

check_antix() {
    if grep -q "antiX" /etc/os-release 2>/dev/null; then
        log_info "Detected antiX Linux - optimizing for your system"
    else
        log_warning "This installer is optimized for antiX Linux"
        log_warning "It may work on other Debian-based systems, but some features may differ"
        echo
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 1
        fi
    fi
}

backup_existing() {
    if [ "$UPDATE_MODE" = true ] && [ -d "$INSTALL_DIR" ]; then
        log_info "Creating backup of existing installation..."
        
        # Backup config files
        if [ -f "$INSTALL_DIR/monitoring-roll-machine/monitoring/config.json" ]; then
            cp "$INSTALL_DIR/monitoring-roll-machine/monitoring/config.json" "/tmp/rollmachine-config-backup.json"
            log_info "Backed up configuration to /tmp/rollmachine-config-backup.json"
        fi
        
        # Backup exports
        if [ -d "$INSTALL_DIR/monitoring-roll-machine/exports" ]; then
            cp -r "$INSTALL_DIR/monitoring-roll-machine/exports" "/tmp/rollmachine-exports-backup"
            log_info "Backed up exports to /tmp/rollmachine-exports-backup"
        fi
        
        # Stop running services
        if [ -f "/etc/init.d/$SERVICE_NAME" ]; then
            log_info "Stopping existing service..."
            /etc/init.d/$SERVICE_NAME stop 2>/dev/null || true
        fi
        
        # Kill any running processes
        pkill -f "python.*monitoring" 2>/dev/null || true
        sleep 2
    fi
}

install_system_dependencies() {
    log_step "Installing system dependencies..."
    
    # Update package list
    apt-get update -qq
    
    # Essential system packages
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv python3-dev \
        build-essential \
        libgl1-mesa-glx libglib2.0-0 \
        libxkbcommon-x11-0 libxcb-icccm4 \
        libxcb-image0 libxcb-keysyms1 \
        libxcb-randr0 libxcb-render-util0 \
        libxcb-xinerama0 libfontconfig1 \
        libdbus-1-3 \
        libxcb-cursor0 \
        qtbase5-dev qt5-qmake \
        libxcb1-dev libxcb-glx0-dev \
        libx11-xcb1 libxcb-util1 \
        libxcb-shape0-dev libxcb-xfixes0-dev \
        libegl1-mesa-dev \
        x11-utils xauth \
        openbox unclutter x11-xserver-utils \
        curl wget git \
        cron rsyslog \
        2>/dev/null || {
            log_warning "Some packages may not be available - continuing..."
        }
    
    # Install specific packages for antiX
    if grep -q "antiX" /etc/os-release 2>/dev/null; then
        apt-get install -y --no-install-recommends \
            fluxbox icewm \
            libqt5core5a libqt5gui5 libqt5widgets5 \
            python3-tk \
            2>/dev/null || true
    fi
    
    log_step "System dependencies installed successfully"
}

create_directories() {
    log_step "Creating application directories..."
    
    # Create main installation directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/exports"
    mkdir -p "$INSTALL_DIR/monitoring-roll-machine"
    
    # Set proper permissions
    chmod 755 "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR/logs"
    chmod 755 "$INSTALL_DIR/exports"
    
    log_step "Application directories created"
}

copy_application_files() {
    log_step "Copying application files..."
    
    # Copy monitoring application
    if [ -d "$CURRENT_DIR/monitoring" ]; then
        cp -r "$CURRENT_DIR/monitoring" "$INSTALL_DIR/monitoring-roll-machine/"
    else
        log_error "Application files not found in current directory"
        exit 1
    fi
    
    # Copy additional files
    [ -f "$CURRENT_DIR/requirements.txt" ] && cp "$CURRENT_DIR/requirements.txt" "$INSTALL_DIR/monitoring-roll-machine/"
    [ -f "$CURRENT_DIR/run_app.py" ] && cp "$CURRENT_DIR/run_app.py" "$INSTALL_DIR/monitoring-roll-machine/"
    [ -f "$CURRENT_DIR/README.md" ] && cp "$CURRENT_DIR/README.md" "$INSTALL_DIR/"
    
    # Create logs and exports directories in app
    mkdir -p "$INSTALL_DIR/monitoring-roll-machine/logs"
    mkdir -p "$INSTALL_DIR/monitoring-roll-machine/exports"
    
    # Link to main directories
    ln -sf "$INSTALL_DIR/logs" "$INSTALL_DIR/monitoring-roll-machine/logs/system" 2>/dev/null || true
    ln -sf "$INSTALL_DIR/exports" "$INSTALL_DIR/monitoring-roll-machine/exports/shared" 2>/dev/null || true
    
    log_step "Application files copied successfully"
}

setup_python_environment() {
    log_step "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Remove old virtual environment if updating
    if [ "$UPDATE_MODE" = true ] && [ -d "venv" ]; then
        log_info "Removing old virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment
    python3 -m venv venv
    
    # Activate and upgrade pip
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    # Install requirements
    if [ -f "$INSTALL_DIR/monitoring-roll-machine/requirements.txt" ]; then
        log_info "Installing Python requirements..."
        pip install -r "$INSTALL_DIR/monitoring-roll-machine/requirements.txt"
    else
        # Install essential packages manually
        log_info "Installing essential Python packages..."
        pip install \
            PySide6>=6.6.0 \
            pyqtgraph>=0.13.3 \
            pyserial>=3.5 \
            python-dotenv>=1.0.0 \
            pyyaml>=6.0.1 \
            appdirs>=1.4.4 \
            qrcode>=7.4.2 \
            Pillow>=10.0.0
    fi
    
    deactivate
    
    log_step "Python environment setup completed"
}

create_startup_scripts() {
    log_step "Creating startup scripts..."
    
    # Create main startup script
    cat > "$INSTALL_DIR/start-rollmachine.sh" << 'STARTUP_EOF'
#!/bin/bash

# Roll Machine Monitor Startup Script

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
VENV_PYTHON="/opt/rollmachine-monitor/venv/bin/python"
LOG_FILE="/opt/rollmachine-monitor/logs/startup.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [STARTUP] $1" | tee -a "$LOG_FILE"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Setup display for GUI
export DISPLAY=${DISPLAY:-:0}
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-xcb}

# Change to application directory
cd "$APP_DIR" || {
    log_message "ERROR: Cannot access application directory"
    exit 1
}

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    log_message "ERROR: Virtual environment not found"
    exit 1
fi

log_message "Starting Roll Machine Monitor..."

# Start the application
exec "$VENV_PYTHON" -m monitoring
STARTUP_EOF

    # Create kiosk mode startup script
    cat > "$INSTALL_DIR/start-rollmachine-kiosk.sh" << 'KIOSK_EOF'
#!/bin/bash

# Roll Machine Monitor Kiosk Mode Startup Script

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
VENV_PYTHON="/opt/rollmachine-monitor/venv/bin/python"
LOG_FILE="/opt/rollmachine-monitor/logs/kiosk.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [KIOSK] $1" | tee -a "$LOG_FILE"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Setup display and disable screensaver
export DISPLAY=${DISPLAY:-:0}
export QT_QPA_PLATFORM=xcb

# Disable screen saver and power management
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

# Hide cursor after 1 second of inactivity
unclutter -idle 1 -root &>/dev/null &

# Change to application directory
cd "$APP_DIR" || {
    log_message "ERROR: Cannot access application directory"
    exit 1
}

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    log_message "ERROR: Virtual environment not found"
    exit 1
fi

log_message "Starting Roll Machine Monitor in Kiosk Mode..."

# Start the application in kiosk mode
exec "$VENV_PYTHON" -c "
import sys
import os
sys.path.insert(0, os.getcwd())

# Try to run kiosk mode
try:
    from monitoring.ui.kiosk_ui import MonitoringKioskApp
    app = MonitoringKioskApp()
    app.run()
except ImportError:
    # Fallback to regular mode
    import monitoring.__main__
"
KIOSK_EOF

    # Make scripts executable
    chmod +x "$INSTALL_DIR/start-rollmachine.sh"
    chmod +x "$INSTALL_DIR/start-rollmachine-kiosk.sh"
    
    log_step "Startup scripts created"
}

create_sysv_init_script() {
    log_step "Creating SysV init script (no systemd)..."
    
    cat > "/etc/init.d/$SERVICE_NAME" << INIT_EOF
#!/bin/bash
### BEGIN INIT INFO
# Provides:          rollmachine-monitor
# Required-Start:    \$local_fs \$remote_fs \$network \$syslog
# Required-Stop:     \$local_fs \$remote_fs \$network \$syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Roll Machine Monitor Service
# Description:       Industrial monitoring application for JSK3588 roll machines
### END INIT INFO

DAEMON="rollmachine-monitor"
DAEMON_USER="root"
DAEMON_DIR="/opt/rollmachine-monitor"
DAEMON_CMD="\$DAEMON_DIR/start-rollmachine-kiosk.sh"
LOCK_FILE="/var/lock/subsys/rollmachine-monitor"
PID_FILE="/var/run/rollmachine-monitor.pid"

start() {
    echo -n "Starting \$DAEMON: "
    
    # Check if already running
    if [ -f "\$PID_FILE" ]; then
        PID=\$(cat "\$PID_FILE")
        if ps -p "\$PID" > /dev/null 2>&1; then
            echo "already running (PID \$PID)"
            return 1
        else
            rm -f "\$PID_FILE"
        fi
    fi
    
    # Start the daemon
    cd "\$DAEMON_DIR"
    nohup "\$DAEMON_CMD" > /dev/null 2>&1 &
    PID=\$!
    
    if ps -p "\$PID" > /dev/null 2>&1; then
        echo "\$PID" > "\$PID_FILE"
        touch "\$LOCK_FILE"
        echo "started (PID \$PID)"
        return 0
    else
        echo "failed to start"
        return 1
    fi
}

stop() {
    echo -n "Stopping \$DAEMON: "
    
    if [ -f "\$PID_FILE" ]; then
        PID=\$(cat "\$PID_FILE")
        if ps -p "\$PID" > /dev/null 2>&1; then
            kill "\$PID"
            sleep 2
            
            if ps -p "\$PID" > /dev/null 2>&1; then
                kill -9 "\$PID"
                sleep 1
            fi
            
            rm -f "\$PID_FILE"
            rm -f "\$LOCK_FILE"
            echo "stopped"
            return 0
        else
            rm -f "\$PID_FILE"
            rm -f "\$LOCK_FILE"
            echo "not running"
            return 1
        fi
    else
        echo "not running"
        return 1
    fi
}

restart() {
    stop
    sleep 1
    start
}

status() {
    if [ -f "\$PID_FILE" ]; then
        PID=\$(cat "\$PID_FILE")
        if ps -p "\$PID" > /dev/null 2>&1; then
            echo "\$DAEMON is running (PID \$PID)"
            return 0
        else
            echo "\$DAEMON is not running (stale PID file)"
            return 1
        fi
    else
        echo "\$DAEMON is not running"
        return 1
    fi
}

case "\$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit \$?
INIT_EOF

    # Make init script executable
    chmod +x "/etc/init.d/$SERVICE_NAME"
    
    # Add to runlevels (antiX uses SysV init)
    if command -v update-rc.d >/dev/null 2>&1; then
        update-rc.d "$SERVICE_NAME" defaults
        log_info "Service enabled for auto-start (update-rc.d)"
    elif command -v chkconfig >/dev/null 2>&1; then
        chkconfig --add "$SERVICE_NAME"
        chkconfig "$SERVICE_NAME" on
        log_info "Service enabled for auto-start (chkconfig)"
    else
        log_warning "Could not auto-enable service. You may need to enable manually."
    fi
    
    log_step "SysV init script created and enabled"
}

create_watchdog_script() {
    log_step "Creating watchdog script..."
    
    cat > "$INSTALL_DIR/watchdog.sh" << 'WATCHDOG_EOF'
#!/bin/bash

# Roll Machine Monitor Watchdog Script
# Monitors the application and restarts if it stops

SERVICE_NAME="rollmachine-monitor"
LOG_FILE="/opt/rollmachine-monitor/logs/watchdog.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WATCHDOG] $1" >> "$LOG_FILE"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check if service should be running
if [ ! -f "/etc/init.d/$SERVICE_NAME" ]; then
    exit 0
fi

# Check service status
if ! /etc/init.d/$SERVICE_NAME status >/dev/null 2>&1; then
    log_message "Service not running - attempting restart"
    
    # Try to restart
    if /etc/init.d/$SERVICE_NAME start >/dev/null 2>&1; then
        log_message "Service restarted successfully"
    else
        log_message "Failed to restart service"
    fi
fi
WATCHDOG_EOF

    chmod +x "$INSTALL_DIR/watchdog.sh"
    
    # Add to cron (every minute)
    if ! crontab -l 2>/dev/null | grep -q "rollmachine.*watchdog"; then
        (crontab -l 2>/dev/null; echo "* * * * * $INSTALL_DIR/watchdog.sh >/dev/null 2>&1") | crontab -
        log_info "Watchdog added to cron (runs every minute)"
    fi
    
    log_step "Watchdog script created and scheduled"
}

create_desktop_shortcuts() {
    log_step "Creating desktop shortcuts..."
    
    # Create application icon (simple text-based)
    cat > "$INSTALL_DIR/rollmachine-icon.svg" << 'ICON_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="#2196F3" rx="8"/>
  <text x="32" y="40" font-family="Arial" font-size="24" font-weight="bold" text-anchor="middle" fill="white">RM</text>
</svg>
ICON_EOF

    # Desktop shortcut for regular mode
    cat > "/usr/share/applications/rollmachine-monitor.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Roll Machine Monitor
Comment=Industrial monitoring application for JSK3588 roll machines
Exec=/opt/rollmachine-monitor/start-rollmachine.sh
Icon=/opt/rollmachine-monitor/rollmachine-icon.svg
Terminal=false
Categories=Utility;System;Monitor;
StartupNotify=true
StartupWMClass=monitoring
DESKTOP_EOF

    # Desktop shortcut for kiosk mode
    cat > "/usr/share/applications/rollmachine-monitor-kiosk.desktop" << 'KIOSK_DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Roll Machine Monitor (Kiosk)
Comment=Industrial monitoring application for JSK3588 roll machines - Kiosk Mode
Exec=/opt/rollmachine-monitor/start-rollmachine-kiosk.sh
Icon=/opt/rollmachine-monitor/rollmachine-icon.svg
Terminal=false
Categories=Utility;System;Monitor;
StartupNotify=true
StartupWMClass=monitoring
KIOSK_DESKTOP_EOF

    # Create desktop shortcuts for all users
    for user_home in /home/*; do
        if [ -d "$user_home" ] && [ "$user_home" != "/home/lost+found" ]; then
            username=$(basename "$user_home")
            
            # Skip if not a real user directory
            if ! id "$username" >/dev/null 2>&1; then
                continue
            fi
            
            user_desktop="$user_home/Desktop"
            mkdir -p "$user_desktop"
            
            # Copy shortcuts to user desktop
            cp "/usr/share/applications/rollmachine-monitor.desktop" "$user_desktop/"
            cp "/usr/share/applications/rollmachine-monitor-kiosk.desktop" "$user_desktop/"
            
            # Set proper ownership
            chown -R "$username:$username" "$user_desktop"
            chmod +x "$user_desktop/rollmachine-monitor.desktop"
            chmod +x "$user_desktop/rollmachine-monitor-kiosk.desktop"
        fi
    done
    
    # Create desktop shortcuts for current user if running with sudo
    if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
        sudo_user_home="/home/$SUDO_USER"
        if [ -d "$sudo_user_home" ]; then
            sudo_desktop="$sudo_user_home/Desktop"
            mkdir -p "$sudo_desktop"
            
            cp "/usr/share/applications/rollmachine-monitor.desktop" "$sudo_desktop/"
            cp "/usr/share/applications/rollmachine-monitor-kiosk.desktop" "$sudo_desktop/"
            
            chown -R "$SUDO_USER:$SUDO_USER" "$sudo_desktop"
            chmod +x "$sudo_desktop/rollmachine-monitor.desktop"
            chmod +x "$sudo_desktop/rollmachine-monitor-kiosk.desktop"
        fi
    fi
    
    log_step "Desktop shortcuts created for all users"
}

setup_kiosk_user() {
    log_step "Setting up kiosk user..."
    
    # Create kiosk user if doesn't exist
    if ! id "kiosk" >/dev/null 2>&1; then
        useradd -m -s /bin/bash kiosk
        echo "kiosk:kiosk123" | chpasswd
        log_info "Created kiosk user with password: kiosk123"
    fi
    
    # Add kiosk user to dialout group (for serial port access)
    usermod -a -G dialout kiosk
    
    # Setup auto-login for kiosk user
    kiosk_home="/home/kiosk"
    mkdir -p "$kiosk_home/.config/autostart"
    mkdir -p "$kiosk_home/.fluxbox"
    mkdir -p "$kiosk_home/.icewm"
    
    # Create autostart script for kiosk user
    cat > "$kiosk_home/.config/autostart/rollmachine.desktop" << 'KIOSK_AUTOSTART_EOF'
[Desktop Entry]
Type=Application
Name=Roll Machine Monitor Kiosk
Exec=/opt/rollmachine-monitor/start-rollmachine-kiosk.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
KIOSK_AUTOSTART_EOF

    # Create fluxbox startup for kiosk
    cat > "$kiosk_home/.fluxbox/startup" << 'FLUXBOX_EOF'
#!/bin/bash

# Disable screen saver
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 1 -root &

# Start roll machine monitor
/opt/rollmachine-monitor/start-rollmachine-kiosk.sh &

# Start fluxbox
exec fluxbox
FLUXBOX_EOF

    chmod +x "$kiosk_home/.fluxbox/startup"
    
    # Set proper ownership
    chown -R kiosk:kiosk "$kiosk_home"
    
    log_step "Kiosk user setup completed"
}

restore_backup() {
    if [ "$UPDATE_MODE" = true ]; then
        log_step "Restoring backed up configuration..."
        
        # Restore config
        if [ -f "/tmp/rollmachine-config-backup.json" ]; then
            cp "/tmp/rollmachine-config-backup.json" "$INSTALL_DIR/monitoring-roll-machine/monitoring/config.json"
            log_info "Configuration restored"
        fi
        
        # Restore exports
        if [ -d "/tmp/rollmachine-exports-backup" ]; then
            cp -r "/tmp/rollmachine-exports-backup/"* "$INSTALL_DIR/monitoring-roll-machine/exports/" 2>/dev/null || true
            log_info "Exports restored"
        fi
        
        # Clean up backup files
        rm -f "/tmp/rollmachine-config-backup.json"
        rm -rf "/tmp/rollmachine-exports-backup"
    fi
}

set_permissions() {
    log_step "Setting proper permissions..."
    
    # Set ownership and permissions
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    # Make specific directories writable
    chmod 777 "$INSTALL_DIR/logs"
    chmod 777 "$INSTALL_DIR/exports"
    chmod 777 "$INSTALL_DIR/monitoring-roll-machine/logs"
    chmod 777 "$INSTALL_DIR/monitoring-roll-machine/exports"
    
    # Ensure scripts are executable
    find "$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \;
    
    log_step "Permissions set correctly"
}

start_services() {
    log_step "Starting services..."
    
    # Start the service
    if /etc/init.d/$SERVICE_NAME start; then
        log_info "Roll Machine Monitor service started successfully"
    else
        log_warning "Failed to start service automatically"
        log_info "You can start it manually with: sudo /etc/init.d/$SERVICE_NAME start"
    fi
    
    # Test if service is running
    sleep 3
    if /etc/init.d/$SERVICE_NAME status >/dev/null 2>&1; then
        log_step "Service is running correctly"
    else
        log_warning "Service may not be running properly"
    fi
}

print_completion_info() {
    echo
    echo "================================================="
    echo -e "${GREEN}🎉 Installation Completed Successfully! 🎉${NC}"
    echo "================================================="
    echo
    echo -e "${BLUE}📁 Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${BLUE}🔧 Service Management:${NC}"
    echo "   Start:   sudo /etc/init.d/$SERVICE_NAME start"
    echo "   Stop:    sudo /etc/init.d/$SERVICE_NAME stop"
    echo "   Restart: sudo /etc/init.d/$SERVICE_NAME restart"
    echo "   Status:  sudo /etc/init.d/$SERVICE_NAME status"
    echo
    echo -e "${BLUE}🚀 Manual Startup:${NC}"
    echo "   Regular Mode: $INSTALL_DIR/start-rollmachine.sh"
    echo "   Kiosk Mode:   $INSTALL_DIR/start-rollmachine-kiosk.sh"
    echo
    echo -e "${BLUE}🖥️  Desktop Shortcuts:${NC}"
    echo "   - Roll Machine Monitor (Regular)"
    echo "   - Roll Machine Monitor (Kiosk)"
    echo
    echo -e "${BLUE}👤 Kiosk User:${NC}"
    echo "   Username: kiosk"
    echo "   Password: kiosk123"
    echo "   Auto-starts Roll Machine Monitor on login"
    echo
    echo -e "${BLUE}📋 Log Files:${NC}"
    echo "   Startup: $INSTALL_DIR/logs/startup.log"
    echo "   Kiosk:   $INSTALL_DIR/logs/kiosk.log"
    echo "   Watchdog: $INSTALL_DIR/logs/watchdog.log"
    echo
    echo -e "${BLUE}🔄 Update:${NC}"
    echo "   To update: sudo $0 --update"
    echo
    echo -e "${GREEN}✅ The application is ready to use!${NC}"
    echo
}

# ===============================================
# MAIN INSTALLATION PROCESS
# ===============================================

main() {
    print_header
    
    # Pre-installation checks
    check_root
    check_antix
    
    # Backup existing installation if updating
    backup_existing
    
    # Core installation steps
    install_system_dependencies
    create_directories
    copy_application_files
    setup_python_environment
    
    # Service and startup setup
    create_startup_scripts
    create_sysv_init_script
    create_watchdog_script
    
    # User interface setup
    create_desktop_shortcuts
    setup_kiosk_user
    
    # Finalization
    restore_backup
    set_permissions
    start_services
    
    # Show completion information
    print_completion_info
}

# Run main installation
main "$@" 