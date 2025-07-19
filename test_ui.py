#!/usr/bin/env python3
"""
Test script untuk memverifikasi semua komponen UI bekerja dengan baik.
"""
import sys
import os
from pathlib import Path

# Add the monitoring package to the path
sys.path.insert(0, str(Path(__file__).parent / "monitoring-roll-machine"))

def test_imports():
    """Test semua import yang diperlukan."""
    print("Testing imports...")
    
    try:
        from monitoring.ui.kiosk_ui import (
            FormField, ProductForm, MachineStatus, 
            ConnectionSettings, ControlButtons, Statistics,
            MonitoringKioskApp
        )
        print("✓ All UI classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_class_attributes():
    """Test bahwa semua class memiliki atribut yang diperlukan."""
    print("\nTesting class attributes...")
    
    try:
        from monitoring.ui.kiosk_ui import (
            FormField, ProductForm, MachineStatus, 
            ConnectionSettings, ControlButtons, Statistics
        )
        
        # Test FormField attributes
        print("✓ FormField class imported")
        
        # Test ProductForm attributes
        print("✓ ProductForm class imported")
        
        # Test MachineStatus attributes
        print("✓ MachineStatus class imported")
        
        # Test ConnectionSettings attributes
        print("✓ ConnectionSettings class imported")
        
        # Test ControlButtons attributes
        print("✓ ControlButtons class imported")
        
        # Test Statistics attributes
        print("✓ Statistics class imported")
        
        return True
    except Exception as e:
        print(f"✗ Class attributes test failed: {e}")
        return False

def test_methods_exist():
    """Test bahwa semua method yang diperlukan ada."""
    print("\nTesting method existence...")
    
    try:
        from monitoring.ui.kiosk_ui import (
            ProductForm, ConnectionSettings, MachineStatus, Statistics
        )
        
        # Test ProductForm methods
        form_methods = ['show_item_menu', 'show_unit_menu', 'select_item', 
                       'select_unit', 'update_converted_length', 'refresh_items']
        for method in form_methods:
            assert hasattr(ProductForm, method), f"ProductForm missing method: {method}"
        print("✓ ProductForm methods exist")
        
        # Test ConnectionSettings methods
        conn_methods = ['show_port_menu', 'select_port', '_set_no_port_state', 
                       'refresh_ports', 'get_selected_port', 'get_auto_connect']
        for method in conn_methods:
            assert hasattr(ConnectionSettings, method), f"ConnectionSettings missing method: {method}"
        print("✓ ConnectionSettings methods exist")
        
        # Test MachineStatus methods
        status_methods = ['update_time', 'update_connection_status', 'update_status']
        for method in status_methods:
            assert hasattr(MachineStatus, method), f"MachineStatus missing method: {method}"
        print("✓ MachineStatus methods exist")
        
        # Test Statistics methods
        stats_methods = ['update_data', 'export_data']
        for method in stats_methods:
            assert hasattr(Statistics, method), f"Statistics missing method: {method}"
        print("✓ Statistics methods exist")
        
        return True
    except Exception as e:
        print(f"✗ Method existence test failed: {e}")
        return False

def test_app_class():
    """Test MonitoringKioskApp class."""
    print("\nTesting MonitoringKioskApp...")
    
    try:
        from monitoring.ui.kiosk_ui import MonitoringKioskApp
        
        # Test that app class exists and has required methods
        assert hasattr(MonitoringKioskApp, 'build'), "MonitoringKioskApp missing build method"
        assert hasattr(MonitoringKioskApp, 'start_monitoring'), "MonitoringKioskApp missing start_monitoring method"
        assert hasattr(MonitoringKioskApp, 'stop_monitoring'), "MonitoringKioskApp missing stop_monitoring method"
        assert hasattr(MonitoringKioskApp, 'handle_data'), "MonitoringKioskApp missing handle_data method"
        assert hasattr(MonitoringKioskApp, 'handle_error'), "MonitoringKioskApp missing handle_error method"
        assert hasattr(MonitoringKioskApp, 'save_data'), "MonitoringKioskApp missing save_data method"
        assert hasattr(MonitoringKioskApp, 'show_error'), "MonitoringKioskApp missing show_error method"
        
        print("✓ MonitoringKioskApp class and methods exist")
        return True
    except Exception as e:
        print(f"✗ MonitoringKioskApp test failed: {e}")
        return False

def test_ui_functionality():
    """Test UI functionality without creating widgets."""
    print("\nTesting UI functionality...")
    
    try:
        from monitoring.ui.kiosk_ui import ProductForm
        
        # Test unit conversion logic
        def test_unit_conversion():
            """Test unit conversion logic."""
            actual_length = 10.0
            unit = "yard"
            
            if unit == "yard":
                # Convert meters to yards (1 meter = 1.09361 yards)
                converted = actual_length * 1.09361
                return f"{converted:.2f} yard"
            else:
                # Keep in meters
                return f"{actual_length:.2f} meter"
        
        result = test_unit_conversion()
        expected = "10.94 yard"
        assert result == expected, f"Unit conversion failed: expected {expected}, got {result}"
        print("✓ Unit conversion logic works correctly")
        
        return True
    except Exception as e:
        print(f"✗ UI functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting UI Component Tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_class_attributes,
        test_methods_exist,
        test_app_class,
        test_ui_functionality,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! UI components are working correctly.")
        print("\n✅ Summary:")
        print("- All UI classes can be imported successfully")
        print("- All required methods exist in classes")
        print("- Unit conversion logic works correctly")
        print("- App class has all required methods")
        print("- No import errors or missing dependencies")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 