#!/usr/bin/env python3
"""
Test untuk memverifikasi cycle time logic di main window sesuai alur aplikasi nyata
"""

import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock, patch

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from monitoring.ui.main_window import ModernMainWindow
from monitoring.logging_table import LoggingTable

def test_main_window_cycle_time():
    """Test cycle time logic di main window"""
    print("=== Testing Main Window Cycle Time Logic ===")
    
    # Setup QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Create main window
    main_window = ModernMainWindow()
    
    # Setup test environment
    logging_table = LoggingTable()
    
    # Clear test data
    test_filename = logging_table.get_today_filename()
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    # Mock logging_table_widget
    main_window.logging_table_widget = Mock()
    main_window.logging_table_widget.add_production_entry = Mock()
    main_window.logging_table_widget.update_last_entry_cycle_time = Mock()
    main_window.logging_table_widget.manual_refresh = Mock()
    
    print("\n1. Testing Product 1 - Length = 1 (New Product Start)")
    
    # Simulate length = 1 (new product starts)
    mock_data_1 = {
        'length_meters': 1.0,
        'unit': 'meter'
    }
    main_window.handle_production_logging(mock_data_1)
    
    # Verify new product started
    assert main_window.is_new_product_started == True, "is_new_product_started should be True"
    assert main_window.last_product_start_time is not None, "last_product_start_time should be set"
    print("   ✓ New product cycle started (length = 1)")
    
    print("\n2. Testing Product 1 - Print")
    
    # Simulate Print for Product 1
    print_data_1 = {
        'product_code': 'BD-1',
        'product_name': 'Baby Doll-1',
        'product_length': 1.18,
        'batch': '1'
    }
    main_window.handle_print_logging(print_data_1)
    
    # Verify product was logged with null cycle_time
    main_window.logging_table_widget.add_production_entry.assert_called()
    call_args = main_window.logging_table_widget.add_production_entry.call_args
    assert call_args[1]['product_name'] == 'Baby Doll-1'
    assert call_args[1]['product_code'] == 'BD-1'
    assert call_args[1]['product_length'] == 1.18
    assert call_args[1]['batch'] == '1'
    assert call_args[1]['cycle_time'] is None  # Should be null
    assert call_args[1]['roll_time'] >= 0  # Should be positive
    print("   ✓ Product 1 printed with cycle_time = null")
    
    print("\n3. Testing Reset Counter")
    
    # Mock monitor for reset counter
    with patch.object(main_window, 'monitor') as mock_monitor:
        mock_monitor.is_running = True
        mock_monitor.serial_port = Mock()
        main_window.reset_counter()
    
    # Verify variables reset
    assert main_window.cycle_start_time is None, "cycle_start_time should be reset"
    assert main_window.roll_start_time is None, "roll_start_time should be reset"
    # product_start_times and last_product_start_time are NOT reset (needed for cycle time calculation)
    assert main_window.is_new_product_started == False, "is_new_product_started should be reset"
    print("   ✓ All variables reset after Reset Counter")
    
    print("\n4. Testing Product 2 - Length = 1 (Should Update Product 1 Cycle Time)")
    
    # Simulate length = 1 for Product 2 (should trigger cycle time update for Product 1)
    mock_data_2 = {
        'length_meters': 1.0,
        'unit': 'meter'
    }
    main_window.handle_production_logging(mock_data_2)
    
    # Debug: Check variables
    print(f"   Debug: is_new_product_started = {main_window.is_new_product_started}")
    print(f"   Debug: product_start_times length = {len(main_window.product_start_times)}")
    print(f"   Debug: last_product_start_time = {main_window.last_product_start_time}")
    
    # Verify new product started
    assert main_window.is_new_product_started == True, "is_new_product_started should be True"
    assert main_window.last_product_start_time is not None, "last_product_start_time should be set"
    print("   ✓ New product cycle started (length = 1)")
    
    # Verify cycle time update was called (for Product 1)
    main_window.logging_table_widget.update_last_entry_cycle_time.assert_called()
    print("   ✓ Product 1 cycle_time automatically updated")
    
    print("\n5. Testing Product 2 - Print")
    
    # Simulate Print for Product 2
    print_data_2 = {
        'product_code': 'BD-2',
        'product_name': 'Baby Doll-2',
        'product_length': 1.18,
        'batch': '1'
    }
    main_window.handle_print_logging(print_data_2)
    
    # Verify product was logged with null cycle_time
    main_window.logging_table_widget.add_production_entry.assert_called()
    call_args = main_window.logging_table_widget.add_production_entry.call_args
    assert call_args[1]['product_name'] == 'Baby Doll-2'
    assert call_args[1]['product_code'] == 'BD-2'
    assert call_args[1]['product_length'] == 1.18
    assert call_args[1]['batch'] == '1'
    assert call_args[1]['cycle_time'] is None  # Should be null
    assert call_args[1]['roll_time'] >= 0  # Should be positive
    print("   ✓ Product 2 printed with cycle_time = null")
    
    print("\n6. Testing Product 3 - Length = 1 (Should Update Product 2 Cycle Time)")
    
    # Reset for Product 3
    with patch.object(main_window, 'monitor') as mock_monitor:
        mock_monitor.is_running = True
        mock_monitor.serial_port = Mock()
        main_window.reset_counter()
    
    # Simulate length = 1 for Product 3 (should trigger cycle time update for Product 2)
    mock_data_3 = {
        'length_meters': 1.0,
        'unit': 'meter'
    }
    main_window.handle_production_logging(mock_data_3)
    
    # Verify cycle time update was called again (for Product 2)
    assert main_window.logging_table_widget.update_last_entry_cycle_time.call_count >= 2
    print("   ✓ Product 2 cycle_time automatically updated")
    
    print("\n7. Testing Close Cycle")
    
    # Simulate Close Cycle
    main_window.close_cycle()
    
    # Verify cycle time update was called for last product
    assert main_window.logging_table_widget.update_last_entry_cycle_time.call_count >= 3
    print("   ✓ Last product cycle_time updated with Close Cycle")
    
    print("\n8. Final Verification")
    
    # Verify all variables reset after Close Cycle
    assert main_window.cycle_start_time is None, "cycle_start_time should be reset"
    assert main_window.roll_start_time is None, "roll_start_time should be reset"
    # product_start_times and last_product_start_time are NOT reset (needed for cycle time calculation)
    assert main_window.is_new_product_started == False, "is_new_product_started should be reset"
    print("   ✓ All variables reset after Close Cycle")
    
    # Verify total calls
    total_cycle_time_updates = main_window.logging_table_widget.update_last_entry_cycle_time.call_count
    print(f"   Total cycle time updates: {total_cycle_time_updates}")
    assert total_cycle_time_updates >= 3, f"Expected at least 3 cycle time updates, got {total_cycle_time_updates}"
    
    print("\n=== All Main Window Cycle Time Tests Passed! ===")
    
    # Cleanup
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("Main window test completed successfully!")

if __name__ == "__main__":
    test_main_window_cycle_time() 