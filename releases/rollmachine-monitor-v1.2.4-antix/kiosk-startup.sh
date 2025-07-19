#!/bin/bash
# Roll Machine Monitor - Kiosk Startup Script
# Runs the application in full kiosk mode with auto-restart

set -e

# Configuration
APP_NAME="rollmachine-monitor"
INSTALL_DIR="/opt/$APP_NAME"
VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
APP_DIR="$INSTALL_DIR/monitoring-roll-machine"
KIOSK_LOG="/var/log/rollmachine-kiosk.log"
MAX_RESTART_ATTEMPTS=999999  # Infinite restart

# Ensure log file exists
sudo touch "$KIOSK_LOG" 2>/dev/null || touch "$HOME/rollmachine-kiosk.log"
KIOSK_LOG="${KIOSK_LOG:-$HOME/rollmachine-kiosk.log}"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [KIOSK] $1" | tee -a "$KIOSK_LOG"
}

# Setup environment for headless/kiosk mode
setup_environment() {
    log_message "Setting up kiosk environment..."
    
    # Set display for headless operation
    export DISPLAY=${DISPLAY:-:0}
    export QT_QPA_PLATFORM=xcb
    
    # Kivy configuration for headless
    export KIVY_WINDOW_PROVIDER=x11
    export KIVY_GL_BACKEND=gl
    export KIVY_WINDOW=sdl2
    
    # Disable screen saver and power management
    xset s off 2>/dev/null || true
    xset -dpms 2>/dev/null || true
    xset s noblank 2>/dev/null || true
    
    # Hide cursor after 1 second of inactivity
    unclutter -idle 1 -root &>/dev/null &
    
    # Disable alt+tab, ctrl+alt+del
    setxkbmap -option 2>/dev/null || true
}

# Start virtual display if running headless
start_virtual_display() {
    if [ -z "$DISPLAY" ] || ! xset q &>/dev/null; then
        log_message "Starting virtual display for headless mode..."
        
        # Kill existing Xvfb instances
        pkill -f "Xvfb.*:99" || true
        sleep 2
        
        # Start virtual display
        Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +extension RANDR +extension RENDER &
        XVFB_PID=$!
        
        export DISPLAY=:99
        sleep 3
        
        # Start a minimal window manager
        openbox --replace &>/dev/null &
        
        log_message "Virtual display started on :99"
    fi
}

# Run the kiosk application
run_kiosk_app() {
    log_message "Starting Roll Machine Monitor in KIOSK MODE (PySide6)..."
    
    cd "$APP_DIR"
    
    # Run PySide6 kiosk UI (default and recommended)
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

# Start event loop
sys.exit(app.exec())
"
}

# Main kiosk loop with auto-restart
main_kiosk_loop() {
    local restart_count=0
    
    log_message "Starting kiosk mode with auto-restart..."
    
    while [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; do
        restart_count=$((restart_count + 1))
        
        log_message "Starting app (attempt #$restart_count)..."
        
        # Run the application
        if run_kiosk_app; then
            log_message "App exited normally"
        else
            exit_code=$?
            log_message "App crashed with exit code: $exit_code"
        fi
        
        log_message "App stopped. Restarting in 3 seconds..."
        sleep 3
    done
    
    log_message "Maximum restart attempts reached. Exiting."
}

# Cleanup function
cleanup() {
    log_message "Cleaning up kiosk session..."
    pkill -f "python.*kiosk_ui" || true
    pkill -f "Xvfb.*:99" || true
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
log_message "=== Starting Roll Machine Monitor Kiosk Mode ==="
log_message "App Directory: $APP_DIR"
log_message "Python: $VENV_PYTHON"
log_message "Log File: $KIOSK_LOG"

setup_environment
start_virtual_display
main_kiosk_loop 