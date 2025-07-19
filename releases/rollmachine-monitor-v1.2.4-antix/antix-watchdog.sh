#!/bin/bash
# AntiX Cron Watchdog Script
# Monitors Roll Machine Monitor and restarts if needed
# Run this every minute via cron

PIDFILE="/var/run/rollmachine-monitor.pid"
LOGFILE="/var/log/rollmachine-watchdog.log"
INIT_SCRIPT="/etc/init.d/rollmachine-monitor"
MAX_MEMORY_MB=1024
CHECK_INTERVAL=60

# Ensure log file exists
touch "$LOGFILE" 2>/dev/null || LOGFILE="/tmp/rollmachine-watchdog.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WATCHDOG] $1" >> "$LOGFILE"
}

# Check if process is running
check_process() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    
    # Also check by process name
    if pgrep -f "ModernMainWindow" >/dev/null; then
        return 0  # Running
    fi
    
    return 1  # Not running
}

# Check memory usage
check_memory() {
    local pid=$(pgrep -f "ModernMainWindow" | head -1)
    if [ -n "$pid" ]; then
        local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null || echo "0")
        local memory_mb=$((memory_kb / 1024))
        
        if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
            log_message "High memory usage: ${memory_mb}MB (limit: ${MAX_MEMORY_MB}MB)"
            return 1
        fi
    fi
    return 0
}

# Check display availability
check_display() {
    # Check if X is running
    if [ -n "$DISPLAY" ] && xset q &>/dev/null; then
        return 0
    fi
    
    # Check virtual display
    if pgrep -f "Xvfb.*:99" >/dev/null; then
        export DISPLAY=:99
        if xset q &>/dev/null 2>&1; then
            return 0
        fi
    fi
    
    return 1
}

# Restart service
restart_service() {
    log_message "Restarting service via init script"
    if [ -x "$INIT_SCRIPT" ]; then
        "$INIT_SCRIPT" restart
        return $?
    else
        log_message "Init script not found: $INIT_SCRIPT"
        return 1
    fi
}

# Main watchdog logic
main_check() {
    local restart_needed=false
    local reason=""
    
    # Check if process is running
    if ! check_process; then
        restart_needed=true
        reason="Process not running"
    # Check memory usage
    elif ! check_memory; then
        restart_needed=true
        reason="Memory limit exceeded"
    # Check display availability
    elif ! check_display; then
        restart_needed=true
        reason="Display not available"
    fi
    
    # Restart if needed
    if [ "$restart_needed" = true ]; then
        log_message "ALERT: $reason - restarting service"
        restart_service
        if [ $? -eq 0 ]; then
            log_message "Service restarted successfully"
        else
            log_message "Failed to restart service"
        fi
    else
        # Service is healthy - just log timestamp
        log_message "Service healthy"
    fi
}

# Only run if not already running
LOCKFILE="/tmp/rollmachine-watchdog.lock"
if [ -f "$LOCKFILE" ]; then
    lock_pid=$(cat "$LOCKFILE" 2>/dev/null)
    if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
        # Another instance is running
        exit 0
    fi
fi

# Create lock file
echo $$ > "$LOCKFILE"

# Run the check
main_check

# Remove lock file
rm -f "$LOCKFILE"

exit 0 