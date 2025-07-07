#!/usr/bin/env python3
"""
Test script to verify Windows compatibility of the Roll Machine Monitor.
"""
import sys
import os
import platform

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        import PySide6
        print("✓ PySide6 imported successfully")
    except ImportError as e:
        print(f"✗ PySide6 import failed: {e}")
        return False
    
    try:
        import serial
        print("✓ Serial module imported successfully")
    except ImportError as e:
        print(f"✗ Serial module import failed: {e}")
        return False
    
    try:
        import pyqtgraph
        print("✓ PyQtGraph imported successfully")
    except ImportError as e:
        print(f"✗ PyQtGraph import failed: {e}")
        return False
    
    try:
        from monitoring.ui.main_window import main
        print("✓ Main window module imported successfully")
    except ImportError as e:
        print(f"✗ Main window import failed: {e}")
        return False
    
    return True

def test_platform_compatibility():
    """Test platform-specific compatibility."""
    print(f"\nPlatform: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    
    # Test temp directory access
    import tempfile
    temp_dir = tempfile.gettempdir()
    print(f"✓ Temp directory accessible: {temp_dir}")
    
    # Test file operations
    test_file = os.path.join(temp_dir, "test_windows_compatibility.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("Test")
        with open(test_file, 'r') as f:
            content = f.read()
        os.remove(test_file)
        print("✓ File operations working")
    except Exception as e:
        print(f"✗ File operations failed: {e}")
        return False
    
    return True

def test_serial_detection():
    """Test serial port detection."""
    print("\nTesting serial port detection...")
    
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        print(f"✓ Found {len(ports)} serial ports:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")
    except Exception as e:
        print(f"✗ Serial port detection failed: {e}")
        return False
    
    return True

def main():
    """Run all compatibility tests."""
    print("=" * 50)
    print("Windows Compatibility Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test platform compatibility
    if not test_platform_compatibility():
        all_tests_passed = False
    
    # Test serial detection
    if not test_serial_detection():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All tests passed! Application should work on Windows.")
        print("\nTo start the application, run:")
        print("  python -m monitoring.ui.main_window")
        print("  or")
        print("  .\\start_windows.ps1")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 50)

if __name__ == "__main__":
    main() 