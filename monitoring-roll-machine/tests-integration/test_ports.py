#!/usr/bin/env python3
"""
Test script to check which COM ports are accessible.
"""
import serial
import serial.tools.list_ports
import time

def test_port_app_style(port_name, baudrate=19200, timeout=1.0):
    """Test if a port can be opened with exact app parameters."""
    try:
        print(f"Testing {port_name} (app style)...", end=" ")
        ser = serial.Serial(
            port=port_name,
            baudrate=baudrate,
            timeout=timeout
        )
        
        # Test if we can write/read (like the app does)
        ser.reset_input_buffer()
        ser.close()
        print("✓ SUCCESS")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_port_simple(port_name, baudrate=19200):
    """Test if a port can be opened with simple parameters."""
    try:
        print(f"Testing {port_name} (simple)...", end=" ")
        ser = serial.Serial(port_name, baudrate, timeout=1)
        ser.close()
        print("✓ SUCCESS")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def main():
    """Test all available COM ports."""
    print("=" * 50)
    print("COM Port Accessibility Test")
    print("=" * 50)
    
    # Get all available ports
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No COM ports detected!")
        return
    
    print(f"Found {len(ports)} port(s):")
    for port in ports:
        print(f"  - {port.device}: {port.description}")
    print()
    
    # Test each port with different methods
    working_ports = []
    for port in ports:
        print(f"\n--- Testing {port.device} ---")
        
        # Test simple method
        if test_port_simple(port.device):
            working_ports.append(port.device)
            print(f"  ✓ {port.device} works with simple method")
        else:
            print(f"  ✗ {port.device} failed with simple method")
        
        # Test app-style method
        if test_port_app_style(port.device):
            print(f"  ✓ {port.device} works with app-style method")
        else:
            print(f"  ✗ {port.device} failed with app-style method")
    
    print("\n" + "=" * 50)
    if working_ports:
        print(f"✓ Working ports: {', '.join(working_ports)}")
        print("\nRecommendation:")
        print(f"  Use port: {working_ports[0]}")
        print("\nTo configure in the application:")
        print("  1. Open the application")
        print("  2. Go to Settings")
        print(f"  3. Set Serial Port to: {working_ports[0]}")
        
        # Check if there might be a timing issue
        print("\nIf app still fails, try:")
        print("  1. Close all other applications using COM ports")
        print("  2. Restart the monitoring application")
        print("  3. Try running as Administrator")
    else:
        print("✗ No working ports found!")
        print("\nTroubleshooting:")
        print("  1. Check if device is properly connected")
        print("  2. Install/update CH340 drivers")
        print("  3. Try different USB cable")
        print("  4. Restart computer")
    print("=" * 50)

if __name__ == "__main__":
    main() 