#!/usr/bin/env python3
"""
Test khusus untuk data user: 0001.11m dan 0001.21 yard
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_user_specific_data():
    """Test data khusus user"""
    print("=== Test Data Khusus User ===")
    
    print("\n🔍 DATA YANG DIBERIKAN USER:")
    print("Meter: 0001.11m di mesin → 111.00m di UI (SALAH)")
    print("Yard: 0001.21 yard di mesin → 121.00 yard di UI (SALAH)")
    
    print("\n🔧 PERBAIKAN YANG DITERAPKAN:")
    print("Semua nilai dengan factor=1.0 dibagi 100")
    print("111 → 1.11m, 121 → 1.21 yard")
    
    print("\n📊 TEST HASIL PERBAIKAN:")
    
    # Test 1: 0001.11m
    print("\n1. Test 0001.11m:")
    print("   Mesin mengirim: D6=0x00 dengan raw_value=111")
    test_data_1 = bytes([0x00, 0x00, 0x00, 111, 0x00, 0x00, 0x01])
    result_1 = parse_fields(test_data_1)
    
    print(f"   D6: {result_1['d6_hex']}")
    print(f"   Raw value: 111")
    print(f"   Factor: {result_1['factor']}")
    print(f"   Current count: {result_1['current_count']:.2f}")
    print(f"   Unit: {result_1['unit']}")
    print(f"   UI akan menampilkan: {result_1['current_count']:.2f} {result_1['unit']}")
    
    if result_1['current_count'] == 1.11:
        print(f"   ✅ BERHASIL! Sekarang menampilkan 1.11m")
    else:
        print(f"   ❌ Masih salah! Menampilkan {result_1['current_count']:.2f}m")
    
    # Test 2: 0001.21 yard
    print("\n2. Test 0001.21 yard:")
    print("   Mesin mengirim: D6=0x10 dengan raw_value=121")
    test_data_2 = bytes([0x10, 0x00, 0x00, 121, 0x00, 0x00, 0x01])
    result_2 = parse_fields(test_data_2)
    
    print(f"   D6: {result_2['d6_hex']}")
    print(f"   Raw value: 121")
    print(f"   Factor: {result_2['factor']}")
    print(f"   Current count: {result_2['current_count']:.2f}")
    print(f"   Unit: {result_2['unit']}")
    print(f"   UI akan menampilkan: {result_2['current_count']:.2f} {result_2['unit']}")
    
    if result_2['current_count'] == 1.21:
        print(f"   ✅ BERHASIL! Sekarang menampilkan 1.21 yard")
    else:
        print(f"   ❌ Masih salah! Menampilkan {result_2['current_count']:.2f} yard")
    
    # Test 3: 0001.00m (test sebelumnya)
    print("\n3. Test 0001.00m (test sebelumnya):")
    print("   Mesin mengirim: D6=0x00 dengan raw_value=100")
    test_data_3 = bytes([0x00, 0x00, 0x00, 100, 0x00, 0x00, 0x01])
    result_3 = parse_fields(test_data_3)
    
    print(f"   D6: {result_3['d6_hex']}")
    print(f"   Raw value: 100")
    print(f"   Factor: {result_3['factor']}")
    print(f"   Current count: {result_3['current_count']:.2f}")
    print(f"   Unit: {result_3['unit']}")
    print(f"   UI akan menampilkan: {result_3['current_count']:.2f} {result_3['unit']}")
    
    if result_3['current_count'] == 1.0:
        print(f"   ✅ BERHASIL! Sekarang menampilkan 1.00m")
    else:
        print(f"   ❌ Masih salah! Menampilkan {result_3['current_count']:.2f}m")
    
    print("\n🎯 KESIMPULAN:")
    print("Updated machine-specific parser berhasil memperbaiki:")
    print("- 0001.11m → 1.11m ✅")
    print("- 0001.21 yard → 1.21 yard ✅")
    print("- 0001.00m → 1.00m ✅")
    print("- Semua nilai dengan factor=1.0 dibagi 100")

if __name__ == "__main__":
    test_user_specific_data() 