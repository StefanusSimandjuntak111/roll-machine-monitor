#!/usr/bin/env python3
"""
Test untuk memverifikasi implementasi cycle time logic sesuai CYCLE_TIME.md
"""

import sys
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from monitoring.ui.main_window import ModernMainWindow
from monitoring.logging_table import LoggingTable

class TestCycleTimeLogic:
    """Test class untuk cycle time logic"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.main_window = ModernMainWindow()
        self.logging_table = LoggingTable()
        
    def setup_test_environment(self):
        """Setup test environment"""
        print("Setting up test environment...")
        
        # Clear any existing test data
        test_filename = self.logging_table.get_today_filename()
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        # Initialize monitoring with mock data
        self.main_window.config = {
            "serial_port": "COM4",
            "baudrate": 19200,
            "use_mock_data": True
        }
        
        # Mock logging_table_widget to avoid UI issues
        self.main_window.logging_table_widget = Mock()
        self.main_window.logging_table_widget.add_production_entry = Mock()
        self.main_window.logging_table_widget.update_last_entry_cycle_time = Mock()
        self.main_window.logging_table_widget.manual_refresh = Mock()
        
        print("Test environment ready")
        
    def test_cycle_time_logic(self):
        """Test cycle time logic sesuai CYCLE_TIME.md"""
        print("\n=== Testing Cycle Time Logic ===")
        
        self.setup_test_environment()
        
        # Test 1: Produk pertama - cycle_time harus null
        print("\n1. Testing first product (cycle_time should be null)")
        self.simulate_product_cycle("BD-1", "Baby Doll-1", 1.18, "1")
        
        # Verify first product has null cycle_time
        data = self.logging_table.load_today_data()
        assert len(data) == 1, f"Expected 1 entry, got {len(data)}"
        assert data[0]['cycle_time'] is None, f"First product cycle_time should be null, got {data[0]['cycle_time']}"
        print("✓ First product cycle_time is null")
        
        # Test 2: Produk kedua - produk pertama harus dapat cycle_time
        print("\n2. Testing second product (first product should get cycle_time)")
        self.simulate_product_cycle("BD-2", "Baby Doll-2", 1.18, "1")
        
        # Verify first product now has cycle_time
        data = self.logging_table.load_today_data()
        assert len(data) == 2, f"Expected 2 entries, got {len(data)}"
        assert data[0]['cycle_time'] is not None, "First product should now have cycle_time"
        assert data[1]['cycle_time'] is None, "Second product cycle_time should still be null"
        print(f"✓ First product cycle_time: {data[0]['cycle_time']:.1f}s")
        print(f"✓ Second product cycle_time: null")
        
        # Test 3: Produk ketiga - produk kedua harus dapat cycle_time
        print("\n3. Testing third product (second product should get cycle_time)")
        self.simulate_product_cycle("BD-3", "Baby Doll-3", 1.18, "1")
        
        # Verify second product now has cycle_time
        data = self.logging_table.load_today_data()
        assert len(data) == 3, f"Expected 3 entries, got {len(data)}"
        assert data[1]['cycle_time'] is not None, "Second product should now have cycle_time"
        assert data[2]['cycle_time'] is None, "Third product cycle_time should still be null"
        print(f"✓ Second product cycle_time: {data[1]['cycle_time']:.1f}s")
        print(f"✓ Third product cycle_time: null")
        
        # Test 4: Close Cycle - produk terakhir harus dapat cycle_time
        print("\n4. Testing Close Cycle (last product should get cycle_time)")
        self.simulate_close_cycle()
        
        # Verify last product now has cycle_time
        data = self.logging_table.load_today_data()
        assert data[2]['cycle_time'] is not None, "Last product should now have cycle_time"
        print(f"✓ Last product cycle_time: {data[2]['cycle_time']:.1f}s")
        
        # Test 5: Reset Counter - semua variabel harus reset
        print("\n5. Testing Reset Counter (all variables should reset)")
        self.simulate_reset_counter()
        
        # Verify variables are reset
        assert self.main_window.cycle_start_time is None, "cycle_start_time should be reset"
        assert self.main_window.roll_start_time is None, "roll_start_time should be reset"
        assert self.main_window.product_start_times == [], "product_start_times should be reset"
        assert self.main_window.is_new_product_started == False, "is_new_product_started should be reset"
        assert self.main_window.last_product_start_time is None, "last_product_start_time should be reset"
        print("✓ All cycle time variables reset")
        
        print("\n=== All Cycle Time Tests Passed! ===")
        
    def simulate_product_cycle(self, product_code, product_name, length, batch):
        """Simulate a complete product cycle"""
        print(f"  Simulating product cycle: {product_code}")
        
        # Simulate length = 1 (new product starts)
        mock_data = {
            'length_meters': 1.0,
            'unit': 'meter'
        }
        self.main_window.handle_production_logging(mock_data)
        time.sleep(0.1)  # Small delay to ensure timing
        
        # Simulate length = length (product completed)
        mock_data = {
            'length_meters': length,
            'unit': 'meter'
        }
        self.main_window.handle_production_logging(mock_data)
        time.sleep(0.1)
        
        # Simulate Print button click
            print_data = {
            'product_code': product_code,
            'product_name': product_name,
            'product_length': length,
            'batch': batch
        }
        self.main_window.handle_print_logging(print_data)
        time.sleep(0.1)
        
        # Simulate Reset Counter (except for last product)
        if product_code != "BD-3":  # Don't reset for last product
            self.simulate_reset_counter()
        
    def simulate_close_cycle(self):
        """Simulate Close Cycle button click"""
        print("  Simulating Close Cycle")
        self.main_window.close_cycle()
        time.sleep(0.1)
        
    def simulate_reset_counter(self):
        """Simulate Reset Counter button click"""
        print("  Simulating Reset Counter")
        # Mock the monitor to avoid serial port issues
        with patch.object(self.main_window, 'monitor') as mock_monitor:
            mock_monitor.is_running = True
            mock_monitor.serial_port = Mock()
            self.main_window.reset_counter()
        time.sleep(0.1)
        
    def cleanup(self):
        """Cleanup test environment"""
        print("\nCleaning up test environment...")
        
        # Remove test data file
        test_filename = self.logging_table.get_today_filename()
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        print("Cleanup completed")

def main():
    """Main test function"""
    print("Starting Cycle Time Logic Test")
    print("=" * 50)
    
    test = TestCycleTimeLogic()
    
    try:
        test.test_cycle_time_logic()
        print("\n🎉 All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        test.cleanup()
        print("\nTest completed")

if __name__ == "__main__":
    main() 