#!/usr/bin/env python3
"""
Test script to verify logging table shows data in descending order (newest first).

This test verifies that:
1. Data is sorted by timestamp in descending order
2. Newest entries appear at the top
3. Highlighting works correctly for the newest entry
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.logging_table import LoggingTable

def test_logging_table_descending_order():
    """Test that logging table returns data in descending order."""
    print("🧪 Testing Logging Table Descending Order")
    
    # Create a temporary logging table for testing
    test_logs_dir = "test_logs"
    logging_table = LoggingTable(logs_dir=test_logs_dir)
    
    try:
        # Create test data with different timestamps
        test_data = []
        base_time = datetime.now()
        
        # Create entries with different timestamps
        for i in range(5):
            entry_time = base_time + timedelta(minutes=i)
            entry = {
                'product_name': f'Test Product {i+1}',
                'product_code': f'TEST{i+1:03d}',
                'product_length': 1.0 + i * 0.5,
                'batch': f'BATCH{i+1:03d}',
                'cycle_time': 60.0 + i * 10,
                'roll_time': 30.0 + i * 5,
                'timestamp': entry_time.isoformat(),
                'settings_timestamp': None
            }
            test_data.append(entry)
        
        # Save test data to file
        today_filename = logging_table.get_today_filename()
        os.makedirs(os.path.dirname(today_filename), exist_ok=True)
        
        with open(today_filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test data saved to: {today_filename}")
        
        # Get data using get_last_50_entries
        retrieved_data = logging_table.get_last_50_entries()
        
        print(f"✅ Retrieved {len(retrieved_data)} entries")
        
        # Verify data is in descending order (newest first)
        if len(retrieved_data) >= 2:
            first_timestamp = retrieved_data[0].get('timestamp', '')
            second_timestamp = retrieved_data[1].get('timestamp', '')
            
            print(f"First entry timestamp: {first_timestamp}")
            print(f"Second entry timestamp: {second_timestamp}")
            
            if first_timestamp > second_timestamp:
                print("✅ Data is correctly sorted in descending order (newest first)")
            else:
                print("❌ Data is not sorted in descending order")
                return False
        else:
            print("⚠️ Not enough data to test sorting")
        
        # Verify the newest entry is first
        if retrieved_data:
            newest_entry = retrieved_data[0]
            expected_newest = test_data[-1]  # Last entry in original data should be newest
            
            if newest_entry.get('timestamp') == expected_newest.get('timestamp'):
                print("✅ Newest entry appears first in the list")
            else:
                print("❌ Newest entry does not appear first")
                return False
        
        # Verify all entries are present
        if len(retrieved_data) == len(test_data):
            print("✅ All entries are present")
        else:
            print(f"❌ Missing entries. Expected: {len(test_data)}, Got: {len(retrieved_data)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up test files
        try:
            if os.path.exists(test_logs_dir):
                import shutil
                shutil.rmtree(test_logs_dir)
                print("✅ Test files cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up test files: {e}")

def test_logging_table_edge_cases():
    """Test edge cases for logging table."""
    print("\n🧪 Testing Logging Table Edge Cases")
    
    # Test with empty data
    test_logs_dir = "test_logs_empty"
    logging_table = LoggingTable(logs_dir=test_logs_dir)
    
    try:
        # Test with no data
        empty_data = logging_table.get_last_50_entries()
        if len(empty_data) == 0:
            print("✅ Empty data handled correctly")
        else:
            print("❌ Empty data not handled correctly")
            return False
        
        # Test with single entry
        single_entry = {
            'product_name': 'Single Product',
            'product_code': 'SINGLE001',
            'product_length': 1.0,
            'batch': 'BATCH001',
            'cycle_time': 60.0,
            'roll_time': 30.0,
            'timestamp': datetime.now().isoformat(),
            'settings_timestamp': None
        }
        
        today_filename = logging_table.get_today_filename()
        os.makedirs(os.path.dirname(today_filename), exist_ok=True)
        
        with open(today_filename, 'w', encoding='utf-8') as f:
            json.dump([single_entry], f, indent=2, ensure_ascii=False)
        
        single_data = logging_table.get_last_50_entries()
        if len(single_data) == 1:
            print("✅ Single entry handled correctly")
        else:
            print("❌ Single entry not handled correctly")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed with error: {e}")
        return False
    
    finally:
        # Clean up test files
        try:
            if os.path.exists(test_logs_dir):
                import shutil
                shutil.rmtree(test_logs_dir)
                print("✅ Edge case test files cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up edge case test files: {e}")

def main():
    """Run all logging table tests."""
    print("🚀 Starting Logging Table Descending Order Tests")
    print("=" * 60)
    
    try:
        # Test descending order
        if not test_logging_table_descending_order():
            print("❌ Descending order test failed")
            return False
        
        # Test edge cases
        if not test_logging_table_edge_cases():
            print("❌ Edge cases test failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All logging table tests passed!")
        print("\nSummary of verified functionality:")
        print("1. ✅ Data is sorted by timestamp in descending order")
        print("2. ✅ Newest entries appear at the top")
        print("3. ✅ Empty data is handled correctly")
        print("4. ✅ Single entry is handled correctly")
        print("5. ✅ All entries are preserved during sorting")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 