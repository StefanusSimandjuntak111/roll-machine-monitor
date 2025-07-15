#!/usr/bin/env python3
import traceback

try:
    from monitoring.parser import parse_packet
    print("✅ Import successful")
    
    # Test packet
    packet = bytes.fromhex("55 AA 20 0C 02 00 00 03 00 00 01 31")
    print(f"✅ Packet created: {packet.hex().upper()}")
    
    # Parse packet
    result = parse_packet(packet)
    print("✅ Parse successful")
    
    # Show results
    print(f"Length: {result['length_meters']:.3f} m")
    print(f"Factor: {result['factor']}")
    print(f"Speed: {result['fields']['speed_text']}")
    print(f"Shift: {result['fields']['shift_text']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Traceback:")
    traceback.print_exc() 