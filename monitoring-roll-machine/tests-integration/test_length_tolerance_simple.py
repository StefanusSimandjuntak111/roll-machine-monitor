#!/usr/bin/env python3
"""
Simple test script for the length tolerance calculation function.
"""
import sys
import os
import math

# Add the parent directory to the path to import monitoring module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_length_tolerance_calculation():
    """Test the length tolerance calculation logic directly."""
    
    # Mock config for testing
    config = {
        "length_tolerance": 5.0,
        "decimal_points": 1,
        "rounding": "UP"
    }
    
    def calculate_length_print(current_length: float, unit: str) -> str:
        """Calculate length print with tolerance based on settings."""
        try:
            # Get tolerance settings from config
            tolerance_percent = config.get("length_tolerance", 0.0)
            decimal_points = config.get("decimal_points", 1)
            rounding_method = config.get("rounding", "UP")
            
            # If no tolerance is set, return current length as is
            if tolerance_percent <= 0:
                # Format with decimal points
                format_str = f"{{:.{decimal_points}f}}"
                if unit == 'yard':
                    return f"{format_str.format(current_length)} yard"
                else:
                    return f"{format_str.format(current_length)} m"
            
            # Apply tolerance formula: length_display = length_input * (1 - tolerance_percent / 100)
            length_with_tolerance = current_length * (1 - tolerance_percent / 100)
            
            # Apply rounding method
            if rounding_method == "UP":
                # Ceiling function
                if decimal_points == 0:
                    length_with_tolerance = math.ceil(length_with_tolerance)
                elif decimal_points == 1:
                    length_with_tolerance = math.ceil(length_with_tolerance * 10) / 10
                elif decimal_points == 2:
                    length_with_tolerance = math.ceil(length_with_tolerance * 100) / 100
            else:  # DOWN
                # Floor function
                if decimal_points == 0:
                    length_with_tolerance = math.floor(length_with_tolerance)
                elif decimal_points == 1:
                    length_with_tolerance = math.floor(length_with_tolerance * 10) / 10
                elif decimal_points == 2:
                    length_with_tolerance = math.floor(length_with_tolerance * 100) / 100
            
            # Format with decimal points
            format_str = f"{{:.{decimal_points}f}}"
            formatted_length = format_str.format(length_with_tolerance)
            
            # Return with unit
            if unit == 'yard':
                return f"{formatted_length} yard"
            else:
                return f"{formatted_length} m"
                
        except Exception as e:
            print(f"Error calculating length print: {e}")
            # Fallback to current length without tolerance
            if unit == 'yard':
                return f"{current_length:.2f} yard"
            else:
                return f"{current_length:.2f} m"
    
    # Test cases
    test_cases = [
        {
            "name": "No tolerance (0%)",
            "current_length": 100.0,
            "unit": "meter",
            "tolerance": 0.0,
            "decimal_points": 1,
            "rounding": "UP",
            "expected": "100.0 m"
        },
        {
            "name": "5% tolerance, UP rounding, 1 decimal",
            "current_length": 100.0,
            "unit": "meter", 
            "tolerance": 5.0,
            "decimal_points": 1,
            "rounding": "UP",
            "expected": "95.0 m"  # 100 * (1 - 5/100) = 95.0
        },
        {
            "name": "5% tolerance, DOWN rounding, 1 decimal",
            "current_length": 100.0,
            "unit": "meter",
            "tolerance": 5.0,
            "decimal_points": 1,
            "rounding": "DOWN", 
            "expected": "95.0 m"  # 100 * (1 - 5/100) = 95.0
        },
        {
            "name": "3% tolerance, UP rounding, 2 decimals",
            "current_length": 100.0,
            "unit": "meter",
            "tolerance": 3.0,
            "decimal_points": 2,
            "rounding": "UP",
            "expected": "97.00 m"  # 100 * (1 - 3/100) = 97.00
        },
        {
            "name": "10% tolerance, DOWN rounding, 0 decimals",
            "current_length": 100.0,
            "unit": "meter",
            "tolerance": 10.0,
            "decimal_points": 0,
            "rounding": "DOWN",
            "expected": "90 m"  # 100 * (1 - 10/100) = 90
        },
        {
            "name": "Yard unit test",
            "current_length": 100.0,
            "unit": "yard",
            "tolerance": 5.0,
            "decimal_points": 1,
            "rounding": "UP",
            "expected": "95.0 yard"  # 100 * (1 - 5/100) = 95.0
        },
        {
            "name": "Real data test (1.41m with 5% tolerance)",
            "current_length": 1.41,
            "unit": "meter",
            "tolerance": 5.0,
            "decimal_points": 2,
            "rounding": "UP",
            "expected": "1.34 m"  # 1.41 * (1 - 5/100) = 1.3395 -> 1.34 (UP)
        }
    ]
    
    print("🧪 Testing Length Tolerance Calculation")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        
        # Update config with test settings
        config.update({
            "length_tolerance": test_case["tolerance"],
            "decimal_points": test_case["decimal_points"],
            "rounding": test_case["rounding"]
        })
        
        # Calculate length print
        result = calculate_length_print(
            test_case["current_length"], 
            test_case["unit"]
        )
        
        # Check result
        if result == test_case["expected"]:
            print(f"✅ PASS: {result}")
            passed += 1
        else:
            print(f"❌ FAIL: Expected '{test_case['expected']}', got '{result}'")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")
    
    return failed == 0

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    # Mock config
    config = {
        "length_tolerance": 5.0,
        "decimal_points": 1,
        "rounding": "UP"
    }
    
    def calculate_length_print(current_length: float, unit: str) -> str:
        """Calculate length print with tolerance based on settings."""
        try:
            tolerance_percent = config.get("length_tolerance", 0.0)
            decimal_points = config.get("decimal_points", 1)
            rounding_method = config.get("rounding", "UP")
            
            if tolerance_percent <= 0:
                format_str = f"{{:.{decimal_points}f}}"
                if unit == 'yard':
                    return f"{format_str.format(current_length)} yard"
                else:
                    return f"{format_str.format(current_length)} m"
            
            length_with_tolerance = current_length * (1 - tolerance_percent / 100)
            
            if rounding_method == "UP":
                if decimal_points == 0:
                    length_with_tolerance = math.ceil(length_with_tolerance)
                elif decimal_points == 1:
                    length_with_tolerance = math.ceil(length_with_tolerance * 10) / 10
                elif decimal_points == 2:
                    length_with_tolerance = math.ceil(length_with_tolerance * 100) / 100
            else:  # DOWN
                if decimal_points == 0:
                    length_with_tolerance = math.floor(length_with_tolerance)
                elif decimal_points == 1:
                    length_with_tolerance = math.floor(length_with_tolerance * 10) / 10
                elif decimal_points == 2:
                    length_with_tolerance = math.floor(length_with_tolerance * 100) / 100
            
            format_str = f"{{:.{decimal_points}f}}"
            formatted_length = format_str.format(length_with_tolerance)
            
            if unit == 'yard':
                return f"{formatted_length} yard"
            else:
                return f"{formatted_length} m"
                
        except Exception as e:
            print(f"Error calculating length print: {e}")
            if unit == 'yard':
                return f"{current_length:.2f} yard"
            else:
                return f"{current_length:.2f} m"
    
    # Test with negative tolerance
    config.update({
        "length_tolerance": -5.0,  # Negative tolerance
        "decimal_points": 1,
        "rounding": "UP"
    })
    
    result = calculate_length_print(100.0, "meter")
    print(f"Negative tolerance (-5%): {result}")
    
    # Test with very high tolerance
    config.update({
        "length_tolerance": 50.0,  # 50% tolerance
        "decimal_points": 1,
        "rounding": "UP"
    })
    
    result = calculate_length_print(100.0, "meter")
    print(f"High tolerance (50%): {result}")
    
    # Test with zero length
    result = calculate_length_print(0.0, "meter")
    print(f"Zero length: {result}")

if __name__ == "__main__":
    print("🚀 Length Tolerance Feature Test")
    print("=" * 40)
    
    # Run main tests
    success = test_length_tolerance_calculation()
    
    # Run edge case tests
    test_edge_cases()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 