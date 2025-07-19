#!/bin/bash
# SysV Init Script for Roll Machine Monitor
# Compatible with antiX, Alpine, and other non-systemd systems

### BEGIN INIT INFO
# Provides:          rollmachine-monitor
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Roll Machine Monitor Smart Watchdog
# Description:       Smart watchdog for Roll Machine Monitor with idle detection
### END INIT INFO

# Configuration
NAME="rollmachine-monitor"
DAEMON="/opt/rollmachine-monitor/smart-watchdog-sysv.sh"
PIDFILE="/var/run/rollmachine-watchdog.pid"
USER="kiosk"
DESC="Roll Machine Monitor Smart Watchdog"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if daemon exists
if [ ! -x "$DAEMON" ]; then
    print_error "Daemon not found: $DAEMON"
    exit 1
fi

# Function to start the service
do_start() {
    print_status "Starting $DESC..."
    
    # Check if already running
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "$NAME is already running (PID: $pid)"
            return 1
        else
            # Remove stale PID file
            rm -f "$PIDFILE"
        fi
    fi
    
    # Start the daemon
    if [ -n "$USER" ] && id "$USER" >/dev/null 2>&1; then
        # Run as specific user
        su - "$USER" -c "$DAEMON start" >/dev/null 2>&1
    else
        # Run as root
        "$DAEMON" start >/dev/null 2>&1
    fi
    
    # Check if started successfully
    sleep 2
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_status "$NAME started successfully (PID: $pid)"
            return 0
        fi
    fi
    
    print_error "Failed to start $NAME"
    return 1
}

# Function to stop the service
do_stop() {
    print_status "Stopping $DESC..."
    
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            # Use the daemon's stop command
            "$DAEMON" stop >/dev/null 2>&1
            
            # Wait for it to stop
            local count=0
            while [ $count -lt 10 ] && kill -0 "$pid" 2>/dev/null; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "Process did not stop gracefully, forcing..."
                kill -KILL "$pid" 2>/dev/null
                rm -f "$PIDFILE"
            fi
            
            print_status "$NAME stopped"
            return 0
        else
            print_warning "$NAME was not running"
            rm -f "$PIDFILE"
            return 0
        fi
    else
        print_warning "$NAME is not running (no PID file)"
        # Make sure no processes are running
        "$DAEMON" stop >/dev/null 2>&1
        return 0
    fi
}

# Function to restart the service
do_restart() {
    do_stop
    sleep 2
    do_start
}

# Function to get status
do_status() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_status "$NAME is running (PID: $pid)"
            
            # Get detailed status from daemon
            "$DAEMON" status
            return 0
        else
            print_error "$NAME is not running (stale PID file)"
            rm -f "$PIDFILE"
            return 1
        fi
    else
        print_error "$NAME is not running"
        return 1
    fi
}

# Function to enable auto-start (add to rc.local or similar)
do_enable() {
    print_status "Enabling auto-start for $NAME..."
    
    # Method 1: Try update-rc.d (Debian/Ubuntu)
    if command -v update-rc.d >/dev/null 2>&1; then
        update-rc.d rollmachine-monitor defaults
        print_status "Enabled via update-rc.d"
        return 0
    fi
    
    # Method 2: Try chkconfig (RedHat/CentOS)
    if command -v chkconfig >/dev/null 2>&1; then
        chkconfig --add rollmachine-monitor
        chkconfig rollmachine-monitor on
        print_status "Enabled via chkconfig"
        return 0
    fi
    
    # Method 3: Try rc-update (OpenRC - Alpine/Gentoo)
    if command -v rc-update >/dev/null 2>&1; then
        rc-update add rollmachine-monitor default
        print_status "Enabled via rc-update"
        return 0
    fi
    
    # Method 4: Fallback to rc.local
    local rc_local="/etc/rc.local"
    if [ -f "$rc_local" ]; then
        # Check if already added
        if ! grep -q "rollmachine-monitor" "$rc_local"; then
            # Backup rc.local
            cp "$rc_local" "$rc_local.backup"
            
            # Add before exit 0
            sed -i '/^exit 0/i # Start Roll Machine Monitor\n/etc/init.d/rollmachine-monitor start\n' "$rc_local"
            print_status "Added to $rc_local"
            return 0
        else
            print_status "Already in $rc_local"
            return 0
        fi
    fi
    
    # Method 5: Create simple startup script
    local startup_script="/etc/init.d/rollmachine-startup"
    cat > "$startup_script" << 'EOF'
#!/bin/bash
# Simple startup script for Roll Machine Monitor
/etc/init.d/rollmachine-monitor start
EOF
    chmod +x "$startup_script"
    print_status "Created startup script: $startup_script"
    print_warning "Please manually add to your system's startup mechanism"
}

# Function to disable auto-start
do_disable() {
    print_status "Disabling auto-start for $NAME..."
    
    # Method 1: Try update-rc.d
    if command -v update-rc.d >/dev/null 2>&1; then
        update-rc.d -f rollmachine-monitor remove
        print_status "Disabled via update-rc.d"
        return 0
    fi
    
    # Method 2: Try chkconfig
    if command -v chkconfig >/dev/null 2>&1; then
        chkconfig rollmachine-monitor off
        chkconfig --del rollmachine-monitor
        print_status "Disabled via chkconfig"
        return 0
    fi
    
    # Method 3: Try rc-update
    if command -v rc-update >/dev/null 2>&1; then
        rc-update del rollmachine-monitor default
        print_status "Disabled via rc-update"
        return 0
    fi
    
    # Method 4: Remove from rc.local
    local rc_local="/etc/rc.local"
    if [ -f "$rc_local" ]; then
        sed -i '/rollmachine-monitor/d' "$rc_local"
        print_status "Removed from $rc_local"
    fi
    
    print_status "Auto-start disabled"
}

# Main command handler
case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart|reload|force-reload)
        do_restart
        ;;
    status)
        do_status
        ;;
    enable)
        do_enable
        ;;
    disable)
        do_disable
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|enable|disable}" >&2
        echo ""
        echo "Roll Machine Monitor Init Script (Universal)"
        echo "Works on any Linux system without systemctl"
        echo ""
        echo "Commands:"
        echo "  start    - Start the service"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  status   - Show service status"
        echo "  enable   - Enable auto-start at boot"
        echo "  disable  - Disable auto-start at boot"
        exit 3
        ;;
esac

exit $? 