#!/usr/bin/env python3
"""
Test script for the length tolerance feature.
"""
import sys
import os

# Add the parent directory to the path to import monitoring module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PySide6.QtWidgets import QApplication
from monitoring.ui.main_window import ModernMainWindow
from monitoring.config import get_default_config
import math

def test_length_tolerance_calculation():
    """Test the length tolerance calculation with different settings."""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = ModernMainWindow()
    
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
        }
    ]
    
    print("🧪 Testing Length Tolerance Calculation")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        
        # Update config with test settings
        main_window.config.update({
            "length_tolerance": test_case["tolerance"],
            "decimal_points": test_case["decimal_points"],
            "rounding": test_case["rounding"]
        })
        
        # Calculate length print
        result = main_window.calculate_length_print(
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
    app = QApplication(sys.argv)
    main_window = ModernMainWindow()
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    # Test with invalid tolerance
    main_window.config.update({
        "length_tolerance": -5.0,  # Negative tolerance
        "decimal_points": 1,
        "rounding": "UP"
    })
    
    result = main_window.calculate_length_print(100.0, "meter")
    print(f"Negative tolerance (-5%): {result}")
    
    # Test with very high tolerance
    main_window.config.update({
        "length_tolerance": 50.0,  # 50% tolerance
        "decimal_points": 1,
        "rounding": "UP"
    })
    
    result = main_window.calculate_length_print(100.0, "meter")
    print(f"High tolerance (50%): {result}")
    
    # Test with zero length
    result = main_window.calculate_length_print(0.0, "meter")
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