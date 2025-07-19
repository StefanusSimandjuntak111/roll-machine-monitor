#!/bin/bash
# AntiX Standalone Kiosk Startup Script
# Works without systemd - for antiX and other init systems

set -e

# Configuration
APP_NAME="rollmachine-monitor"
INSTALL_DIR="/opt/$APP_NAME"
VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
APP_DIR="$INSTALL_DIR/monitoring-roll-machine"
KIOSK_LOG="/var/log/rollmachine-kiosk.log"
PID_FILE="/var/run/rollmachine-kiosk.pid"
MAX_RESTART_ATTEMPTS=999999

# Ensure log file exists
sudo touch "$KIOSK_LOG" 2>/dev/null || touch "$HOME/rollmachine-kiosk.log"
KIOSK_LOG="${KIOSK_LOG:-$HOME/rollmachine-kiosk.log}"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ANTIX-KIOSK] $1" | tee -a "$KIOSK_LOG"
}

# Check if already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

# Stop running instance
stop_instance() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        log_message "Stopping existing instance (PID: $pid)"
        kill -TERM "$pid" 2>/dev/null || true
        sleep 3
        kill -KILL "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "python.*kiosk_ui" 2>/dev/null || true
    pkill -f "Xvfb.*:99" 2>/dev/null || true
}

# Setup environment for antiX
setup_environment() {
    log_message "Setting up AntiX kiosk environment..."
    
    # Set display
    export DISPLAY=${DISPLAY:-:0}
    export QT_QPA_PLATFORM=xcb
    
    # Kivy configuration
    export KIVY_WINDOW_PROVIDER=x11
    export KIVY_GL_BACKEND=gl
    export KIVY_WINDOW=sdl2
    
    # Disable screen saver and power management
    xset s off 2>/dev/null || true
    xset -dpms 2>/dev/null || true
    xset s noblank 2>/dev/null || true
    
    # Hide cursor
    unclutter -idle 1 -root &>/dev/null &
    
    # Disable keyboard shortcuts
    setxkbmap -option 2>/dev/null || true
}

# Start virtual display if needed
start_virtual_display() {
    if [ -z "$DISPLAY" ] || ! xset q &>/dev/null; then
        log_message "Starting virtual display for headless mode..."
        
        # Kill existing Xvfb
        pkill -f "Xvfb.*:99" 2>/dev/null || true
        sleep 2
        
        # Start virtual display
        Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +extension RANDR +extension RENDER &
        XVFB_PID=$!
        
        export DISPLAY=:99
        sleep 3
        
        # Start minimal window manager
        if command -v openbox >/dev/null; then
            openbox --replace &>/dev/null &
        elif command -v fluxbox >/dev/null; then
            fluxbox --replace &>/dev/null &
        elif command -v icewm >/dev/null; then
            icewm --replace &>/dev/null &
        fi
        
        log_message "Virtual display started on :99"
    fi
}

# Run the kiosk application
run_kiosk_app() {
    log_message "Starting Roll Machine Monitor in AntiX KIOSK MODE..."
    
    cd "$APP_DIR"
    
    # Use PySide6 as DEFAULT (perfect design and very stable)
    log_message "Starting PySide6 kiosk mode (recommended - perfect UI design)"
    
    # Run PySide6 in fullscreen kiosk mode
    exec "$VENV_PYTHON" -c "
import sys
import os
sys.path.insert(0, os.getcwd())

# Set Qt environment for kiosk mode
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from monitoring.ui.main_window import ModernMainWindow

# Create application
app = QApplication(sys.argv)
app.setStyle('Fusion')

# Create main window
window = ModernMainWindow()

# Set KIOSK MODE - fullscreen, no close button, stays on top
window.setWindowState(Qt.WindowState.WindowFullScreen)
window.setWindowFlags(
    Qt.WindowType.FramelessWindowHint | 
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.CustomizeWindowHint
)

# Override close event to prevent closing
original_close_event = window.closeEvent
def prevent_close(event):
    event.ignore()  # Prevent closing in kiosk mode
    print('Close attempt blocked - kiosk mode active')

window.closeEvent = prevent_close

# Show fullscreen
window.showFullScreen()

print('PySide6 kiosk mode started successfully')

# Start event loop
sys.exit(app.exec())
"
}

# Main kiosk loop with auto-restart
main_kiosk_loop() {
    local restart_count=0
    
    log_message "Starting AntiX kiosk mode with auto-restart..."
    
    while [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; do
        restart_count=$((restart_count + 1))
        
        log_message "Starting app (attempt #$restart_count)..."
        
        # Run the application in background
        run_kiosk_app &
        local app_pid=$!
        
        # Save PID
        echo "$app_pid" > "$PID_FILE"
        
        log_message "App started with PID: $app_pid"
        
        # Wait for app to exit
        wait "$app_pid" || true
        
        # Check if app is still running
        if ! kill -0 "$app_pid" 2>/dev/null; then
            log_message "App exited. Restarting in 3 seconds..."
            rm -f "$PID_FILE"
            sleep 3
        fi
    done
    
    log_message "Maximum restart attempts reached. Exiting."
}

# Cleanup function
cleanup() {
    log_message "Cleaning up AntiX kiosk session..."
    stop_instance
    exit 0
}

# Signal handlers
trap cleanup SIGTERM SIGINT

# Check if application exists
if [ ! -d "$APP_DIR" ]; then
    log_message "ERROR: Application not found at $APP_DIR"
    log_message "Please install Roll Machine Monitor first"
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    log_message "ERROR: Python virtual environment not found at $VENV_PYTHON"
    log_message "Please reinstall Roll Machine Monitor"
    exit 1
fi

# Main execution
log_message "=== Starting Roll Machine Monitor AntiX Kiosk Mode ==="
log_message "App Directory: $APP_DIR"
log_message "Python: $VENV_PYTHON"
log_message "Log File: $KIOSK_LOG"
log_message "PID File: $PID_FILE"

# Stop any existing instance
stop_instance

setup_environment
start_virtual_display
main_kiosk_loop 