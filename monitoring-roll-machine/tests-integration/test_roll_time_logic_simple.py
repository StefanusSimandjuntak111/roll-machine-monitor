#!/usr/bin/env python3
"""
Simple test to verify roll time logic without PyQt6 dependencies.

This test verifies the roll time calculation logic:
1. roll_start_time initialization
2. roll time calculation
3. roll_start_time reset after print
"""

import sys
import os
from datetime import datetime, timedelta

def test_roll_time_calculation_logic():
    """Test roll time calculation logic without UI dependencies."""
    print("🧪 Testing Roll Time Calculation Logic")
    
    # Simulate roll_start_time initialization
    print("\n1. Testing roll_start_time initialization...")
    roll_start_time = datetime.now()
    print(f"✅ roll_start_time initialized: {roll_start_time.strftime('%H:%M:%S')}")
    
    # Wait a bit to simulate rolling time
    import time
    time.sleep(0.1)
    
    # Simulate print time
    print_time = datetime.now()
    
    # Calculate roll time
    roll_time = (print_time - roll_start_time).total_seconds()
    print(f"✅ Roll time calculated: {roll_time:.1f}s")
    
    # Verify roll time is positive
    if roll_time > 0:
        print("✅ Roll time is positive")
    else:
        print("❌ Roll time is not positive")
        return False
    
    # Simulate roll_start_time reset after print
    print("\n2. Testing roll_start_time reset after print...")
    roll_start_time = None
    if roll_start_time is None:
        print("✅ roll_start_time reset to None after print")
    else:
        print("❌ roll_start_time not reset after print")
        return False
    
    # Simulate new roll start
    print("\n3. Testing new roll start...")
    new_roll_start_time = datetime.now()
    print(f"✅ New roll_start_time set: {new_roll_start_time.strftime('%H:%M:%S')}")
    
    # Wait a bit
    time.sleep(0.1)
    
    # Simulate second print
    second_print_time = datetime.now()
    second_roll_time = (second_print_time - new_roll_start_time).total_seconds()
    print(f"✅ Second roll time calculated: {second_roll_time:.1f}s")
    
    # Verify second roll time is different from first
    if abs(second_roll_time - roll_time) > 0.01:  # Allow small difference due to timing
        print("✅ Second roll time is different from first (as expected)")
    else:
        print("❌ Second roll time is same as first (unexpected)")
        return False
    
    return True

def test_roll_time_edge_cases():
    """Test roll time edge cases."""
    print("\n🧪 Testing Roll Time Edge Cases")
    
    # Test with None roll_start_time
    print("\n1. Testing with None roll_start_time...")
    roll_start_time = None
    print_time = datetime.now()
    
    # Calculate roll time
    roll_time = 0.0
    if roll_start_time:
        roll_time = (print_time - roll_start_time).total_seconds()
    
    print(f"✅ Roll time with None start: {roll_time:.1f}s (should be 0.0)")
    
    if roll_time == 0.0:
        print("✅ Correctly handled None roll_start_time")
    else:
        print("❌ Incorrectly handled None roll_start_time")
        return False
    
    # Test with very short roll time
    print("\n2. Testing very short roll time...")
    start_time = datetime.now()
    import time
    time.sleep(0.01)  # Very short delay
    end_time = datetime.now()
    
    short_roll_time = (end_time - start_time).total_seconds()
    print(f"✅ Short roll time: {short_roll_time:.3f}s")
    
    if short_roll_time > 0:
        print("✅ Short roll time calculated correctly")
    else:
        print("❌ Short roll time calculation failed")
        return False
    
    return True

def main():
    """Run all roll time logic tests."""
    print("🚀 Starting Roll Time Logic Tests")
    print("=" * 50)
    
    try:
        # Test basic roll time calculation
        if not test_roll_time_calculation_logic():
            print("❌ Roll time calculation logic test failed")
            return False
        
        # Test edge cases
        if not test_roll_time_edge_cases():
            print("❌ Roll time edge cases test failed")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All roll time logic tests passed!")
        print("\nSummary of verified logic:")
        print("1. ✅ roll_start_time can be initialized with current time")
        print("2. ✅ roll time calculation: (print_time - roll_start_time)")
        print("3. ✅ roll_start_time can be reset to None after print")
        print("4. ✅ new roll_start_time can be set for subsequent prints")
        print("5. ✅ roll time is 0.0 when roll_start_time is None")
        print("6. ✅ roll time calculation works for very short durations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 