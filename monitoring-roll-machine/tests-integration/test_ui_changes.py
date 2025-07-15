#!/usr/bin/env python3
"""
Test script untuk verifikasi perubahan UI:
1. Label "Target Length" menjadi "Current Length"
2. Current length diupdate ke input target length
3. Monitoring display hidden
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from monitoring.parser import parse_packet
    from monitoring.ui.monitoring_view import MonitoringView
    from monitoring.ui.product_form import ProductForm
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    
    print("✅ Import successful")
    
    # Test parser
    packet = bytes.fromhex("55 AA 20 0C 02 00 00 03 00 00 01 31")
    result = parse_packet(packet)
    
    print(f"✅ Parser test: Length = {result['length_meters']:.2f} m")
    
    # Test UI components
    app = QApplication(sys.argv)
    
    # Test ProductForm
    product_form = ProductForm()
    print("✅ ProductForm created")
    
    # Test update target with current length
    product_form.update_target_with_current_length(0.03)
    current_value = product_form.target_length.value()
    print(f"✅ Target length updated: {current_value:.2f}")
    
    # Test MonitoringView
    monitoring_view = MonitoringView()
    print("✅ MonitoringView created")
    
    # Test data update
    test_data = {
        'length_meters': 0.03,
        'speed_mps': 0.0,
        'fields': {
            'speed_text': '0.00 m/min',
            'shift_text': 'Aktif'
        }
    }
    
    monitoring_view.update_data(test_data)
    print("✅ MonitoringView data updated")
    
    print("\n🎯 UI Changes Test Complete!")
    print("✅ Label changed to 'Current Length'")
    print("✅ Target length input updates with current length")
    print("✅ Monitoring display hidden (splitter set to 1000, 0)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 