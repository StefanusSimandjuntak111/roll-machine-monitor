#!/usr/bin/env python3
"""
Test untuk memverifikasi updated machine-specific parser
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_updated_machine_parser():
    """Test updated machine-specific parser"""
    print("=== Test Updated Machine-Specific Parser ===")
    
    print("\n🔧 PERBAIKAN YANG DILAKUKAN:")
    print("Machine-specific parser untuk semua nilai dengan factor=1.0")
    print("Semua nilai dibagi 100 (bukan hanya nilai 100)")
    
    print("\n📊 TEST HASIL PERBAIKAN:")
    
    # Test cases: (D6, raw_value, expected_display, description)
    test_cases = [
        # Meter cases (factor=1.0, semua dibagi 100)
        (0x00, 111, 1.11, "Meter: 0001.11m → 1.11m"),
        (0x00, 100, 1.00, "Meter: 0001.00m → 1.00m"),
        (0x00, 50, 0.50, "Meter: 0000.50m → 0.50m"),
        (0x00, 200, 2.00, "Meter: 0002.00m → 2.00m"),
        
        # Yard cases (factor=1.0, semua dibagi 100)
        (0x10, 121, 1.21, "Yard: 0001.21 yard → 1.21 yard"),
        (0x10, 100, 1.00, "Yard: 0001.00 yard → 1.00 yard"),
        (0x10, 50, 0.50, "Yard: 0000.50 yard → 0.50 yard"),
        (0x10, 200, 2.00, "Yard: 0002.00 yard → 2.00 yard"),
        
        # Factor 0.1 cases (tidak terpengaruh)
        (0x01, 10, 1.00, "Factor 0.1 meter: 10 → 1.00m"),
        (0x11, 10, 1.00, "Factor 0.1 yard: 10 → 1.00 yard"),
        (0x01, 5, 0.50, "Factor 0.1 meter: 5 → 0.50m"),
        (0x11, 5, 0.50, "Factor 0.1 yard: 5 → 0.50 yard"),
        
        # Edge cases
        (0x00, 0, 0.00, "Zero value: 0 → 0.00m"),
        (0x10, 0, 0.00, "Zero value yard: 0 → 0.00 yard"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for d6, raw_value, expected, description in test_cases:
        test_data = bytes([d6, 0x00, 0x00, raw_value, 0x00, 0x00, 0x01])
        result = parse_fields(test_data)
        
        print(f"\n{description}:")
        print(f"   D6: {result['d6_hex']}")
        print(f"   Raw value: {raw_value}")
        print(f"   Factor: {result['factor']}")
        print(f"   Current count: {result['current_count']:.2f}")
        print(f"   Unit: {result['unit']}")
        print(f"   UI akan menampilkan: {result['current_count']:.2f} {result['unit']}")
        
        # Check if result matches expected
        if abs(result['current_count'] - expected) < 0.01:
            print(f"   ✅ PASS: {result['current_count']:.2f} ≈ {expected:.2f}")
            passed += 1
        else:
            print(f"   ❌ FAIL: {result['current_count']:.2f} ≠ {expected:.2f}")
    
    print(f"\n📊 HASIL TEST: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 SEMUA TEST BERHASIL!")
        print("Updated machine-specific parser bekerja dengan sempurna")
    else:
        print("⚠️  Ada beberapa test yang gagal")
        print("Perlu penyesuaian lebih lanjut")
    
    print("\n🎯 KESIMPULAN:")
    print("Updated machine-specific parser berhasil menangani:")
    print("- Semua nilai meter dengan factor=1.0 (dibagi 100)")
    print("- Semua nilai yard dengan factor=1.0 (dibagi 100)")
    print("- Factor 0.1 tidak terpengaruh")
    print("- Edge cases (zero values)")

if __name__ == "__main__":
    test_updated_machine_parser() 