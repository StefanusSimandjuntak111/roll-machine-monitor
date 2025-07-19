#!/usr/bin/env python3
"""
Simple debug test untuk masalah display
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def simple_debug():
    """Simple debug untuk masalah display"""
    print("=== Simple Debug ===")
    
    # Test untuk 0.91 meter
    print("\nTest 1: 0.91 meter")
    print("Jika mesin mengirim raw_value=91 dengan D6=0x00:")
    
    test_data = bytes([0x00, 0x00, 0x00, 91, 0x00, 0x00, 0x01])
    result = parse_fields(test_data)
    
    print(f"D6: {result['d6_hex']}")
    print(f"Factor: {result['factor']}")
    print(f"Unit: {result['unit']}")
    print(f"Raw value: 91")
    print(f"Calculated: {result['current_count']:.2f}")
    print(f"Display: {result['length_meters']:.2f} m")
    
    if result['length_meters'] == 91.0:
        print("❌ INI YANG SALAH! Seharusnya 0.91m")
    else:
        print("✅ Ini benar")
    
    # Test untuk 1.00 yard
    print("\nTest 2: 1.00 yard")
    print("Jika mesin mengirim raw_value=100 dengan D6=0x10:")
    
    test_data2 = bytes([0x10, 0x00, 0x00, 100, 0x00, 0x00, 0x01])
    result2 = parse_fields(test_data2)
    
    print(f"D6: {result2['d6_hex']}")
    print(f"Factor: {result2['factor']}")
    print(f"Unit: {result2['unit']}")
    print(f"Raw value: 100")
    print(f"Calculated: {result2['current_count']:.2f}")
    print(f"Display: {result2['length_meters']:.2f} m")
    
    if result2['length_meters'] == 91.44:
        print("❌ INI YANG SALAH! Seharusnya 1.00 yard")
    else:
        print("✅ Ini benar")

if __name__ == "__main__":
    simple_debug() 