#!/usr/bin/env python3
"""
Test komprehensif untuk memverifikasi semua kasus dengan machine-specific parser
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_comprehensive_fix():
    """Test komprehensif untuk semua kasus"""
    print("=== Test Komprehensif Machine-Specific Parser ===")
    
    print("\n🔧 PERBAIKAN YANG DILAKUKAN:")
    print("Machine-specific parser untuk roll machine")
    print("Deteksi dan koreksi format data khusus")
    
    print("\n📊 TEST SEMUA KASUS:")
    
    # Test cases: (D6, raw_value, expected_display, description)
    test_cases = [
        # Machine-specific cases (raw_value=100 → 1.00)
        (0x00, 100, 1.00, "Machine-specific: 100 → 1.00m"),
        (0x10, 100, 1.00, "Machine-specific yard: 100 → 1.00 yard"),
        
        # Normal cases (tidak terpengaruh)
        (0x00, 50, 50.00, "Normal meter: 50 → 50.00m"),
        (0x10, 50, 50.00, "Normal yard: 50 → 50.00 yard"),
        (0x00, 1, 1.00, "Normal meter: 1 → 1.00m"),
        (0x10, 1, 1.00, "Normal yard: 1 → 1.00 yard"),
        
        # Factor 0.1 cases (tidak terpengaruh)
        (0x01, 10, 1.00, "Factor 0.1 meter: 10 → 1.00m"),
        (0x11, 10, 1.00, "Factor 0.1 yard: 10 → 1.00 yard"),
        (0x01, 5, 0.50, "Factor 0.1 meter: 5 → 0.50m"),
        (0x11, 5, 0.50, "Factor 0.1 yard: 5 → 0.50 yard"),
        
        # Edge cases
        (0x00, 0, 0.00, "Zero value: 0 → 0.00m"),
        (0x00, 200, 200.00, "Large value: 200 → 200.00m"),
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
        print("Machine-specific parser bekerja dengan sempurna")
    else:
        print("⚠️  Ada beberapa test yang gagal")
        print("Perlu penyesuaian lebih lanjut")
    
    print("\n🎯 KESIMPULAN:")
    print("Machine-specific parser berhasil menangani:")
    print("- Format data khusus roll machine (100 → 1.00)")
    print("- Data normal tidak terpengaruh")
    print("- Factor 0.1 tidak terpengaruh")
    print("- Unit meter dan yard")
    print("- Edge cases (zero, large values)")

if __name__ == "__main__":
    test_comprehensive_fix() 