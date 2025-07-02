#!/bin/bash
# Smart Watchdog for Roll Machine Monitor
# Only restarts on crash or extended idle (>1 hour)

set -e

# Configuration
WATCHDOG_LOG="/var/log/rollmachine-smart-watchdog.log"
HEARTBEAT_FILE="/tmp/rollmachine_heartbeat"
LOCK_FILE="/tmp/rollmachine_monitor.lock"
CHECK_INTERVAL=60  # Check every minute
IDLE_THRESHOLD=3600  # 1 hour in seconds
MAX_MEMORY_MB=2048  # Increased memory limit

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
PYTHON_PATH="/opt/rollmachine-monitor/venv/bin/python"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SMART-WATCHDOG] $1" | tee -a "$WATCHDOG_LOG"
}

# Check if application process is running
check_process_running() {
    if pgrep -f "python.*monitoring" >/dev/null; then
        return 0
    else
        return 1
    fi
}

# Read heartbeat status
read_heartbeat() {
    if [ -f "$HEARTBEAT_FILE" ]; then
        python3 -c "
import json
import sys
from datetime import datetime, timezone

try:
    with open('$HEARTBEAT_FILE', 'r') as f:
        data = json.load(f)
    
    # Calculate age of heartbeat
    heartbeat_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    
    if heartbeat_time.tzinfo is None:
        heartbeat_time = heartbeat_time.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    age_seconds = (current_time - heartbeat_time).total_seconds()
    
    print(f'{data[\"pid\"]}|{data[\"idle_seconds\"]}|{data[\"is_processing_data\"]}|{age_seconds}')
except Exception as e:
    print('ERROR|0|false|999999')
    sys.exit(1)
"
    else
        echo "NO_HEARTBEAT|0|false|999999"
    fi
}

# Check if singleton lock exists and is valid
check_singleton_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid=$(head -1 "$LOCK_FILE" 2>/dev/null || echo "")
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            return 0  # Lock is valid
        else
            log_message "Found stale lock file, removing..."
            rm -f "$LOCK_FILE"
            return 1  # Lock is stale
        fi
    else
        return 1  # No lock file
    fi
}

# Check memory usage
check_memory_usage() {
    local pid=$(pgrep -f "python.*monitoring" | head -1)
    if [ -n "$pid" ]; then
        local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null || echo "0")
        local memory_mb=$((memory_kb / 1024))
        
        if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
            log_message "HIGH MEMORY: ${memory_mb}MB (limit: ${MAX_MEMORY_MB}MB)"
            return 1
        fi
        
        echo "$memory_mb"
        return 0
    fi
    return 1
}

# Start application safely
start_application() {
    log_message "Starting Roll Machine Monitor..."
    
    # Ensure no other instances
    if check_singleton_lock; then
        log_message "Another instance is already running (singleton lock exists)"
        return 1
    fi
    
    # Kill any zombie processes
    pkill -f "python.*monitoring" 2>/dev/null || true
    sleep 2
    
    # Ensure directory exists and change to it
    if [ ! -d "$APP_DIR" ]; then
        log_message "ERROR: Application directory not found: $APP_DIR"
        return 1
    fi
    
    cd "$APP_DIR"
    
    # Set display if needed
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=:0
    fi
    
    # Start application in background
    nohup "$PYTHON_PATH" -m monitoring > /dev/null 2>&1 &
    local app_pid=$!
    
    # Wait a moment and check if it started successfully
    sleep 5
    if kill -0 "$app_pid" 2>/dev/null; then
        log_message "✅ Application started successfully (PID: $app_pid)"
        return 0
    else
        log_message "❌ Application failed to start"
        return 1
    fi
}

# Main watchdog logic
main_watchdog() {
    log_message "🚀 Starting Smart Watchdog for Roll Machine Monitor"
    log_message "📋 Configuration:"
    log_message "   - Check interval: ${CHECK_INTERVAL}s"
    log_message "   - Idle threshold: ${IDLE_THRESHOLD}s ($(($IDLE_THRESHOLD / 3600)) hour)"
    log_message "   - Memory limit: ${MAX_MEMORY_MB}MB"
    log_message "   - App directory: $APP_DIR"
    log_message "   - Python path: $PYTHON_PATH"
    
    while true; do
        local should_restart=false
        local restart_reason=""
        
        # Check if process is running
        if ! check_process_running; then
            should_restart=true
            restart_reason="Application process not found (crashed)"
        else
            # Process is running, check its health
            local heartbeat_data=$(read_heartbeat)
            IFS='|' read -r pid idle_seconds is_processing_data heartbeat_age <<< "$heartbeat_data"
            
            if [ "$heartbeat_data" = "NO_HEARTBEAT" ] || [ "$pid" = "ERROR" ]; then
                should_restart=true
                restart_reason="No heartbeat detected (application may be frozen)"
            
            elif [ "$heartbeat_age" -gt 120 ]; then
                should_restart=true
                restart_reason="Heartbeat is stale (${heartbeat_age}s old)"
            
            elif [ "$idle_seconds" -gt "$IDLE_THRESHOLD" ] && [ "$is_processing_data" = "false" ]; then
                should_restart=true
                restart_reason="Application idle for too long (${idle_seconds}s > ${IDLE_THRESHOLD}s)"
            
            else
                # Check memory usage
                local memory_mb=$(check_memory_usage)
                if [ $? -ne 0 ]; then
                    should_restart=true
                    restart_reason="Memory usage too high or process error"
                else
                    # Everything looks good
                    log_message "✅ Application healthy - PID: $pid, Idle: ${idle_seconds}s, Memory: ${memory_mb}MB, Processing: $is_processing_data"
                fi
            fi
        fi
        
        # Restart if needed
        if [ "$should_restart" = true ]; then
            log_message "🔄 RESTART NEEDED: $restart_reason"
            
            # Kill existing processes
            log_message "Stopping existing processes..."
            pkill -f "python.*monitoring" 2>/dev/null || true
            sleep 3
            
            # Force kill if still running
            if check_process_running; then
                log_message "Force killing stubborn processes..."
                pkill -9 -f "python.*monitoring" 2>/dev/null || true
                sleep 2
            fi
            
            # Clean up lock files
            rm -f "$LOCK_FILE" "$HEARTBEAT_FILE"
            
            # Start application
            if start_application; then
                log_message "✅ Application restarted successfully"
            else
                log_message "❌ Failed to restart application, will try again next cycle"
            fi
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# Signal handlers
cleanup() {
    log_message "Smart watchdog shutting down..."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Ensure log file exists
touch "$WATCHDOG_LOG"

# Start main watchdog
main_watchdog 