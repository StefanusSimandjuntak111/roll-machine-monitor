#!/usr/bin/env python3
"""
Test script untuk enhanced parser JSK3588.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring.parser import parse_packet, format_packet_table

def test_parser():
    """Test enhanced parser dengan contoh data."""
    print("🧪 Testing Enhanced JSK3588 Parser")
    print("=" * 60)
    
    # Test case 1: Contoh dari user
    test_data_1 = bytes.fromhex("55 AA 20 0C 02 00 00 03 00 00 01 31")
    
    print("\n📦 Test Case 1: Contoh User")
    print(f"Raw: {test_data_1.hex().upper()}")
    
    try:
        result_1 = parse_packet(test_data_1)
        print("\n✅ Parsed Successfully!")
        print(f"Length: {result_1['length_meters']:.3f} m")
        print(f"Speed: {result_1['fields']['speed_text']}")
        print(f"Shift: {result_1['fields']['shift_text']}")
        print(f"Unit: {result_1['unit']}")
        print(f"Factor: {result_1['factor']}")
        
        # Show detailed table
        print("\n📊 Packet Analysis Table:")
        table_1 = format_packet_table(test_data_1)
        print(table_1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test case 2: Contoh dari dokumentasi
    test_data_2 = bytes.fromhex("55 AA 20 0C 01 00 00 23 00 00 01 50")
    
    print("\n" + "=" * 60)
    print("\n📦 Test Case 2: Contoh Dokumentasi")
    print(f"Raw: {test_data_2.hex().upper()}")
    
    try:
        result_2 = parse_packet(test_data_2)
        print("\n✅ Parsed Successfully!")
        print(f"Length: {result_2['length_meters']:.3f} m")
        print(f"Speed: {result_2['fields']['speed_text']}")
        print(f"Shift: {result_2['fields']['shift_text']}")
        print(f"Unit: {result_2['unit']}")
        print(f"Factor: {result_2['factor']}")
        
        # Show detailed table
        print("\n📊 Packet Analysis Table:")
        table_2 = format_packet_table(test_data_2)
        print(table_2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test case 3: Data dengan speed
    test_data_3 = bytes.fromhex("55 AA 20 0C 01 00 00 50 00 30 01 5D")
    
    print("\n" + "=" * 60)
    print("\n📦 Test Case 3: Data dengan Speed")
    print(f"Raw: {test_data_3.hex().upper()}")
    
    try:
        result_3 = parse_packet(test_data_3)
        print("\n✅ Parsed Successfully!")
        print(f"Length: {result_3['length_meters']:.3f} m")
        print(f"Speed: {result_3['fields']['speed_text']}")
        print(f"Shift: {result_3['fields']['shift_text']}")
        print(f"Unit: {result_3['unit']}")
        print(f"Factor: {result_3['factor']}")
        
        # Show detailed table
        print("\n📊 Packet Analysis Table:")
        table_3 = format_packet_table(test_data_3)
        print(table_3)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Parser Test Complete!")
    print("\nData yang di-parse akan otomatis muncul di:")
    print("✅ Length Card - nilai dalam meter")
    print("✅ Speed Card - nilai dalam m/min")
    print("✅ Shift Card - status shift")
    print("✅ Serial Display - tabel analisis packet")

if __name__ == "__main__":
    test_parser() 