#!/usr/bin/env python3
"""
Test script for logging table functionality with new cycle time and roll time fields.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitoring'))

from logging_table import LoggingTable

def test_logging_table():
    """Test the logging table with new timing fields."""
    print("Testing Logging Table with Cycle Time and Roll Time...")
    
    # Create a test logging table
    test_logs_dir = "test_logs"
    logging_table = LoggingTable(test_logs_dir)
    
    # Test data
    test_entries = [
        {
            'product_name': 'Test Product 1',
            'product_code': 'TP001',
            'product_length': 100.5,
            'batch': 'BATCH001',
            'cycle_time': 120.5,  # 2 minutes cycle time
            'roll_time': 45.2     # 45 seconds roll time
        },
        {
            'product_name': 'Test Product 2',
            'product_code': 'TP002',
            'product_length': 150.0,
            'batch': 'BATCH002',
            'cycle_time': 180.0,  # 3 minutes cycle time
            'roll_time': 60.0     # 1 minute roll time
        },
        {
            'product_name': 'Test Product 3',
            'product_code': 'TP003',
            'product_length': 75.25,
            'batch': 'BATCH003',
            'cycle_time': 90.0,   # 1.5 minutes cycle time
            'roll_time': 30.5     # 30.5 seconds roll time
        }
    ]
    
    # Add test entries
    for entry in test_entries:
        logging_table.log_production_data(
            product_name=entry['product_name'],
            product_code=entry['product_code'],
            product_length=entry['product_length'],
            batch=entry['batch'],
            cycle_time=entry['cycle_time'],
            roll_time=entry['roll_time']
        )
        print(f"Added entry: {entry['product_name']} - Cycle: {entry['cycle_time']}s, Roll: {entry['roll_time']}s")
    
    # Retrieve and display entries
    entries = logging_table.get_last_50_entries()
    print(f"\nRetrieved {len(entries)} entries:")
    
    for i, entry in enumerate(entries, 1):
        print(f"{i}. {entry['product_name']} ({entry['product_code']})")
        print(f"   Length: {entry['product_length']}m, Batch: {entry['batch']}")
        print(f"   Cycle Time: {entry['cycle_time']}s, Roll Time: {entry['roll_time']}s")
        print(f"   Timestamp: {entry['timestamp']}")
        print()
    
    # Clean up test directory
    import shutil
    if os.path.exists(test_logs_dir):
        shutil.rmtree(test_logs_dir)
        print(f"Cleaned up test directory: {test_logs_dir}")
    
    print("Logging table test completed successfully!")

if __name__ == "__main__":
    test_logging_table() 