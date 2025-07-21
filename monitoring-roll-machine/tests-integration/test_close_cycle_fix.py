#!/usr/bin/env python3
"""
Test for Close Cycle button fix:
- State tracking for cycle closed
- Button disable after close cycle
- Counter reset after close cycle
- Button enable when new data arrives
"""

import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock, patch

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def test_close_cycle_state_management():
    """Test the complete close cycle state management flow."""
    print("🧪 Testing Close Cycle State Management")
    
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from monitoring.ui.main_window import ModernMainWindow
        
        # Create main window
        window = ModernMainWindow()
        
        print("\n1. Initial State Check")
        # Check initial state
        assert window.cycle_is_closed == False, "Initial cycle_is_closed should be False"
        assert window.product_form.close_cycle_button.isEnabled() == True, "Close cycle button should be enabled initially"
        print("   ✓ Initial state correct")
        
        print("\n2. Simulating Close Cycle")
        # Simulate close cycle
        window.close_cycle()
        
        # Check state after close cycle
        assert window.cycle_is_closed == True, "cycle_is_closed should be True after close cycle"
        assert window.product_form.close_cycle_button.isEnabled() == False, "Close cycle button should be disabled"
        assert window.product_form.close_cycle_button.text() == "Cycle Closed", "Button text should be 'Cycle Closed'"
        print("   ✓ Close cycle state correct")
        
        print("\n3. Testing Counter Reset")
        # Check that counters are reset
        assert window.cycle_start_time is None, "cycle_start_time should be reset"
        assert window.roll_start_time is None, "roll_start_time should be reset"
        assert window.last_length == 0.0, "last_length should be reset to 0.0"
        assert window.current_product_info == {}, "current_product_info should be reset"
        assert window.product_start_times == [], "product_start_times should be reset"
        assert window.last_product_start_time is None, "last_product_start_time should be reset"
        assert window.is_new_product_started == False, "is_new_product_started should be reset"
        print("   ✓ All counters reset correctly")
        
        print("\n4. Testing Duplicate Close Cycle")
        # Try to close cycle again (should be ignored)
        window.close_cycle()
        
        # State should remain the same
        assert window.cycle_is_closed == True, "cycle_is_closed should remain True"
        assert window.product_form.close_cycle_button.isEnabled() == False, "Button should remain disabled"
        print("   ✓ Duplicate close cycle ignored")
        
        print("\n5. Testing New Data Arrival")
        # Simulate new data arrival
        mock_data = {
            'length_meters': 0.5,
            'speed_mps': 1.2,
            'unit': 'meter',
            'current_count': 0.5,
            'current_speed': 72.0
        }
        
        window.handle_data(mock_data)
        
        # Check that button is enabled again
        assert window.cycle_is_closed == False, "cycle_is_closed should be False after new data"
        assert window.product_form.close_cycle_button.isEnabled() == True, "Close cycle button should be enabled"
        assert window.product_form.close_cycle_button.text() == "Close Cycle", "Button text should be 'Close Cycle'"
        print("   ✓ Button enabled after new data")
        
        print("\n6. Testing Complete Flow")
        # Test complete flow: close cycle again
        window.close_cycle()
        assert window.cycle_is_closed == True, "cycle_is_closed should be True again"
        assert window.product_form.close_cycle_button.isEnabled() == False, "Button should be disabled again"
        
        # Simulate more data
        window.handle_data(mock_data)
        assert window.cycle_is_closed == False, "cycle_is_closed should be False again"
        assert window.product_form.close_cycle_button.isEnabled() == True, "Button should be enabled again"
        print("   ✓ Complete flow works correctly")
        
        print("\n✅ All Close Cycle State Management Tests Passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        if 'window' in locals():
            window.close()

def test_close_cycle_with_logging():
    """Test close cycle with actual logging table integration."""
    print("\n🧪 Testing Close Cycle with Logging Integration")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from monitoring.ui.main_window import ModernMainWindow
        
        # Create main window
        window = ModernMainWindow()
        
        print("\n1. Setup Mock Logging")
        # Mock the logging table widget
        mock_logging_widget = Mock()
        window.logging_table_widget = mock_logging_widget
        
        print("\n2. Simulate Product Data")
        # Simulate some product data first
        mock_data = {
            'length_meters': 0.01,  # Trigger new product start
            'speed_mps': 1.2,
            'unit': 'meter',
            'current_count': 0.01,
            'current_speed': 72.0
        }
        
        # Set up timing for cycle time calculation
        window.last_product_start_time = datetime.now()
        time.sleep(0.1)  # Small delay to ensure time difference
        
        print("\n3. Test Close Cycle with Logging")
        # Close cycle
        window.close_cycle()
        
        # Check that logging was called
        assert mock_logging_widget.update_last_entry_cycle_time.called, "Logging update should be called"
        print("   ✓ Logging integration works")
        
        print("\n4. Verify State After Close")
        assert window.cycle_is_closed == True, "cycle_is_closed should be True"
        assert window.product_form.close_cycle_button.isEnabled() == False, "Button should be disabled"
        print("   ✓ State correct after close cycle")
        
        print("\n✅ Close Cycle Logging Integration Test Passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'window' in locals():
            window.close()

if __name__ == "__main__":
    print("🚀 Starting Close Cycle Fix Tests")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_close_cycle_state_management()
    success &= test_close_cycle_with_logging()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All Close Cycle Fix Tests Passed!")
        sys.exit(0)
    else:
        print("💥 Some Close Cycle Fix Tests Failed!")
        sys.exit(1) 