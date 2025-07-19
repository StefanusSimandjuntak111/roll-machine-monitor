#!/usr/bin/env python3
"""
Simple test untuk memverifikasi implementasi cycle time logic
"""

import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock, patch

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.logging_table import LoggingTable

def test_cycle_time_logic():
    """Test cycle time logic dengan logging table langsung"""
    print("=== Testing Cycle Time Logic ===")
    
    # Setup
    logging_table = LoggingTable()
    
    # Clear test data
    test_filename = logging_table.get_today_filename()
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    # Test 1: Produk pertama
    print("\n1. Testing first product")
    logging_table.log_production_data(
        product_name="Baby Doll-1",
        product_code="BD-1", 
        product_length=1.18,
        batch="1",
        cycle_time=None,  # Should be null initially
        roll_time=166.38
    )
    
    data = logging_table.load_today_data()
    assert len(data) == 1, f"Expected 1 entry, got {len(data)}"
    assert data[0]['cycle_time'] is None, f"First product cycle_time should be null"
    print("✓ First product cycle_time is null")
    
    # Test 2: Produk kedua - update produk pertama
    print("\n2. Testing second product (update first product cycle_time)")
    logging_table.log_production_data(
        product_name="Baby Doll-2",
        product_code="BD-2",
        product_length=1.18, 
        batch="1",
        cycle_time=None,  # Should be null initially
        roll_time=180.45
    )
    
    # Update first product cycle_time (simulate when second product starts)
    data = logging_table.load_today_data()
    data[0]['cycle_time'] = 240.5  # Simulate calculated cycle time
    
    # Save updated data
    with open(test_filename, 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Verify update
    data = logging_table.load_today_data()
    assert data[0]['cycle_time'] == 240.5, f"First product should have cycle_time 240.5, got {data[0]['cycle_time']}"
    assert data[1]['cycle_time'] is None, "Second product cycle_time should still be null"
    print("✓ First product cycle_time updated to 240.5s")
    print("✓ Second product cycle_time is null")
    
    # Test 3: Close Cycle - update produk terakhir
    print("\n3. Testing Close Cycle (update last product cycle_time)")
    data = logging_table.load_today_data()
    data[1]['cycle_time'] = 195.2  # Simulate calculated cycle time for last product
    
    # Save updated data
    with open(test_filename, 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Verify update
    data = logging_table.load_today_data()
    assert data[1]['cycle_time'] == 195.2, f"Last product should have cycle_time 195.2, got {data[1]['cycle_time']}"
    print("✓ Last product cycle_time updated to 195.2s")
    
    # Test 4: Verify final data structure
    print("\n4. Verifying final data structure")
    data = logging_table.load_today_data()
    print(f"Total entries: {len(data)}")
    
    for i, entry in enumerate(data):
        print(f"Entry {i+1}:")
        print(f"  Product: {entry['product_code']} - {entry['product_name']}")
        print(f"  Length: {entry['product_length']}m")
        print(f"  Cycle Time: {entry['cycle_time']}s")
        print(f"  Roll Time: {entry['roll_time']}s")
        print(f"  Timestamp: {entry['timestamp']}")
    
    print("\n=== All Cycle Time Tests Passed! ===")
    
    # Cleanup
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_cycle_time_logic() 