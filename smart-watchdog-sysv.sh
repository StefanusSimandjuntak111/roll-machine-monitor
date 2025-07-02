#!/bin/bash
# Smart Watchdog for Roll Machine Monitor (SysV/OpenRC/Universal)
# Works on any Linux system without systemd/systemctl

set -e

# Configuration
WATCHDOG_LOG="/var/log/rollmachine-smart-watchdog.log"
HEARTBEAT_FILE="/tmp/rollmachine_heartbeat"
LOCK_FILE="/tmp/rollmachine_monitor.lock"
PID_FILE="/var/run/rollmachine-watchdog.pid"
CHECK_INTERVAL=60  # Check every minute
IDLE_THRESHOLD=3600  # 1 hour in seconds
MAX_MEMORY_MB=2048  # Increased memory limit

APP_DIR="/opt/rollmachine-monitor/monitoring-roll-machine"
PYTHON_PATH="/opt/rollmachine-monitor/venv/bin/python"

# Try to find Python if venv doesn't exist
if [ ! -f "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python3 2>/dev/null || which python 2>/dev/null || echo "python3")
fi

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$WATCHDOG_LOG")"
mkdir -p "$(dirname "$PID_FILE")"

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
from datetime import datetime

try:
    with open('$HEARTBEAT_FILE', 'r') as f:
        data = json.load(f)
    
    # Calculate age of heartbeat
    try:
        from datetime import timezone
        heartbeat_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        
        if heartbeat_time.tzinfo is None:
            heartbeat_time = heartbeat_time.replace(tzinfo=timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
    except:
        # Fallback for older Python versions
        heartbeat_time = datetime.fromisoformat(data['timestamp'].split('T')[0] + ' ' + data['timestamp'].split('T')[1].split('.')[0])
        current_time = datetime.now()
    
    age_seconds = (current_time - heartbeat_time).total_seconds()
    
    print(f'{data[\"pid\"]}|{data[\"idle_seconds\"]}|{data[\"is_processing_data\"]}|{age_seconds}')
except Exception as e:
    print('ERROR|0|false|999999')
    sys.exit(1)
" 2>/dev/null || echo "ERROR|0|false|999999"
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
    
    # Check for recent restart attempts to prevent popup spam
    RESTART_FLAG="/tmp/rollmachine_restart_attempt"
    if [ -f "$RESTART_FLAG" ]; then
        restart_age=$(( $(date +%s) - $(stat -c %Y "$RESTART_FLAG" 2>/dev/null || echo "0") ))
        if [ "$restart_age" -lt 30 ]; then
            log_message "Recent restart attempt detected (${restart_age}s ago), skipping to prevent popup spam"
            return 1
        fi
    fi
    
    # Mark restart attempt
    date +%s > "$RESTART_FLAG"
    
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
        # Try common display values
        for display in :0 :1 :99; do
            if DISPLAY=$display timeout 2 xset q >/dev/null 2>&1; then
                export DISPLAY=$display
                log_message "Using display: $DISPLAY"
                break
            fi
        done
        
        # If no display found, set default
        if [ -z "$DISPLAY" ]; then
            export DISPLAY=:0
            log_message "No display detected, using default: $DISPLAY"
        fi
    fi
    
    # Start application in background
    nohup "$PYTHON_PATH" -m monitoring >> "$WATCHDOG_LOG" 2>&1 &
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

# Stop all application instances
stop_application() {
    log_message "Stopping Roll Machine Monitor..."
    
    # Send TERM signal first
    pkill -TERM -f "python.*monitoring" 2>/dev/null || true
    sleep 3
    
    # Check if still running
    if check_process_running; then
        log_message "Force killing remaining processes..."
        pkill -KILL -f "python.*monitoring" 2>/dev/null || true
        sleep 2
    fi
    
    # Clean up lock files
    rm -f "$LOCK_FILE" "$HEARTBEAT_FILE"
    
    log_message "Application stopped"
}

# Main watchdog logic
main_watchdog() {
    log_message "🚀 Starting Smart Watchdog for Roll Machine Monitor (Universal Mode)"
    log_message "📋 Configuration:"
    log_message "   - Check interval: ${CHECK_INTERVAL}s"
    log_message "   - Idle threshold: ${IDLE_THRESHOLD}s ($(($IDLE_THRESHOLD / 3600)) hour)"
    log_message "   - Memory limit: ${MAX_MEMORY_MB}MB"
    log_message "   - App directory: $APP_DIR"
    log_message "   - Python path: $PYTHON_PATH"
    log_message "   - PID file: $PID_FILE"
    log_message "   - No systemctl dependency"
    
    # Write our PID
    echo $$ > "$PID_FILE"
    
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
            
            elif [ "${heartbeat_age%.*}" -gt 120 ]; then  # Remove decimal part
                should_restart=true
                restart_reason="Heartbeat is stale (${heartbeat_age%.*}s old)"
            
            elif [ "${idle_seconds%.*}" -gt "$IDLE_THRESHOLD" ] && [ "$is_processing_data" = "false" ]; then
                should_restart=true
                restart_reason="Application idle for too long (${idle_seconds%.*}s > ${IDLE_THRESHOLD}s)"
            
            else
                # Check memory usage
                local memory_mb=$(check_memory_usage)
                if [ $? -ne 0 ]; then
                    should_restart=true
                    restart_reason="Memory usage too high or process error"
                else
                    # Everything looks good
                    log_message "✅ Application healthy - PID: $pid, Idle: ${idle_seconds%.*}s, Memory: ${memory_mb}MB, Processing: $is_processing_data"
                fi
            fi
        fi
        
        # Restart if needed
        if [ "$should_restart" = true ]; then
            log_message "🔄 RESTART NEEDED: $restart_reason"
            
            stop_application
            
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
    rm -f "$PID_FILE"
    exit 0
}

# Handle different signals
trap cleanup SIGTERM SIGINT SIGQUIT

# Commands
case "${1:-start}" in
    start)
        if [ -f "$PID_FILE" ]; then
            local old_pid=$(cat "$PID_FILE")
            if kill -0 "$old_pid" 2>/dev/null; then
                echo "Watchdog already running with PID $old_pid"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi
        
        echo "Starting Smart Watchdog..."
        main_watchdog &
        echo "Smart Watchdog started with PID $!"
        ;;
        
    stop)
        if [ -f "$PID_FILE" ]; then
            local pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping Smart Watchdog (PID: $pid)..."
                kill -TERM "$pid"
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid"
                fi
                rm -f "$PID_FILE"
                echo "Smart Watchdog stopped"
            else
                echo "Watchdog not running"
                rm -f "$PID_FILE"
            fi
        else
            echo "Watchdog not running (no PID file)"
        fi
        
        # Also stop application
        stop_application
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            local pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Smart Watchdog is running (PID: $pid)"
                
                # Check application status
                if check_process_running; then
                    local app_pid=$(pgrep -f "python.*monitoring" | head -1)
                    echo "Application is running (PID: $app_pid)"
                    
                    # Show heartbeat if available
                    if [ -f "$HEARTBEAT_FILE" ]; then
                        echo "Heartbeat:"
                        python3 -c "
import json
try:
    with open('$HEARTBEAT_FILE', 'r') as f:
        data = json.load(f)
    print(f'  PID: {data[\"pid\"]}')
    print(f'  Idle time: {data[\"idle_seconds\"]}s')
    print(f'  Processing: {data[\"is_processing_data\"]}')
except:
    print('  Could not read heartbeat data')
" 2>/dev/null || echo "  Heartbeat file corrupted"
                    else
                        echo "  No heartbeat file"
                    fi
                else
                    echo "Application is NOT running"
                fi
                exit 0
            else
                echo "Smart Watchdog is NOT running (stale PID file)"
                rm -f "$PID_FILE"
                exit 1
            fi
        else
            echo "Smart Watchdog is NOT running"
            exit 1
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Smart Watchdog for Roll Machine Monitor"
        echo "Works without systemctl on any Linux system"
        echo ""
        echo "Commands:"
        echo "  start   - Start the watchdog"
        echo "  stop    - Stop watchdog and application" 
        echo "  restart - Restart watchdog"
        echo "  status  - Show status"
        exit 1
        ;;
esac 