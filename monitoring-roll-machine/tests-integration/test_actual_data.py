#!/usr/bin/env python3
"""
Test untuk mensimulasikan data aktual dari mesin roll user
"""

import sys
import os

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from monitoring.parser import parse_fields

def test_actual_machine_data():
    """Test dengan data aktual dari mesin roll"""
    print("=== Testing Actual Machine Data ===")
    
    print("\n1. Testing Meter Mode: 0000.91 meter")
    print("   Expected: Should show 0.91m in application")
    
    # Simulate data for 0.91 meter
    # If D6.bit0 = 1 (factor = 0.1), then raw value should be 9
    # If D6.bit0 = 0 (factor = 1.0), then raw value should be 0.91 (not possible with integer)
    
    # Let's try different D6 values to see what gives us 0.91
    test_cases = [
        (0x01, "D6=0x01 (bit0=1, factor=0.1) - raw=9"),
        (0x00, "D6=0x00 (bit0=0, factor=1.0) - raw=0"),
        (0x11, "D6=0x11 (bit0=1, bit4=1, factor=0.1, unit=yard) - raw=9"),
        (0x10, "D6=0x10 (bit0=0, bit4=1, factor=1.0, unit=yard) - raw=0"),
    ]
    
    for d6, description in test_cases:
        # Try different raw values
        for raw_value in [0, 1, 9, 91]:
            test_data = bytes([d6, 0x00, 0x00, raw_value, 0x00, 0x00, 0x01])
            result = parse_fields(test_data)
            
            print(f"   {description}")
            print(f"   Raw value: {raw_value}")
            print(f"   D6: {result['d6_hex']}")
            print(f"   Factor: {result['factor']}")
            print(f"   Unit: {result['unit']}")
            print(f"   Length: {result['length_meters']:.2f} m")
            print(f"   Current count: {result['current_count']:.2f}")
            print()
            
            # Check if this matches 0.91 meter
            if abs(result['length_meters'] - 0.91) < 0.01 and result['unit'] == 'meter':
                print(f"   ✓ FOUND MATCH: {description} with raw_value={raw_value}")
                print(f"   This should display as 0.91m in application")
                break
    
    print("\n2. Testing Yard Mode: 0001.00 yard")
    print("   Expected: Should show 1.00 yard in application")
    
    # Simulate data for 1.00 yard
    for d6, description in test_cases:
        # Try different raw values
        for raw_value in [0, 1, 10, 100]:
            test_data = bytes([d6, 0x00, 0x00, raw_value, 0x00, 0x00, 0x01])
            result = parse_fields(test_data)
            
            print(f"   {description}")
            print(f"   Raw value: {raw_value}")
            print(f"   D6: {result['d6_hex']}")
            print(f"   Factor: {result['factor']}")
            print(f"   Unit: {result['unit']}")
            print(f"   Length: {result['length_meters']:.2f} m")
            print(f"   Current count: {result['current_count']:.2f}")
            print()
            
            # Check if this matches 1.00 yard (0.9144 meters)
            if abs(result['length_meters'] - 0.9144) < 0.01 and result['unit'] == 'yard':
                print(f"   ✓ FOUND MATCH: {description} with raw_value={raw_value}")
                print(f"   This should display as 1.00 yard in application")
                break
    
    print("\n3. Debugging the Issue")
    print("   If machine shows 0000.91 meter but app shows 91.00m:")
    print("   - Possible: D6.bit0 = 0 (factor=1.0) but raw_value=91")
    print("   - This would give: 91 × 1.0 = 91.00 meters")
    print()
    print("   If machine shows 0001.00 yard but app shows 91.44 yard:")
    print("   - Possible: D6.bit0 = 0 (factor=1.0) but raw_value=100")
    print("   - This would give: 100 × 1.0 = 100 yards")
    print("   - But app converts to meters: 100 × 0.9144 = 91.44 meters")
    print()
    print("   SOLUTION: Need to check what D6 value the machine is actually sending")

if __name__ == "__main__":
    test_actual_machine_data() 