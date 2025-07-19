#!/usr/bin/env python3
"""
Test untuk memverifikasi parser JSK3588 sesuai dokumentasi
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_jsk3588_parser():
    """Test parser JSK3588 sesuai dokumentasi"""
    print("=== Testing JSK3588 Parser ===")
    
    # Test data berdasarkan dokumentasi JSK3588.md
    # Contoh: 55 AA 20 0C 01 00 00 23 00 00 01 50
    # Data: 01 00 00 23 00 00 01
    # D6 = 0x01, D5D4D3 = 0x000023, D2D1 = 0x0000, D0 = 0x01
    
    print("\n1. Testing D6 = 0x01 (bit0=1, bit4=0)")
    print("   Expected: factor = 0.1, unit = meter")
    
    test_data_1 = bytes([0x01, 0x00, 0x00, 0x23, 0x00, 0x00, 0x01])
    result_1 = parse_fields(test_data_1)
    
    print(f"   D6: {result_1['d6_hex']}")
    print(f"   Factor bit: {result_1['factor_bit']}")
    print(f"   Factor: {result_1['factor']}")
    print(f"   Unit: {result_1['unit']}")
    print(f"   Length: {result_1['length_meters']:.2f} m")
    print(f"   Speed: {result_1['speed_text']}")
    
    # Verify results
    assert result_1['factor_bit'] == 1, f"Expected factor_bit = 1, got {result_1['factor_bit']}"
    assert result_1['factor'] == "×0.1", f"Expected factor = ×0.1, got {result_1['factor']}"
    assert result_1['unit'] == "meter", f"Expected unit = meter, got {result_1['unit']}"
    print("   ✓ Test 1 passed")
    
    print("\n2. Testing D6 = 0x00 (bit0=0, bit4=0)")
    print("   Expected: factor = 1.0, unit = meter")
    
    test_data_2 = bytes([0x00, 0x00, 0x00, 0x23, 0x00, 0x00, 0x01])
    result_2 = parse_fields(test_data_2)
    
    print(f"   D6: {result_2['d6_hex']}")
    print(f"   Factor bit: {result_2['factor_bit']}")
    print(f"   Factor: {result_2['factor']}")
    print(f"   Unit: {result_2['unit']}")
    print(f"   Length: {result_2['length_meters']:.2f} m")
    print(f"   Speed: {result_2['speed_text']}")
    
    # Verify results
    assert result_2['factor_bit'] == 0, f"Expected factor_bit = 0, got {result_2['factor_bit']}"
    assert result_2['factor'] == "×1.0", f"Expected factor = ×1.0, got {result_2['factor']}"
    assert result_2['unit'] == "meter", f"Expected unit = meter, got {result_2['unit']}"
    print("   ✓ Test 2 passed")
    
    print("\n3. Testing D6 = 0x11 (bit0=1, bit4=1)")
    print("   Expected: factor = 0.1, unit = yard")
    
    test_data_3 = bytes([0x11, 0x00, 0x00, 0x23, 0x00, 0x00, 0x01])
    result_3 = parse_fields(test_data_3)
    
    print(f"   D6: {result_3['d6_hex']}")
    print(f"   Factor bit: {result_3['factor_bit']}")
    print(f"   Factor: {result_3['factor']}")
    print(f"   Unit: {result_3['unit']}")
    print(f"   Length: {result_3['length_meters']:.2f} m")
    print(f"   Speed: {result_3['speed_text']}")
    
    # Verify results
    assert result_3['factor_bit'] == 1, f"Expected factor_bit = 1, got {result_3['factor_bit']}"
    assert result_3['factor'] == "×0.1", f"Expected factor = ×0.1, got {result_3['factor']}"
    assert result_3['unit'] == "yard", f"Expected unit = yard, got {result_3['unit']}"
    print("   ✓ Test 3 passed")
    
    print("\n4. Testing D6 = 0x10 (bit0=0, bit4=1)")
    print("   Expected: factor = 1.0, unit = yard")
    
    test_data_4 = bytes([0x10, 0x00, 0x00, 0x23, 0x00, 0x00, 0x01])
    result_4 = parse_fields(test_data_4)
    
    print(f"   D6: {result_4['d6_hex']}")
    print(f"   Factor bit: {result_4['factor_bit']}")
    print(f"   Factor: {result_4['factor']}")
    print(f"   Unit: {result_4['unit']}")
    print(f"   Length: {result_4['length_meters']:.2f} m")
    print(f"   Speed: {result_4['speed_text']}")
    
    # Verify results
    assert result_4['factor_bit'] == 0, f"Expected factor_bit = 0, got {result_4['factor_bit']}"
    assert result_4['factor'] == "×1.0", f"Expected factor = ×1.0, got {result_4['factor']}"
    assert result_4['unit'] == "yard", f"Expected unit = yard, got {result_4['unit']}"
    print("   ✓ Test 4 passed")
    
    print("\n5. Testing with actual length value")
    print("   D6 = 0x01, Length = 0x000123 (291 decimal)")
    print("   Expected: 291 × 0.1 = 29.1 meters")
    
    test_data_5 = bytes([0x01, 0x00, 0x01, 0x23, 0x00, 0x00, 0x01])
    result_5 = parse_fields(test_data_5)
    
    print(f"   Raw length: 0x{result_5['d5_d4_d3_hex'].replace(' ', '')}")
    print(f"   Calculated length: {result_5['length_meters']:.2f} m")
    print(f"   Factor applied: {result_5['factor']}")
    
    # Verify calculation
    expected_length = 291 * 0.1  # 0x123 = 291, factor = 0.1
    assert abs(result_5['length_meters'] - expected_length) < 0.01, f"Expected length = {expected_length}, got {result_5['length_meters']}"
    print("   ✓ Test 5 passed")
    
    print("\n=== All JSK3588 Parser Tests Passed! ===")
    print("\nSummary of changes:")
    print("- OLD: Used 4 bits (0x0F) for factor calculation")
    print("- NEW: Use only bit 0 for factor calculation (0.1 or 1.0)")
    print("- Unit detection remains the same (bit 4)")
    print("- Removed 0.01 factor as it's not in documentation")

if __name__ == "__main__":
    test_jsk3588_parser() 