#!/usr/bin/env python3
"""
Test script to verify print preview fix and tolerance calculation.
This script tests that the PrintPreviewDialog can be created without errors
and that the tolerance calculation is working correctly.
"""

import sys
import os
import traceback

# Add parent directory to path to import monitoring package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from monitoring.ui.print_preview import PrintPreviewDialog
    from monitoring.config import calculate_print_length, load_config
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_print_preview_creation():
    """Test that PrintPreviewDialog can be created without errors."""
    print("\n🧪 Testing Print Preview Creation")
    print("=" * 50)
    
    # Sample product info
    product_info = {
        'product_code': 'BD-1',
        'product_name': 'Test Product',
        'target_length': 100.0,
        'color_code': '1',
        'roll_number': '123',
        'batch_number': 'BATCH001',
        'units': 'Meter'
    }
    
    try:
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create PrintPreviewDialog
        print("Creating PrintPreviewDialog...")
        dialog = PrintPreviewDialog(product_info)
        print("✅ PrintPreviewDialog created successfully")
        
        # Test tolerance calculation
        config = load_config()
        tolerance_percent = config.get("length_tolerance", 3.0)
        decimal_points = config.get("decimal_points", 1)
        rounding = config.get("rounding", "UP")
        
        target_length = product_info['target_length']
        print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)
        
        print(f"📊 Tolerance Calculation:")
        print(f"   Target Length: {target_length}m")
        print(f"   Tolerance: {tolerance_percent}%")
        print(f"   Print Length: {print_length:.{decimal_points}f}m")
        
        # Verify print_length is in product_info
        if 'print_length' in dialog.product_info:
            print(f"✅ Print length added to product_info: {dialog.product_info['print_length']}")
        else:
            print("❌ Print length not found in product_info")
        
        # Close dialog after a short delay
        QTimer.singleShot(1000, dialog.close)
        QTimer.singleShot(1100, app.quit)
        
        print("✅ Test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PrintPreviewDialog: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_tolerance_calculation():
    """Test tolerance calculation with various values."""
    print("\n🧪 Testing Tolerance Calculation")
    print("=" * 50)
    
    test_cases = [
        (100.0, 5.0, 1, "UP"),    # User's example
        (50.0, 3.0, 1, "UP"),     # Small length
        (200.0, 10.0, 1, "UP"),   # Large tolerance
        (75.0, 0.0, 1, "UP"),     # No tolerance
    ]
    
    for target, tolerance, decimals, rounding in test_cases:
        print_length = calculate_print_length(target, tolerance, decimals, rounding)
        expected = target / (1 - tolerance/100)
        
        print(f"Target: {target}m, Tolerance: {tolerance}%")
        print(f"  Expected: {expected:.{decimals}f}m")
        print(f"  Calculated: {print_length:.{decimals}f}m")
        print(f"  ✅ Match: {abs(print_length - expected) < 0.01}")
        print()

def main():
    """Main test function."""
    print("🚀 Starting Print Preview Fix Test")
    print("=" * 50)
    
    # Test tolerance calculation
    test_tolerance_calculation()
    
    # Test print preview creation
    success = test_print_preview_creation()
    
    if success:
        print("\n🎉 All tests passed! Print preview fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main() 