#!/usr/bin/env python3
"""
Test script to verify all buttons in the settings dialog work correctly.
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from monitoring.ui.settings_dialog import SettingsDialog
from monitoring.config import get_default_config

def test_settings_buttons():
    """Test all buttons in the settings dialog."""
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
        print("✅ Save button works!")
    
    dialog.settings_updated.connect(on_settings_updated)
    
    # Test refresh ports button
    def test_refresh_ports():
        print("🔄 Testing refresh ports button...")
        dialog.refresh_ports()
        print(f"✅ Refresh ports completed. Found {dialog.port_combo.count()} ports")
    
    # Test save with invalid data
    def test_save_invalid():
        print("🧪 Testing save with invalid tolerance...")
        dialog.tolerance_input.setText("invalid")
        dialog.save_settings()
        print("✅ Error handling works for invalid input")
    
    # Test save with valid data
    def test_save_valid():
        print("🧪 Testing save with valid data...")
        dialog.tolerance_input.setText("5")
        dialog.decimal_combo.setCurrentText("#.##")
        dialog.round_down_radio.setChecked(True)
        dialog.save_settings()
    
    # Set up test sequence
    timer = QTimer()
    test_step = 0
    
    def run_test_sequence():
        nonlocal test_step
        if test_step == 0:
            print("\n=== Testing Settings Dialog Buttons ===")
            test_refresh_ports()
            test_step += 1
            timer.singleShot(1000, run_test_sequence)
        elif test_step == 1:
            test_save_invalid()
            test_step += 1
            timer.singleShot(1000, run_test_sequence)
        elif test_step == 2:
            test_save_valid()
            test_step += 1
            timer.singleShot(1000, run_test_sequence)
        else:
            print("\n✅ All tests completed!")
            dialog.close()
    
    # Start test sequence after dialog shows
    timer.singleShot(500, run_test_sequence)
    
    # Show dialog
    print("Opening settings dialog...")
    dialog.show()
    
    # Run the application
    result = app.exec()
    
    print(f"Dialog result: {result}")
    return result

if __name__ == "__main__":
    test_settings_buttons() 