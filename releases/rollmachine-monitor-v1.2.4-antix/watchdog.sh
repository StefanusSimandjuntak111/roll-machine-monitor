#!/bin/bash
# Roll Machine Monitor Watchdog Script
# Monitors the kiosk application and restarts it if needed

set -e

WATCHDOG_LOG="/var/log/rollmachine-watchdog.log"
KIOSK_SERVICE="rollmachine-kiosk.service"
CHECK_INTERVAL=30  # seconds
MAX_MEMORY_MB=1024  # Max memory usage in MB

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WATCHDOG] $1" | tee -a "$WATCHDOG_LOG"
}

# Check if kiosk process is running
check_process() {
    if pgrep -f "python.*kiosk_ui" >/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if display is available
check_display() {
    if [ -n "$DISPLAY" ] && xset q &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check memory usage
check_memory() {
    local pid=$(pgrep -f "python.*kiosk_ui" | head -1)
    if [ -n "$pid" ]; then
        local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null || echo "0")
        local memory_mb=$((memory_kb / 1024))
        
        if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
            log_message "WARNING: High memory usage: ${memory_mb}MB (limit: ${MAX_MEMORY_MB}MB)"
            return 1
        fi
    fi
    return 0
}

# Check if systemd service is active
check_service() {
    systemctl is-active --quiet "$KIOSK_SERVICE"
}

# Restart the service
restart_service() {
    log_message "Restarting kiosk service..."
    systemctl restart "$KIOSK_SERVICE"
    sleep 10
}

# Kill hanging processes
kill_hanging_processes() {
    log_message "Killing hanging processes..."
    pkill -f "python.*kiosk_ui" || true
    pkill -f "Xvfb.*:99" || true
    sleep 5
}

# Main watchdog loop
main_watchdog() {
    log_message "Starting Roll Machine Monitor Watchdog"
    log_message "Check interval: ${CHECK_INTERVAL}s"
    log_message "Memory limit: ${MAX_MEMORY_MB}MB"
    
    while true; do
        local restart_needed=false
        local reason=""
        
        # Check if service is running
        if ! check_service; then
            restart_needed=true
            reason="Service not active"
        # Check if process is running
        elif ! check_process; then
            restart_needed=true
            reason="Process not found"
        # Check display availability
        elif ! check_display; then
            restart_needed=true
            reason="Display not available"
        # Check memory usage
        elif ! check_memory; then
            restart_needed=true
            reason="Memory limit exceeded"
        fi
        
        # If restart is needed
        if [ "$restart_needed" = true ]; then
            log_message "ALERT: $reason - restarting application"
            kill_hanging_processes
            restart_service
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# Signal handlers
cleanup() {
    log_message "Watchdog shutting down..."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Ensure log file exists
touch "$WATCHDOG_LOG"

# Start watchdog
main_watchdog 