#!/bin/bash
# Start Roll Machine Monitor in Kiosk Mode

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
PYTHON_PATH="/opt/rollmachine-monitor/venv/bin/python"
LOG_FILE="/var/log/rollmachine-kiosk.log"

echo "🚀 Starting Roll Machine Monitor in Kiosk Mode..."

# Check if installation exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Installation not found in $APP_DIR"
    echo "   Please install the application first"
    exit 1
fi

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python virtual environment not found"
    echo "   Please reinstall the application"
    exit 1
fi

# Kill any existing instances
echo "🔄 Stopping existing instances..."
pkill -f "python.*monitoring" 2>/dev/null || true
sleep 2

# Set display (try common displays)
if [ -z "$DISPLAY" ]; then
    for display in :0 :1 :99; do
        if xset -display $display q &>/dev/null; then
            export DISPLAY=$display
            echo "✅ Using display: $DISPLAY"
            break
        fi
    done
fi

if [ -z "$DISPLAY" ]; then
    echo "⚠️  No X display found - starting virtual display"
    # Start virtual display if needed
    if ! pgrep Xvfb >/dev/null; then
        Xvfb :99 -screen 0 1920x1080x24 &
        sleep 2
    fi
    export DISPLAY=:99
fi

# Change to application directory
cd "$APP_DIR" || exit 1

# Start application in kiosk mode
echo "🎯 Starting application..."
echo "   Directory: $APP_DIR"
echo "   Python: $PYTHON_PATH"
echo "   Display: $DISPLAY"
echo "   Log: $LOG_FILE"

# Start with output to log
$PYTHON_PATH -m monitoring >> "$LOG_FILE" 2>&1 &

APP_PID=$!
echo "✅ Application started with PID: $APP_PID"

# Monitor and restart if needed
echo "🔄 Monitoring application (press Ctrl+C to stop)..."
while true; do
    if ! kill -0 $APP_PID 2>/dev/null; then
        echo "💥 Application crashed - restarting in 3 seconds..."
        sleep 3
        
        cd "$APP_DIR"
        $PYTHON_PATH -m monitoring >> "$LOG_FILE" 2>&1 &
        APP_PID=$!
        echo "🔄 Restarted with PID: $APP_PID"
    fi
    sleep 5
done 