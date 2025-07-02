#!/bin/bash
# AntiX Init Script for Roll Machine Monitor
# Auto-start and auto-restart for antiX systems

### BEGIN INIT INFO
# Provides:          rollmachine-monitor
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Roll Machine Monitor Kiosk
# Description:       Auto-start and auto-restart Roll Machine Monitor in kiosk mode
### END INIT INFO

# Configuration
NAME="rollmachine-monitor"
DAEMON="/opt/rollmachine-monitor/antix-startup.sh"
PIDFILE="/var/run/rollmachine-monitor.pid"
LOGFILE="/var/log/rollmachine-monitor-init.log"
USER="kiosk"

# Ensure log file exists
touch "$LOGFILE"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INIT] $1" | tee -a "$LOGFILE"
}

# Check if process is running
is_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

# Start the service
start() {
    if is_running; then
        log_message "Service already running"
        return 0
    fi
    
    log_message "Starting Roll Machine Monitor..."
    
    # Kill any existing processes
    pkill -f "ModernMainWindow" 2>/dev/null || true
    pkill -f "antix-startup.sh" 2>/dev/null || true
    sleep 2
    
    # Start as kiosk user in background
    su - "$USER" -c "nohup $DAEMON >/dev/null 2>&1 &"
    sleep 3
    
    # Find and save PID
    local pid=$(pgrep -f "antix-startup.sh" | head -1)
    if [ -n "$pid" ]; then
        echo "$pid" > "$PIDFILE"
        log_message "Service started with PID: $pid"
        return 0
    else
        log_message "Failed to start service"
        return 1
    fi
}

# Stop the service
stop() {
    if ! is_running; then
        log_message "Service not running"
        return 0
    fi
    
    log_message "Stopping Roll Machine Monitor..."
    
    # Kill main process
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if [ -n "$pid" ]; then
            kill -TERM "$pid" 2>/dev/null || true
            sleep 3
            kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$PIDFILE"
    fi
    
    # Kill any remaining processes
    pkill -f "ModernMainWindow" 2>/dev/null || true
    pkill -f "antix-startup.sh" 2>/dev/null || true
    pkill -f "Xvfb.*:99" 2>/dev/null || true
    
    log_message "Service stopped"
    return 0
}

# Restart the service
restart() {
    log_message "Restarting Roll Machine Monitor..."
    stop
    sleep 2
    start
}

# Get status
status() {
    if is_running; then
        local pid=$(cat "$PIDFILE")
        echo "Roll Machine Monitor is running (PID: $pid)"
        return 0
    else
        echo "Roll Machine Monitor is not running"
        return 1
    fi
}

# Main command handler
case "$1" in
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
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit $? 