#!/bin/bash
# Exit Kiosk Mode Script
# This script will signal the application to exit kiosk mode

echo "🚪 Exiting Roll Machine Monitor Kiosk Mode..."

# Create exit flag
touch /tmp/exit_kiosk_mode

echo "✅ Exit signal sent. Application will exit within 10 seconds."
echo "   If application doesn't exit, try:"
echo "   sudo pkill -f 'python.*monitoring'"

# Optional: Kill application directly after 15 seconds
sleep 15
if pgrep -f "python.*monitoring" > /dev/null; then
    echo "🔨 Force killing application..."
    sudo pkill -f "python.*monitoring"
    echo "✅ Application terminated"
fi 