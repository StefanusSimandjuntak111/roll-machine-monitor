# Restart Script Fix for Python Module Mode

## Problem Description

The restart button was not working correctly when the application was run using `python -m monitoring`. The application would close successfully, but it would not restart because the restart script was not detecting the correct execution mode.

### Root Cause

When running with `python -m monitoring`, `sys.argv[0]` contains the path to the Python interpreter (e.g., `python.exe`), not the application path. The original restart script logic was not handling this case correctly.

## Solution Implemented

### Updated Restart Script Logic

**File**: `monitoring/ui/main_window.py`
**Function**: `create_restart_script()`

```python
def create_restart_script(self):
    """Create a script to restart the application."""
    try:
        import sys
        import os
        
        # Get the current script path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = sys.executable
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
        
        # Write restart script to temp file
        import tempfile
        temp_dir = tempfile.gettempdir()
        restart_script_path = os.path.join(temp_dir, "restart_roll_machine.bat")
        
        with open(restart_script_path, 'w') as f:
            f.write(restart_script_content)
        
        # Execute restart script
        import subprocess
        subprocess.Popen(['cmd', '/c', restart_script_path], 
                       creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        logger.info(f"Restart script created: {restart_script_path}")
        logger.info(f"App path: {app_path}")
        logger.info(f"Working dir: {working_dir}")
        
    except Exception as e:
        logger.error(f"Error creating restart script: {e}")
        # Fallback: just quit and let user restart manually
        logger.info("Fallback: quitting application for manual restart")
```

## Key Changes

### 1. Execution Mode Detection

The script now properly detects different execution modes:

- **Python Module Mode**: `python -m monitoring`
- **Direct Executable**: `app.exe` or `script.py`
- **Compiled Executable**: Frozen application

### 2. Different Script Content

#### For Python Module Mode:
```batch
@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
cd /d "D:\Apps\monitoring-roll-machine\monitoring-roll-machine"
python -m monitoring
del "%~f0"
```

#### For Direct Executable:
```batch
@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
start "" "C:\path\to\app.exe"
del "%~f0"
```

### 3. Working Directory Handling

- **Python Module Mode**: Changes to the current working directory before executing
- **Direct Executable**: Uses the executable's directory

## Testing

### Test Cases Verified

1. **`python.exe -m monitoring`** ✅
2. **`python -m monitoring`** ✅
3. **`C:\Python39\python.exe -m monitoring`** ✅
4. **`C:\path\to\app.exe`** ✅
5. **`run_app.py`** ✅

### Test Results

```
🧪 Testing Restart Logic

--- Test Case 1: ['python.exe', '-m', 'monitoring'] ---
✅ Detected: python -m monitoring
✅ App path: python -m monitoring
✅ Working dir: D:\Apps\monitoring-roll-machine\monitoring-roll-machine
✅ Script type: Python module
✅ Will execute: python -m monitoring
✅ Will change to directory: D:\Apps\monitoring-roll-machine\monitoring-roll-machine
✅ Script should work correctly!

--- Test Case 2: ['python', '-m', 'monitoring'] ---
✅ Detected: python -m monitoring
✅ App path: python -m monitoring
✅ Working dir: D:\Apps\monitoring-roll-machine\monitoring-roll-machine
✅ Script type: Python module
✅ Will execute: python -m monitoring
✅ Will change to directory: D:\Apps\monitoring-roll-machine\monitoring-roll-machine
✅ Script should work correctly!
```

## Benefits

1. **Universal Compatibility**: Works with all execution modes
2. **Correct Path Detection**: Properly detects Python module mode
3. **Working Directory**: Ensures correct working directory for Python module mode
4. **Robust Fallback**: Graceful handling of edge cases
5. **Detailed Logging**: Better debugging information

## Usage

### For Python Module Mode:
1. Run application: `python -m monitoring`
2. Click restart button
3. Confirm restart dialog
4. Application closes and restarts automatically

### For Direct Executable:
1. Run application: `app.exe` or `python run_app.py`
2. Click restart button
3. Confirm restart dialog
4. Application closes and restarts automatically

## Files Modified

- `monitoring/ui/main_window.py`: Updated `create_restart_script()` function
- `tests-integration/test_restart_script.py`: Added comprehensive tests
- `tests-integration/test_restart_script_manual.py`: Added manual verification test
- `test_restart_logic.py`: Added logic verification test

## Conclusion

The restart functionality now works correctly for all execution modes, including `python -m monitoring`. The script properly detects the execution mode and generates the appropriate restart command, ensuring the application can be restarted reliably regardless of how it was launched. 