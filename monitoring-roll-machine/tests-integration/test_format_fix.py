#!/usr/bin/env python3
from monitoring.parser import parse_packet

# Test the user's example
packet = bytes.fromhex("55 AA 20 0C 02 00 00 03 00 00 01 31")
result = parse_packet(packet)

print("Test Format Fix:")
print(f"Length: {result['length_meters']:.2f} m")  # Should show 0.03 m
print(f"Factor: {result['factor']}")
print(f"Speed: {result['fields']['speed_text']}")
print(f"Shift: {result['fields']['shift_text']}")

# Test with different values
test_cases = [
    ("55 AA 20 0C 02 00 00 03 00 00 01 31", "0.03 m"),
    ("55 AA 20 0C 01 00 00 23 00 00 01 50", "3.50 m"),
    ("55 AA 20 0C 00 00 00 50 00 30 01 5D", "80.00 m"),
]

print("\nFormat Test Cases:")
for packet_hex, expected in test_cases:
    packet = bytes.fromhex(packet_hex)
    result = parse_packet(packet)
    formatted = f"{result['length_meters']:.2f} m"
    print(f"Expected: {expected}, Got: {formatted}, Match: {formatted == expected}") 