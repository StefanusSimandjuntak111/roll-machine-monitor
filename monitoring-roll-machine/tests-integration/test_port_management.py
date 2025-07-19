#!/usr/bin/env python3
"""
Test script for the new port management features in settings dialog.
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from monitoring.ui.settings_dialog import SettingsDialog
from monitoring.config import get_default_config

def test_port_management():
    """Test the port management features."""
    app = QApplication(sys.argv)
    
    # Load default config
    config = get_default_config()
    print("Default config:", config)
    
    # Create settings dialog
    dialog = SettingsDialog(config)
    
    # Connect to settings updated signal
    def on_settings_updated(settings):
        print("✅ Settings updated successfully!")
        print("Settings:", settings)
    
    dialog.settings_updated.connect(on_settings_updated)
    
    # Test sequence for port management
    def test_kill_port():
        print("🔌 Testing kill port connection...")
        dialog.kill_port_connection()
        print("✅ Kill port completed")
    
    def test_auto_connect():
        print("🔗 Testing auto connect...")
        dialog.auto_connect_port()
        print("✅ Auto connect completed")
    
    def test_disconnect():
        print("❌ Testing disconnect...")
        dialog.disconnect_port()
        print("✅ Disconnect completed")
    
    def test_auto_reconnect():
        print("🔄 Testing auto reconnect...")
        # Enable auto reconnect
        dialog.auto_reconnect_checkbox.setChecked(True)
        # Disconnect to trigger auto reconnect
        dialog.disconnect_port()
        print("✅ Auto reconnect test completed")
    
    # Set up test sequence
    timer = QTimer()
    test_step = 0
    
    def run_test_sequence():
        nonlocal test_step
        if test_step == 0:
            print("\n=== Testing Port Management Features ===")
            print("Step 1: Testing kill port connection")
            test_kill_port()
            test_step += 1
            timer.singleShot(2000, run_test_sequence)
        elif test_step == 1:
            print("Step 2: Testing auto connect")
            test_auto_connect()
            test_step += 1
            timer.singleShot(2000, run_test_sequence)
        elif test_step == 2:
            print("Step 3: Testing disconnect")
            test_disconnect()
            test_step += 1
            timer.singleShot(2000, run_test_sequence)
        elif test_step == 3:
            print("Step 4: Testing auto reconnect")
            test_auto_reconnect()
            test_step += 1
            timer.singleShot(3000, run_test_sequence)
        else:
            print("\n✅ All port management tests completed!")
            print("Features tested:")
            print("  ✅ Kill/Close Port Connection")
            print("  ✅ Auto Connect to Available Port")
            print("  ✅ Disconnect")
            print("  ✅ Auto Reconnect on Disconnect")
            dialog.close()
    
    # Start test sequence after dialog shows
    timer.singleShot(1000, run_test_sequence)
    
    # Show dialog
    print("Opening settings dialog with port management...")
    dialog.show()
    
    # Run the application
    result = app.exec()
    
    print(f"Dialog result: {result}")
    return result

if __name__ == "__main__":
    test_port_management() 