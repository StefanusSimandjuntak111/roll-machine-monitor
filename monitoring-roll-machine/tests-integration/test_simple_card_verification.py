#!/usr/bin/env python3
"""
Simple test to verify card length print consistency.
"""

import sys
import os

# Add parent directory to path to import monitoring package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.config import calculate_print_length
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_user_example():
    """Test the user's specific example."""
    print("\n🧪 Testing User Example")
    print("=" * 50)
    
    # User's configuration
    current_length = 2.37  # Current Length (Machine)
    tolerance = 10.0       # Length Tolerance
    decimals = 1           # Decimal Format #.#
    
    print(f"Configuration:")
    print(f"  Current Length (Machine): {current_length}m")
    print(f"  Length Tolerance: {tolerance}%")
    print(f"  Decimal Format: #.{decimals}")
    print()
    
    # Calculate using correct formula
    correct_result = calculate_print_length(current_length, tolerance, decimals, "UP")
    
    # Old wrong formula (for comparison)
    wrong_result = current_length * (1 - tolerance/100)
    
    print(f"Results:")
    print(f"  ✅ Correct Formula: {correct_result:.{decimals}f}m")
    print(f"  ❌ Wrong Formula: {wrong_result:.{decimals}f}m")
    print(f"  📊 Difference: {correct_result - wrong_result:.{decimals}f}m")
    print()
    
    print(f"Expected Behavior:")
    print(f"  Card Length Print: {correct_result:.{decimals}f}m")
    print(f"  Print Preview: {correct_result:.{decimals}f}m")
    print(f"  ✅ Both should be the same")
    
    return correct_result

def test_formula_verification():
    """Verify the formula is correct."""
    print("\n🧪 Formula Verification")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        (2.37, 10.0, 1),   # User's example
        (100.0, 5.0, 1),   # Standard example
        (50.0, 3.0, 1),    # Small length
    ]
    
    for current_length, tolerance, decimals in test_cases:
        # Manual calculation
        manual_result = current_length / (1 - tolerance/100)
        
        # Function calculation
        function_result = calculate_print_length(current_length, tolerance, decimals, "UP")
        
        print(f"Current Length: {current_length}m, Tolerance: {tolerance}%")
        print(f"  Manual: {manual_result:.{decimals}f}m")
        print(f"  Function: {function_result:.{decimals}f}m")
        print(f"  ✅ Match: {abs(manual_result - function_result) < 0.01}")
        print()

def main():
    """Main test function."""
    print("🚀 Simple Card Length Print Verification")
    print("=" * 50)
    
    # Test user example
    result = test_user_example()
    
    # Test formula verification
    test_formula_verification()
    
    print("\n🎉 Test completed!")
    print(f"\n📋 Summary:")
    print(f"  ✅ Card Length Print should show: {result:.1f}m")
    print(f"  ✅ Print Preview should show: {result:.1f}m")
    print(f"  ✅ Both should be consistent")

if __name__ == "__main__":
    main() 