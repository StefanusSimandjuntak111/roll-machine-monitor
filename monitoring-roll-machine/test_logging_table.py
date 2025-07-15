#!/usr/bin/env python3
"""
Test script untuk menambahkan data contoh ke logging table.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from monitoring.logging_table import LoggingTable

def add_sample_data():
    """Add sample production data to logging table."""
    logging_table = LoggingTable()
    
    # Sample product data
    products = [
        {"name": "Kain Cotton Premium", "code": "CTN-001", "length": 150.5, "batch": "BATCH-2024-001"},
        {"name": "Kain Polyester Mix", "code": "PLY-002", "length": 200.0, "batch": "BATCH-2024-002"},
        {"name": "Kain Linen Natural", "code": "LNN-003", "length": 175.8, "batch": "BATCH-2024-003"},
        {"name": "Kain Silk Premium", "code": "SLK-004", "length": 120.3, "batch": "BATCH-2024-004"},
        {"name": "Kain Denim Classic", "code": "DNM-005", "length": 180.2, "batch": "BATCH-2024-005"},
        {"name": "Kain Rayon Soft", "code": "RYN-006", "length": 160.7, "batch": "BATCH-2024-006"},
        {"name": "Kain Wool Blend", "code": "WOL-007", "length": 140.9, "batch": "BATCH-2024-007"},
        {"name": "Kain Nylon Sport", "code": "NYL-008", "length": 190.4, "batch": "BATCH-2024-008"},
        {"name": "Kain Acrylic Warm", "code": "ACR-009", "length": 130.6, "batch": "BATCH-2024-009"},
        {"name": "Kain Spandex Flex", "code": "SPN-010", "length": 110.8, "batch": "BATCH-2024-010"}
    ]
    
    print("Menambahkan data contoh ke logging table...")
    
    # Add 20 sample entries with realistic timing
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(20):
        product = random.choice(products)
        
        # Generate realistic timing data
        time_to_print = random.uniform(30.0, 80.0)  # 30-80 seconds
        time_to_roll = random.uniform(10.0, 25.0)   # 10-25 seconds
        
        # Add some variation to product length
        length_variation = random.uniform(-5.0, 5.0)
        product_length = product["length"] + length_variation
        
        # Log the production data
        logging_table.log_production_data(
            product_name=product["name"],
            product_code=product["code"],
            product_length=product_length,
            batch=product["batch"],
            time_to_print=time_to_print,
            time_to_roll=time_to_roll
        )
        
        print(f"Added: {product['name']} - {product_length:.1f}m - Print: {time_to_print:.1f}s - Roll: {time_to_roll:.1f}s")
        
        # Small delay to simulate real production timing
        base_time += timedelta(minutes=random.randint(2, 8))
    
    print(f"\nBerhasil menambahkan 20 data contoh!")
    print(f"Data tersimpan di: {logging_table.get_today_filename()}")
    
    # Show current data
    data = logging_table.get_last_50_entries()
    print(f"Total data dalam tabel: {len(data)}")

if __name__ == "__main__":
    add_sample_data() 