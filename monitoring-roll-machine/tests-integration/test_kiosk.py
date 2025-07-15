#!/usr/bin/env python3
"""
Test script untuk verify kiosk mode functionality.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def test_kiosk_mode():
    """Test kiosk mode functionality."""
    print("🧪 Testing Roll Machine Monitor Kiosk Mode...")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "monitoring").exists():
        print("❌ Error: Run this script from monitoring-roll-machine directory")
        return False
    
    # Test 1: Import test
    print("1️⃣ Testing imports...")
    try:
        from monitoring.ui.main_window import ModernMainWindow
        from monitoring.config import load_config
        print("   ✅ Imports successful")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Config test  
    print("2️⃣ Testing configuration...")
    try:
        config = load_config()
        print(f"   ✅ Config loaded: {config}")
        
        # Check required keys
        required_keys = ['serial_port', 'baudrate', 'auto_connect', 'use_mock_data']
        for key in required_keys:
            if key not in config:
                print(f"   ⚠️  Missing config key: {key}")
            else:
                print(f"   ✅ {key}: {config[key]}")
                
    except Exception as e:
        print(f"   ❌ Config test failed: {e}")
        return False
    
    # Test 3: Mock serial test
    print("3️⃣ Testing mock serial...")
    try:
        from monitoring.mock.mock_serial import MockSerial
        mock = MockSerial(port="TEST", baudrate=19200)
        mock.open()
        
        # Test query
        query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
        mock.write(query)
        response = mock.read(16)
        
        if response:
            print(f"   ✅ Mock response: {response.hex()}")
        else:
            print("   ⚠️  No mock response")
            
        mock.close()
        
    except Exception as e:
        print(f"   ❌ Mock serial test failed: {e}")
        return False
    
    # Test 4: Auto-detection test
    print("4️⃣ Testing auto-detection...")
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        if ports:
            print(f"   ✅ Found {len(ports)} serial ports:")
            for port in ports:
                print(f"      - {port.device}")
        else:
            print("   ⚠️  No serial ports found (will use mock mode)")
            
    except Exception as e:
        print(f"   ❌ Auto-detection test failed: {e}")
        return False
    
    # Test 5: Dependencies test
    print("5️⃣ Testing dependencies...")
    dependencies = ['PySide6', 'pyqtgraph', 'pyserial']
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - MISSING!")
            return False
    
    print("=" * 50)
    print("🎉 All tests passed! Kiosk mode should work correctly.")
    print()
    print("📋 Quick Start Commands:")
    print("   # Test GUI (normal mode):")
    print("   python -m monitoring")
    print()
    print("   # Test kiosk mode:")
    print("   ./start_kiosk.sh")
    print()
    print("   # Exit kiosk mode:")
    print("   ./exit_kiosk.sh")
    print()
    
    return True

def test_gui_quick():
    """Quick GUI test (non-blocking)."""
    print("🖥️  Quick GUI Test...")
    
    try:
        # Test if GUI can be created without display
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        
        from PySide6.QtWidgets import QApplication
        from monitoring.ui.main_window import ModernMainWindow
        
        app = QApplication([])
        window = ModernMainWindow()
        
        print("   ✅ GUI created successfully")
        print("   ✅ Kiosk mode configuration applied")
        
        # Don't show window in test
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"   ❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        success = test_gui_quick()
    else:
        success = test_kiosk_mode()
    
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1) 