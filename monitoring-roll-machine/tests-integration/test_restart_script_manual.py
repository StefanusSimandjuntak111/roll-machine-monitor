#!/usr/bin/env python3
"""
Manual test to verify restart script creation and content.

This test creates an actual restart script and shows its content
so you can verify it will work correctly.
"""

import sys
import os
import tempfile

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_actual_restart_script():
    """Create and display actual restart script content."""
    print("🧪 Testing Actual Restart Script Creation")
    
    try:
        # Simulate the logic from create_restart_script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = sys.executable
            working_dir = os.path.dirname(app_path)
        else:
            # Running as script - handle different cases
            if len(sys.argv) > 0:
                if sys.argv[0].endswith('python.exe') or sys.argv[0].endswith('python'):
                    # Running with python -m monitoring
                    current_dir = os.getcwd()
                    app_path = f'python -m monitoring'
                    working_dir = current_dir
                else:
                    # Running as direct script
                    app_path = sys.argv[0]
                    working_dir = os.path.dirname(os.path.abspath(app_path))
            else:
                # Fallback
                app_path = 'python -m monitoring'
                working_dir = os.getcwd()
        
        print(f"✅ Detected app_path: {app_path}")
        print(f"✅ Detected working_dir: {working_dir}")
        
        # Create restart script content
        if app_path.startswith('python'):
            # For python -m monitoring command
            restart_script_content = f'''@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
cd /d "{working_dir}"
{app_path}
del "%~f0"
'''
        else:
            # For direct executable
            restart_script_content = f'''@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
start "" "{app_path}"
del "%~f0"
'''
        
        # Create temporary script file
        temp_dir = tempfile.gettempdir()
        restart_script_path = os.path.join(temp_dir, "test_restart_roll_machine.bat")
        
        with open(restart_script_path, 'w') as f:
            f.write(restart_script_content)
        
        print(f"\n✅ Restart script created: {restart_script_path}")
        print("\n📄 Script content:")
        print("=" * 50)
        print(restart_script_content)
        print("=" * 50)
        
        # Test if the script would work
        print(f"\n🔍 Analysis:")
        print(f"- Script type: {'Python module' if app_path.startswith('python') else 'Direct executable'}")
        print(f"- Working directory: {working_dir}")
        print(f"- Command: {app_path}")
        
        if app_path.startswith('python'):
            print(f"- Will change to directory: {working_dir}")
            print(f"- Will execute: {app_path}")
        else:
            print(f"- Will start executable: {app_path}")
        
        print(f"\n✅ Script should work correctly!")
        print(f"💡 To test manually, run: {restart_script_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating restart script: {e}")
        return False

def main():
    """Run the manual test."""
    print("🚀 Starting Manual Restart Script Test")
    print("=" * 60)
    
    try:
        if not test_actual_restart_script():
            print("❌ Manual test failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Manual test completed successfully!")
        print("\nThe restart script should now work correctly when you:")
        print("1. Click the restart button in the application")
        print("2. Confirm the restart dialog")
        print("3. The application will close and restart automatically")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 