#!/usr/bin/env python3
"""
Debug test untuk masalah display yang user alami
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def debug_display_issue():
    """Debug masalah display yang user alami"""
    print("=== Debug Display Issue ===")
    
    print("\n🔍 ANALISIS MASALAH:")
    print("Mesin Roll: 0000.91 meter → Aplikasi: 91.00m")
    print("Mesin Roll: 0001.00 yard → Aplikasi: 91.44 yard")
    
    print("\n📊 SIMULASI DATA YANG MUNGKIN:")
    
    # Test 1: Untuk 0.91 meter
    print("\n1. Untuk 0.91 meter:")
    print("   Jika mesin mengirim D6=0x00 (factor=1.0) dengan raw_value=91:")
    test_data_1 = bytes([0x00, 0x00, 0x00, 91, 0x00, 0x00, 0x01])
    result_1 = parse_fields(test_data_1)
    print(f"   D6: {result_1['d6_hex']} (bit0=0, factor=1.0)")
    print(f"   Raw value: 91")
    print(f"   Calculation: 91 × 1.0 = {result_1['current_count']:.2f} meters")
    print(f"   Display: {result_1['length_meters']:.2f} m")
    print(f"   ❌ INI YANG SALAH! Seharusnya 0.91m")
    
    print("\n   Jika mesin mengirim D6=0x01 (factor=0.1) dengan raw_value=9:")
    test_data_2 = bytes([0x01, 0x00, 0x00, 9, 0x00, 0x00, 0x01])
    result_2 = parse_fields(test_data_2)
    print(f"   D6: {result_2['d6_hex']} (bit0=1, factor=0.1)")
    print(f"   Raw value: 9")
    print(f"   Calculation: 9 × 0.1 = {result_2['current_count']:.2f} meters")
    print(f"   Display: {result_2['length_meters']:.2f} m")
    print(f"   ❌ Masih salah! Seharusnya 0.91m")
    
    # Test 2: Untuk 1.00 yard
    print("\n2. Untuk 1.00 yard:")
    print("   Jika mesin mengirim D6=0x10 (factor=1.0, unit=yard) dengan raw_value=100:")
    test_data_3 = bytes([0x10, 0x00, 0x00, 100, 0x00, 0x00, 0x01])
    result_3 = parse_fields(test_data_3)
    print(f"   D6: {result_3['d6_hex']} (bit0=0, bit4=1, factor=1.0, unit=yard)")
    print(f"   Raw value: 100")
    print(f"   Calculation: 100 × 1.0 = {result_3['current_count']:.2f} yards")
    print(f"   Display: {result_3['length_meters']:.2f} m")
    print(f"   ❌ INI YANG SALAH! Seharusnya 1.00 yard")
    
    print("\n   Jika mesin mengirim D6=0x11 (factor=0.1, unit=yard) dengan raw_value=10:")
    test_data_4 = bytes([0x11, 0x00, 0x00, 10, 0x00, 0x00, 0x01])
    result_4 = parse_fields(test_data_4)
    print(f"   D6: {result_4['d6_hex']} (bit0=1, bit4=1, factor=0.1, unit=yard)")
    print(f"   Raw value: 10")
    print(f"   Calculation: 10 × 0.1 = {result_4['current_count']:.2f} yards")
    print(f"   Display: {result_4['length_meters']:.2f} m")
    print(f"   ❌ Masih salah! Seharusnya 1.00 yard")
    
    print("\n🎯 KESIMPULAN:")
    print("Masalahnya BUKAN di parser, tapi di:")
    print("1. Mesin roll mengirim data dengan format yang berbeda")
    print("2. Atau ada masalah di UI display")
    
    print("\n🔧 SOLUSI YANG DICARI:")
    print("Untuk 0.91 meter:")
    print("- Mesin harus mengirim D6=0x01 dengan raw_value=9")
    print("- Atau mesin mengirim dengan format yang berbeda")
    
    print("\nUntuk 1.00 yard:")
    print("- Mesin harus mengirim D6=0x11 dengan raw_value=10")
    print("- Atau mesin mengirim dengan format yang berbeda")
    
    print("\n📋 LANGKAH SELANJUTNYA:")
    print("1. Cek data mentah yang dikirim mesin (hex dump)")
    print("2. Bandingkan dengan dokumentasi JSK3588.md")
    print("3. Sesuaikan parser jika perlu")

if __name__ == "__main__":
    debug_display_issue() 