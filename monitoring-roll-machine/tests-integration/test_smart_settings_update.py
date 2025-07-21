#!/usr/bin/env python3
"""
Test Smart Settings Update Feature

This test verifies that:
1. Display settings (length tolerance, decimal format, rounding) update immediately without restart
2. Port settings (serial_port, baudrate) require restart
3. Settings changes only affect current and future data, not historical data
4. Length Print card updates immediately with new settings
5. Product form gets length print value (with tolerance) instead of raw length
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitoring'))

# Import after adding to path
try:
    from ui.main_window import ModernMainWindow
    from ui.product_form import ProductForm
    from ui.settings_dialog import SettingsDialog
except ImportError as e:
    print(f"Import error: {e}")
    print("Current sys.path:", sys.path)
    sys.exit(1)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

class TestSmartSettingsUpdate(unittest.TestCase):
    """Test Smart Settings Update functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up each test"""
        self.main_window = ModernMainWindow()
        self.product_form = ProductForm()
        
        # Mock config
        self.main_window.config = {
            'serial_port': 'COM4',
            'baudrate': 9600,
            'length_tolerance': 0.0,
            'decimal_points': 2,
            'rounding': 'round'
        }
        
        # Mock last_data
        self.main_window.last_data = {
            'fields': {
                'current_count': 10.5,
                'unit': 'meter'
            },
            'length_meters': 10.5,
            'unit': 'meter'
        }
        
        # Mock settings timestamp
        self.main_window.settings_changed_at = datetime.now()
    
    def tearDown(self):
        """Clean up after each test"""
        self.main_window.close()
        self.product_form.close()
    
    def test_needs_monitoring_restart(self):
        """Test if settings require monitoring restart"""
        # Display settings - should NOT require restart
        display_settings = {
            'length_tolerance': 5.0,
            'decimal_points': 3,
            'rounding': 'ceil'
        }
        self.assertFalse(self.main_window._needs_monitoring_restart(display_settings))
        
        # Port settings - should require restart
        port_settings = {
            'serial_port': 'COM5'
        }
        self.assertTrue(self.main_window._needs_monitoring_restart(port_settings))
        
        # Mixed settings - should require restart
        mixed_settings = {
            'length_tolerance': 5.0,
            'serial_port': 'COM5'
        }
        self.assertTrue(self.main_window._needs_monitoring_restart(mixed_settings))
    
    def test_display_settings_update_without_restart(self):
        """Test display settings update without restart"""
        # Mock product form
        self.main_window.product_form = self.product_form
        
        # Update display settings
        self.main_window._update_display_settings()
        
        # Verify settings timestamp was updated
        self.assertIsNotNone(self.main_window.settings_changed_at)
        
        # Verify handle_data was called with last_data
        # (This would be verified by checking if Length Print was updated)
    
    def test_product_form_length_print_update(self):
        """Test product form gets length print value with tolerance"""
        # Test with tolerance = 5%
        length_print_text = "9.98 m"  # 10.5 * (1 - 5/100) = 9.975, rounded to 2 decimals
        
        # Update product form with length print
        self.product_form.update_target_with_length_print(length_print_text)
        
        # Verify target length was updated with extracted value
        self.assertEqual(self.product_form.target_length.value(), 9.98)
    
    def test_length_print_extraction(self):
        """Test extraction of numeric value from length print text"""
        test_cases = [
            ("9.98 m", 9.98),
            ("15.5 yard", 15.5),
            ("0.123 m", 0.123),
            ("100 m", 100.0),
            ("Invalid text", None)  # Should handle invalid text gracefully
        ]
        
        for length_print_text, expected_value in test_cases:
            with self.subTest(length_print_text=length_print_text):
                # Reset target length
                self.product_form.target_length.setValue(0.0)
                
                # Update with length print text
                self.product_form.update_target_with_length_print(length_print_text)
                
                if expected_value is not None:
                    self.assertEqual(self.product_form.target_length.value(), expected_value)
                else:
                    # Should remain unchanged for invalid text
                    self.assertEqual(self.product_form.target_length.value(), 0.0)
    
    def test_settings_timestamp_storage(self):
        """Test that settings timestamp is stored when logging data"""
        # Mock logging table widget
        mock_logging_widget = Mock()
        self.main_window.logging_table_widget = mock_logging_widget
        
        # Mock print data
        print_data = {
            'product_name': 'Test Product',
            'product_code': 'TEST001',
            'product_length': 10.5,
            'batch': 'BATCH001'
        }
        
        # Call handle_print_logging
        self.main_window.handle_print_logging(print_data)
        
        # Verify add_production_entry was called with settings timestamp
        mock_logging_widget.add_production_entry.assert_called_once()
        call_args = mock_logging_widget.add_production_entry.call_args
        
        # Check that settings_timestamp parameter was passed
        self.assertIn('settings_timestamp', call_args.kwargs)
        self.assertIsNotNone(call_args.kwargs['settings_timestamp'])
    
    def test_calculate_length_print_with_tolerance(self):
        """Test length print calculation with tolerance"""
        # Test with 5% tolerance, 2 decimal places, round
        self.main_window.config['length_tolerance'] = 5.0
        self.main_window.config['decimal_points'] = 2
        self.main_window.config['rounding'] = 'round'
        
        # Calculate length print
        result = self.main_window.calculate_length_print(10.5, 'meter')
        
        # Expected: 10.5 * (1 - 5/100) = 9.975, rounded to 2 decimals = 9.98
        self.assertEqual(result, "9.98 m")
        
        # Test with ceil rounding
        self.main_window.config['rounding'] = 'ceil'
        result = self.main_window.calculate_length_print(10.5, 'meter')
        self.assertEqual(result, "9.98 m")  # 9.975 ceiled to 2 decimals = 9.98
        
        # Test with floor rounding
        self.main_window.config['rounding'] = 'floor'
        result = self.main_window.calculate_length_print(10.5, 'meter')
        self.assertEqual(result, "9.97 m")  # 9.975 floored to 2 decimals = 9.97
    
    def test_settings_update_messages(self):
        """Test appropriate messages for different types of settings updates"""
        # Mock show_kiosk_dialog
        self.main_window.show_kiosk_dialog = Mock()
        
        # Test display settings update
        display_settings = {'length_tolerance': 5.0}
        self.main_window.handle_settings_update(display_settings)
        
        # Verify correct message for display settings
        self.main_window.show_kiosk_dialog.assert_called_with(
            "information",
            "Settings Updated",
            "Display settings have been updated successfully!\n\nLength tolerance and formatting are now active.\n\nNew settings apply to current and future products only.\n\nNo connection interruption."
        )
        
        # Reset mock
        self.main_window.show_kiosk_dialog.reset_mock()
        
        # Test port settings update (mock kill_port_connection and toggle_monitoring)
        self.main_window.kill_port_connection = Mock()
        self.main_window.toggle_monitoring = Mock()
        
        port_settings = {'serial_port': 'COM5'}
        self.main_window.handle_settings_update(port_settings)
        
        # Verify correct message for port settings
        self.main_window.show_kiosk_dialog.assert_called_with(
            "information",
            "Settings Updated",
            "Port settings have been updated.\n\nMonitoring has been restarted with new configuration.\n\nNew settings will apply to current and future products only."
        )

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 