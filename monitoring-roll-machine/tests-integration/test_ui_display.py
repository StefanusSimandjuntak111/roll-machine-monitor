#!/usr/bin/env python3
"""
Test untuk memverifikasi bagaimana UI menampilkan data
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_ui_display():
    """Test bagaimana UI menampilkan data"""
    print("=== Test UI Display ===")
    
    print("\n🔍 MASALAH YANG DITEMUKAN:")
    print("Mesin Roll: 0000.91 meter → Aplikasi: 91.00m")
    print("Mesin Roll: 0001.00 yard → Aplikasi: 91.44 yard")
    
    print("\n📊 ANALISIS DATA:")
    
    # Test 1: 0.91 meter
    print("\n1. Untuk 0.91 meter:")
    print("   Jika mesin mengirim D6=0x00 dengan raw_value=91:")
    test_data_1 = bytes([0x00, 0x00, 0x00, 91, 0x00, 0x00, 0x01])
    result_1 = parse_fields(test_data_1)
    
    print(f"   D6: {result_1['d6_hex']} (factor=1.0, unit=meter)")
    print(f"   Raw value: 91")
    print(f"   Current count: {result_1['current_count']:.2f} meters")
    print(f"   Length meters: {result_1['length_meters']:.2f} m")
    print(f"   UI akan menampilkan: {result_1['length_meters']:.2f} m")
    print(f"   ❌ SALAH! Seharusnya 0.91m")
    
    # Test 2: 1.00 yard
    print("\n2. Untuk 1.00 yard:")
    print("   Jika mesin mengirim D6=0x10 dengan raw_value=100:")
    test_data_2 = bytes([0x10, 0x00, 0x00, 100, 0x00, 0x00, 0x01])
    result_2 = parse_fields(test_data_2)
    
    print(f"   D6: {result_2['d6_hex']} (factor=1.0, unit=yard)")
    print(f"   Raw value: 100")
    print(f"   Current count: {result_2['current_count']:.2f} yards")
    print(f"   Length meters: {result_2['length_meters']:.2f} m")
    print(f"   UI akan menampilkan: {result_2['length_meters']:.2f} m")
    print(f"   ❌ SALAH! Seharusnya 1.00 yard")
    
    print("\n🎯 KESIMPULAN:")
    print("Masalahnya adalah:")
    print("1. Aplikasi SELALU menampilkan dalam meter (length_meters)")
    print("2. Mesin roll menampilkan dalam unit asli (meter/yard)")
    print("3. Aplikasi tidak menampilkan unit asli dari mesin")
    
    print("\n🔧 SOLUSI:")
    print("1. UI harus menampilkan current_count dengan unit asli")
    print("2. Atau tambahkan opsi untuk menampilkan unit asli")
    print("3. Atau perbaiki interpretasi data dari mesin")
    
    print("\n📋 LANGKAH SELANJUTNYA:")
    print("1. Cek data mentah yang dikirim mesin")
    print("2. Bandingkan dengan yang diharapkan")
    print("3. Sesuaikan parser atau UI display")

if __name__ == "__main__":
    test_ui_display() 