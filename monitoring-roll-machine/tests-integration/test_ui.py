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

def test_form_field():
    """Test FormField class."""
    print("\nTesting FormField...")
    
    try:
        from monitoring.ui.kiosk_ui import FormField
        
        # Test basic field
        field = FormField("Test Label", "Test Hint")
        assert field.label.text == "Test Label"
        assert field.text_field.hint_text == "Test Hint"
        print("✓ FormField basic functionality works")
        
        # Test readonly field
        readonly_field = FormField("Readonly", "Hint", readonly=True)
        assert readonly_field.text_field.readonly == True
        print("✓ FormField readonly functionality works")
        
        return True
    except Exception as e:
        print(f"✗ FormField test failed: {e}")
        return False

def test_product_form():
    """Test ProductForm class."""
    print("\nTesting ProductForm...")
    
    try:
        from monitoring.ui.kiosk_ui import ProductForm
        
        form = ProductForm()
        
        # Test that all fields are created
        assert hasattr(form, 'item_code_button')
        assert hasattr(form, 'product_name_field')
        assert hasattr(form, 'actual_length_field')
        assert hasattr(form, 'unit_button')
        assert hasattr(form, 'converted_length_field')
        print("✓ ProductForm fields created successfully")
        
        # Test unit conversion
        form.actual_length_field.text_field.text = "10.0"
        form.unit_button.text = "yard"
        form.update_converted_length()
        expected = "10.94 yard"  # 10 * 1.09361
        assert form.converted_length_field.text_field.text == expected
        print("✓ Unit conversion works correctly")
        
        return True
    except Exception as e:
        print(f"✗ ProductForm test failed: {e}")
        return False

def test_connection_settings():
    """Test ConnectionSettings class."""
    print("\nTesting ConnectionSettings...")
    
    try:
        from monitoring.ui.kiosk_ui import ConnectionSettings
        
        settings = ConnectionSettings()
        
        # Test that all components are created
        assert hasattr(settings, 'port_button')
        assert hasattr(settings, 'auto_connect')
        assert hasattr(settings, 'port_status')
        print("✓ ConnectionSettings components created successfully")
        
        # Test port selection
        settings.select_port("COM1")
        assert settings.port_button.text == "COM1"
        print("✓ Port selection works")
        
        # Test no port state
        settings._set_no_port_state()
        assert settings.port_button.text == "PORT"
        assert settings.port_status.text == "Port Tidak Ditemukan"
        print("✓ No port state works")
        
        return True
    except Exception as e:
        print(f"✗ ConnectionSettings test failed: {e}")
        return False

def test_machine_status():
    """Test MachineStatus class."""
    print("\nTesting MachineStatus...")
    
    try:
        from monitoring.ui.kiosk_ui import MachineStatus
        
        status = MachineStatus()
        
        # Test that all components are created
        assert hasattr(status, 'rolled_length')
        assert hasattr(status, 'speed_label')
        assert hasattr(status, 'shift_label')
        print("✓ MachineStatus components created successfully")
        
        # Test status update
        status.update_status(100.5, 2.5, 1)
        assert status.rolled_length.text == "100.5"
        assert status.speed_label.text == "2.5 m/s"
        assert status.shift_label.text == "Shift 1"
        print("✓ Status update works")
        
        return True
    except Exception as e:
        print(f"✗ MachineStatus test failed: {e}")
        return False

def test_control_buttons():
    """Test ControlButtons class."""
    print("\nTesting ControlButtons...")
    
    try:
        from monitoring.ui.kiosk_ui import ControlButtons
        
        buttons = ControlButtons()
        
        # Test that buttons are created
        assert hasattr(buttons, 'start_button')
        assert hasattr(buttons, 'save_button')
        print("✓ ControlButtons created successfully")
        
        return True
    except Exception as e:
        print(f"✗ ControlButtons test failed: {e}")
        return False

def test_statistics():
    """Test Statistics class."""
    print("\nTesting Statistics...")
    
    try:
        from monitoring.ui.kiosk_ui import Statistics
        
        stats = Statistics()
        
        # Test that graphs are created
        assert hasattr(stats, 'length_graph')
        assert hasattr(stats, 'speed_graph')
        print("✓ Statistics graphs created successfully")
        
        # Test data update
        test_data = {
            'length': 50.0,
            'speed': 2.5,
            'timestamp': '2024-03-20 10:00:00'
        }
        stats.update_data(test_data)
        print("✓ Statistics data update works")
        
        return True
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting UI Component Tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_form_field,
        test_product_form,
        test_connection_settings,
        test_machine_status,
        test_control_buttons,
        test_statistics,
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
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 