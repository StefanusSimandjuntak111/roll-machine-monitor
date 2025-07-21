#!/usr/bin/env python3
"""
Test script for the port kill functionality to fix permission errors.
"""
import sys
import os
import time

# Add the parent directory to the path to import monitoring module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PySide6.QtWidgets import QApplication
from monitoring.ui.main_window import ModernMainWindow
from monitoring.config import get_default_config

def test_port_kill_functionality():
    """Test the port kill functionality."""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = ModernMainWindow()
    
    print("🧪 Testing Port Kill Functionality")
    print("=" * 40)
    
    # Test 1: Force kill COM port method
    print("\n📋 Test 1: Force kill COM port")
    try:
        main_window.force_kill_com_port("COM4")
        print("✅ Force kill COM port method executed successfully")
    except Exception as e:
        print(f"❌ Force kill COM port failed: {e}")
    
    # Test 2: Kill port connection method
    print("\n📋 Test 2: Kill port connection")
    try:
        main_window.kill_port_connection()
        print("✅ Kill port connection method executed successfully")
    except Exception as e:
        print(f"❌ Kill port connection failed: {e}")
    
    # Test 3: Simulate settings update with port kill
    print("\n📋 Test 3: Simulate settings update")
    try:
        # Set a test port
        main_window.config.update({"serial_port": "COM4"})
        
        # Simulate settings update
        test_settings = {
            "serial_port": "COM4",
            "baudrate": 19200,
            "length_tolerance": 5.0,
            "decimal_points": 2,
            "rounding": "UP"
        }
        
        print("Simulating settings update with port kill...")
        main_window.handle_settings_update(test_settings)
        print("✅ Settings update with port kill executed successfully")
        
    except Exception as e:
        print(f"❌ Settings update failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Port kill functionality test completed!")

def test_windows_specific_commands():
    """Test Windows-specific commands for port management."""
    print("\n🧪 Testing Windows-Specific Commands")
    print("=" * 40)
    
    import platform
    if platform.system() != "Windows":
        print("⚠️  Windows-specific tests skipped (not on Windows)")
        return
    
    import subprocess
    
    # Test 1: Check available COM ports
    print("\n📋 Test 1: Check available COM ports")
    try:
        result = subprocess.run('mode', shell=True, capture_output=True, text=True, timeout=5)
        if result.stdout:
            print("✅ Mode command executed successfully")
            # Look for COM ports in output
            lines = result.stdout.split('\n')
            com_ports = [line for line in lines if 'COM' in line]
            if com_ports:
                print(f"Found COM ports: {com_ports[:3]}")  # Show first 3
            else:
                print("No COM ports found in mode output")
        else:
            print("⚠️  Mode command returned no output")
    except Exception as e:
        print(f"❌ Mode command failed: {e}")
    
    # Test 2: Check netstat for COM ports
    print("\n📋 Test 2: Check netstat for COM ports")
    try:
        result = subprocess.run('netstat -ano | findstr COM', shell=True, capture_output=True, text=True, timeout=10)
        if result.stdout:
            print("✅ Netstat command executed successfully")
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                print(f"Found {len(lines)} COM port connections")
                for line in lines[:3]:  # Show first 3
                    print(f"  {line}")
            else:
                print("No COM port connections found")
        else:
            print("No COM port connections found in netstat")
    except Exception as e:
        print(f"❌ Netstat command failed: {e}")
    
    # Test 3: Test taskkill command (without actually killing)
    print("\n📋 Test 3: Test taskkill command structure")
    try:
        # Just test the command structure, don't actually kill anything
        test_cmd = 'taskkill /PID 999999 /F'  # Non-existent PID
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=5)
        if "not found" in result.stderr or "does not exist" in result.stderr:
            print("✅ Taskkill command structure is correct")
        else:
            print("⚠️  Taskkill command returned unexpected result")
    except Exception as e:
        print(f"❌ Taskkill command test failed: {e}")

if __name__ == "__main__":
    print("🚀 Port Kill Fix Test")
    print("=" * 30)
    
    # Run main tests
    test_port_kill_functionality()
    
    # Run Windows-specific tests
    test_windows_specific_commands()
    
    print("\n✅ All tests completed!")
    print("\n💡 Note: This test verifies the port kill functionality.")
    print("   The actual port killing will happen when you save settings.")
    print("   If you still get permission errors, try:")
    print("   1. Close any other applications using the COM port")
    print("   2. Restart the monitoring application")
    print("   3. Check Device Manager for port conflicts") 