#!/usr/bin/env python3
"""
Test untuk menganalisis data baru: 0001.00m → 100.00m
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_new_data_format():
    """Test format data baru"""
    print("=== Test Data Baru: 0001.00m → 100.00m ===")
    
    print("\n🔍 ANALISIS MASALAH:")
    print("Mesin Roll: 0001.00m → Aplikasi: 100.00m")
    print("Seharusnya: 1.00m")
    
    print("\n📊 SIMULASI DATA YANG MUNGKIN:")
    
    # Test berbagai kemungkinan data yang dikirim mesin
    test_cases = [
        # (D6, raw_value, description)
        (0x00, 100, "D6=0x00 (factor=1.0) dengan raw_value=100"),
        (0x01, 100, "D6=0x01 (factor=0.1) dengan raw_value=100"),
        (0x00, 1, "D6=0x00 (factor=1.0) dengan raw_value=1"),
        (0x01, 1, "D6=0x01 (factor=0.1) dengan raw_value=1"),
        (0x00, 10, "D6=0x00 (factor=1.0) dengan raw_value=10"),
        (0x01, 10, "D6=0x01 (factor=0.1) dengan raw_value=10"),
    ]
    
    for d6, raw_value, description in test_cases:
        test_data = bytes([d6, 0x00, 0x00, raw_value, 0x00, 0x00, 0x01])
        result = parse_fields(test_data)
        
        print(f"\n{description}:")
        print(f"   D6: {result['d6_hex']}")
        print(f"   Raw value: {raw_value}")
        print(f"   Factor: {result['factor']}")
        print(f"   Current count: {result['current_count']:.2f}")
        print(f"   UI akan menampilkan: {result['current_count']:.2f} m")
        
        # Cek apakah ini yang menyebabkan 100.00m
        if result['current_count'] == 100.0:
            print(f"   🎯 INI YANG MENYEBABKAN 100.00m!")
            print(f"   Mesin mengirim: D6={d6:02X}, raw_value={raw_value}")
            print(f"   Calculation: {raw_value} × {result['factor']} = {result['current_count']:.2f}")
    
    print("\n🎯 KESIMPULAN:")
    print("Jika aplikasi menampilkan 100.00m, kemungkinan:")
    print("1. Mesin mengirim D6=0x00 dengan raw_value=100")
    print("2. Atau mesin menggunakan format data yang berbeda")
    
    print("\n🔧 SOLUSI YANG DICARI:")
    print("Untuk menampilkan 1.00m, mesin harus mengirim:")
    print("- D6=0x00 dengan raw_value=1, ATAU")
    print("- D6=0x01 dengan raw_value=10")
    
    print("\n📋 LANGKAH SELANJUTNYA:")
    print("1. Cek data mentah yang dikirim mesin")
    print("2. Bandingkan dengan hasil test ini")
    print("3. Sesuaikan parser jika perlu")

if __name__ == "__main__":
    test_new_data_format() 