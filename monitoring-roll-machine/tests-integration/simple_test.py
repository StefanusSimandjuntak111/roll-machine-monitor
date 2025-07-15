#!/usr/bin/env python3
from monitoring.parser import parse_packet

# Test the user's example
packet = bytes.fromhex("55 AA 20 0C 02 00 00 03 00 00 01 31")
result = parse_packet(packet)

print("Test Result:")
print(f"Length: {result['length_meters']:.3f} m")
print(f"Factor: {result['factor']}")
print(f"Speed: {result['fields']['speed_text']}")
print(f"Shift: {result['fields']['shift_text']}")

# Expected: Length: 0.030 m (3 × 0.01)
print(f"\nExpected: 0.030 m")
print(f"Actual: {result['length_meters']:.3f} m")
print(f"Correct: {abs(result['length_meters'] - 0.030) < 0.001}") 