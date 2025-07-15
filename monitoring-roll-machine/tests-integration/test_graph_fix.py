#!/usr/bin/env python3
"""
Test script untuk verifikasi perbaikan graph error.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from monitoring.ui.monitoring_view import MonitoringView
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    
    print("✅ Import successful")
    
    # Test UI components
    app = QApplication(sys.argv)
    
    # Test MonitoringView
    monitoring_view = MonitoringView()
    print("✅ MonitoringView created")
    
    # Test multiple data updates to simulate real usage
    for i in range(5):
        test_data = {
            'length_meters': 0.03 + (i * 0.01),
            'speed_mps': 0.0 + (i * 0.1),
            'fields': {
                'speed_text': f'{0.0 + (i * 6.0):.2f} m/min',
                'shift_text': 'Aktif'
            }
        }
        
        monitoring_view.update_data(test_data)
        print(f"✅ Data update {i+1}: Length = {test_data['length_meters']:.2f} m")
    
    # Test cleanup
    monitoring_view.cleanup()
    print("✅ Cleanup successful")
    
    print("\n🎯 Graph Fix Test Complete!")
    print("✅ No RuntimeError occurred")
    print("✅ Safe graph updates implemented")
    print("✅ Cleanup method added")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 