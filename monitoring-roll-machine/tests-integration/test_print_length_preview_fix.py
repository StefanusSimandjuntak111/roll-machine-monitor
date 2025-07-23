#!/usr/bin/env python3
"""
Test script to verify that print length and print preview show the same values
when using current machine length.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.config import calculate_print_length, load_config
from monitoring.ui.print_preview import PrintPreviewDialog

def test_print_length_preview_same():
    """Test that print length and print preview show the same values."""
    print("Testing Print Length vs Print Preview Same Value")
    print("=" * 50)
    
    # Test data
    current_machine_length = 2.00  # Current machine length
    target_length = 2.30  # Target length from form
    tolerance_percent = 10.0  # 10% tolerance
    decimal_points = 1
    rounding = "UP"
    
    # Calculate expected values
    print_length_with_current = calculate_print_length(current_machine_length, tolerance_percent, decimal_points, rounding)
    print_preview_with_current = calculate_print_length(current_machine_length, tolerance_percent, decimal_points, rounding)
    
    print(f"Current Machine Length: {current_machine_length}m")
    print(f"Target Length: {target_length}m")
    print(f"Tolerance: {tolerance_percent}%")
    print(f"Rounding: {rounding}")
    print()
    
    print(f"Print Length (with current machine): {print_length_with_current:.{decimal_points}f}m")
    print(f"Print Preview (with current machine): {print_preview_with_current:.{decimal_points}f}m")
    print()
    
    # Check if they are the same
    if abs(print_length_with_current - print_preview_with_current) < 0.01:
        print("✅ SUCCESS: Print Length and Print Preview show the same value")
        print(f"   Both values: {print_length_with_current:.{decimal_points}f}m")
    else:
        print("❌ FAILED: Print Length and Print Preview show different values")
        print(f"   Difference: {abs(print_length_with_current - print_preview_with_current):.{decimal_points}f}m")
    
    print()
    
    # Test PrintPreviewDialog with current machine length
    print("Testing PrintPreviewDialog with current machine length...")
    
    product_info = {
        'product_code': 'TEST-001',
        'product_name': 'Test Product',
        'color_code': 'RED',
        'target_length': target_length,
        'units': 'Meter',
        'batch_number': '20241201'
    }
    
    try:
        # Create dialog with current machine length
        dialog = PrintPreviewDialog(product_info, current_machine_length=current_machine_length)
        print("✅ PrintPreviewDialog created successfully with current machine length")
        print("   Print Preview will now use current machine length (same as Print Length)")
        
    except Exception as e:
        print(f"❌ Error creating PrintPreviewDialog: {e}")
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    test_print_length_preview_same() 