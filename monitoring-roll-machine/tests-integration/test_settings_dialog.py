#!/usr/bin/env python3
"""
Test script for the new tabbed settings dialog.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QDialog
from monitoring.ui.settings_dialog import SettingsDialog
from monitoring.config import get_default_config

def test_settings_dialog():
    """Test the new settings dialog with tabs."""
    app = QApplication(sys.argv)
    
    # Load default config
    config = get_default_config()
    print("Default config:", config)
    
    # Create and show settings dialog
    dialog = SettingsDialog(config)
    dialog.show()
    
    # Connect to settings updated signal
    def on_settings_updated(settings):
        print("Settings updated:", settings)
        print("Length tolerance:", settings.get("length_tolerance"))
        print("Decimal points:", settings.get("decimal_points"))
        print("Rounding:", settings.get("rounding"))
    
    dialog.settings_updated.connect(on_settings_updated)
    
    # Run the dialog
    result = dialog.exec()
    
    if result == 1:  # QDialog.Accepted
        print("Settings saved successfully")
    else:
        print("Settings dialog cancelled")
    
    return result

if __name__ == "__main__":
    test_settings_dialog() 