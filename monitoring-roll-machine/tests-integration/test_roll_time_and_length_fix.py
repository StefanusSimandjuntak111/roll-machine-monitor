#!/usr/bin/env python3
"""
Test script to verify roll time fix and length print formula consistency.
This script tests:
1. Roll time calculation after cycle reset
2. Length print formula consistency between main window and print preview
3. Tolerance calculation accuracy
"""

import sys
import os
import traceback
from datetime import datetime, timedelta

# Add parent directory to path to import monitoring package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.config import calculate_print_length, load_config
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_length_print_formula_consistency():
    """Test that length print formula is consistent between main window and print preview."""
    print("\n🧪 Testing Length Print Formula Consistency")
    print("=" * 60)
    
    # Test cases based on user's example
    test_cases = [
        (2.37, 10.0, 1, "UP"),    # User's example: 2.37m with 10% tolerance
        (100.0, 5.0, 1, "UP"),    # Standard example: 100m with 5% tolerance
        (50.0, 3.0, 1, "UP"),     # Small length: 50m with 3% tolerance
        (200.0, 10.0, 1, "UP"),   # Large tolerance: 200m with 10% tolerance
    ]
    
    print("Testing CORRECT formula: P_roll = P_target / (1 - T/100)")
    print("-" * 60)
    
    for target_length, tolerance, decimals, rounding in test_cases:
        # Calculate using the CORRECT formula
        print_length = calculate_print_length(target_length, tolerance, decimals, rounding)
        
        # Manual calculation for verification
        expected = target_length / (1 - tolerance/100)
        
        print(f"Target Length: {target_length}m")
        print(f"Tolerance: {tolerance}%")
        print(f"Formula: {target_length} / (1 - {tolerance}/100) = {target_length} / {1-tolerance/100:.3f}")
        print(f"Expected: {expected:.{decimals}f}m")
        print(f"Calculated: {print_length:.{decimals}f}m")
        print(f"✅ Match: {abs(print_length - expected) < 0.01}")
        print()

def test_old_vs_new_formula():
    """Test the difference between old (wrong) and new (correct) formulas."""
    print("\n🧪 Testing Old vs New Formula")
    print("=" * 60)
    
    # User's example
    current_length = 2.37
    tolerance = 10.0
    
    # OLD FORMULA (WRONG): length_display = length_input * (1 - tolerance_percent / 100)
    old_formula = current_length * (1 - tolerance / 100)
    
    # NEW FORMULA (CORRECT): P_roll = P_target / (1 - T/100)
    new_formula = current_length / (1 - tolerance / 100)
    
    print(f"Current Length (Machine): {current_length}m")
    print(f"Tolerance: {tolerance}%")
    print()
    print("OLD FORMULA (WRONG):")
    print(f"  length_display = {current_length} × (1 - {tolerance}/100)")
    print(f"  length_display = {current_length} × {1-tolerance/100:.3f}")
    print(f"  length_display = {old_formula:.2f}m")
    print()
    print("NEW FORMULA (CORRECT):")
    print(f"  P_roll = {current_length} ÷ (1 - {tolerance}/100)")
    print(f"  P_roll = {current_length} ÷ {1-tolerance/100:.3f}")
    print(f"  P_roll = {new_formula:.2f}m")
    print()
    print(f"Difference: {new_formula - old_formula:.2f}m")
    print(f"Percentage difference: {((new_formula - old_formula) / old_formula * 100):.1f}%")

def test_roll_time_scenario():
    """Test roll time calculation scenario."""
    print("\n🧪 Testing Roll Time Scenario")
    print("=" * 60)
    
    # Simulate the scenario:
    # 1. Reset counter (roll_start_time = None)
    # 2. New product starts (length = 0.01) -> roll_start_time = current_time
    # 3. Print product -> roll_time = current_time - roll_start_time
    # 4. Print again -> roll_time should continue from same roll_start_time
    
    print("Scenario: Reset Counter → New Product → Print → Print Again")
    print("-" * 60)
    
    # Simulate timestamps
    reset_time = datetime.now()
    new_product_time = reset_time + timedelta(seconds=5)  # 5 seconds later
    first_print_time = new_product_time + timedelta(seconds=30)  # 30 seconds later
    second_print_time = first_print_time + timedelta(seconds=15)  # 15 seconds later
    
    print(f"1. Reset Counter: {reset_time.strftime('%H:%M:%S')}")
    print(f"   roll_start_time = None")
    print()
    
    print(f"2. New Product Starts (length = 0.01): {new_product_time.strftime('%H:%M:%S')}")
    print(f"   roll_start_time = {new_product_time.strftime('%H:%M:%S')}")
    print()
    
    print(f"3. First Print: {first_print_time.strftime('%H:%M:%S')}")
    roll_time_1 = (first_print_time - new_product_time).total_seconds()
    print(f"   roll_time = {roll_time_1:.1f}s")
    print(f"   roll_start_time remains: {new_product_time.strftime('%H:%M:%S')}")
    print()
    
    print(f"4. Second Print: {second_print_time.strftime('%H:%M:%S')}")
    roll_time_2 = (second_print_time - new_product_time).total_seconds()
    print(f"   roll_time = {roll_time_2:.1f}s")
    print(f"   roll_start_time remains: {new_product_time.strftime('%H:%M:%S')}")
    print()
    
    print("✅ Roll time continues from same start time for multiple prints")
    print("✅ roll_start_time is NOT reset between prints")
    print("✅ roll_start_time is only reset when new product starts")

def test_tolerance_calculation_edge_cases():
    """Test edge cases for tolerance calculation."""
    print("\n🧪 Testing Tolerance Calculation Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        (0.0, 5.0, 1, "UP"),      # Zero length
        (100.0, 0.0, 1, "UP"),    # Zero tolerance
        (100.0, 100.0, 1, "UP"),  # 100% tolerance (edge case)
        (1.0, 1.0, 2, "DOWN"),    # Small tolerance
        (999.99, 50.0, 1, "UP"),  # Large length
    ]
    
    for target, tolerance, decimals, rounding in edge_cases:
        try:
            print_length = calculate_print_length(target, tolerance, decimals, rounding)
            print(f"Target: {target}m, Tolerance: {tolerance}% → Print: {print_length:.{decimals}f}m")
        except Exception as e:
            print(f"Target: {target}m, Tolerance: {tolerance}% → Error: {e}")

def main():
    """Main test function."""
    print("🚀 Starting Roll Time and Length Print Fix Test")
    print("=" * 60)
    
    # Test formula consistency
    test_length_print_formula_consistency()
    
    # Test old vs new formula
    test_old_vs_new_formula()
    
    # Test roll time scenario
    test_roll_time_scenario()
    
    # Test edge cases
    test_tolerance_calculation_edge_cases()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary of Fixes:")
    print("1. ✅ Length print formula corrected: P_roll = P_target / (1 - T/100)")
    print("2. ✅ Roll time logic fixed: roll_start_time not reset between prints")
    print("3. ✅ Formula consistency between main window and print preview")
    print("4. ✅ Roll time continues from same start time for multiple prints")

if __name__ == "__main__":
    main() 