@echo off
REM ===============================================
REM Roll Machine Monitor Kiosk Startup Script
REM Windows Kiosk Mode (Fullscreen)
REM ===============================================

setlocal EnableDelayedExpansion

REM Get the installation directory (parent of windows folder)
set "APP_DIR=%~dp0.."
set "VENV_PYTHON=%APP_DIR%\venv\Scripts\python.exe"
set "LOG_FILE=%APP_DIR%\logs\kiosk.log"

REM Ensure log directory exists
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"

REM Function to log messages
set "LOG_PREFIX=[%DATE% %TIME%] [KIOSK]"

echo %LOG_PREFIX% Starting Roll Machine Monitor in Kiosk Mode... >> "%LOG_FILE%"
echo.
echo ======================================================
echo 🖥️ Starting Roll Machine Monitor - KIOSK MODE
echo ======================================================
echo.

REM Check if virtual environment exists
if not exist "%VENV_PYTHON%" (
    echo ❌ Python virtual environment not found!
    echo %LOG_PREFIX% ERROR: Virtual environment not found at %VENV_PYTHON% >> "%LOG_FILE%"
    echo.
    echo Please reinstall Roll Machine Monitor.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Change to application directory
cd /d "%APP_DIR%"
if %ERRORLEVEL% neq 0 (
    echo ❌ Cannot access application directory!
    echo %LOG_PREFIX% ERROR: Cannot access directory %APP_DIR% >> "%LOG_FILE%"
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ Application directory: %APP_DIR%
echo ✅ Python executable: %VENV_PYTHON%
echo ✅ Mode: KIOSK (Fullscreen)
echo %LOG_PREFIX% Using Python: %VENV_PYTHON% >> "%LOG_FILE%"
echo %LOG_PREFIX% Starting in KIOSK mode >> "%LOG_FILE%"

REM Set environment variables for kiosk mode
set "QT_QPA_PLATFORM=windows"
set "ROLLMACHINE_KIOSK_MODE=1"
set "ROLLMACHINE_FULLSCREEN=1"

REM Check for JSK3588 device (optional warning)
echo 🔍 Checking for serial devices...
for /f %%i in ('powershell -command "Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like '*COM*' -or $_.Name -like '*Serial*' -or $_.Name -like '*USB*'} | Measure-Object | Select-Object -ExpandProperty Count"') do set "SERIAL_COUNT=%%i"

if "%SERIAL_COUNT%"=="0" (
    echo ⚠️ No serial devices detected
    echo %LOG_PREFIX% WARNING: No serial devices detected >> "%LOG_FILE%"
    echo    Make sure your JSK3588 device is connected
    echo.
) else (
    echo ✅ Found %SERIAL_COUNT% serial/USB device(s)
    echo %LOG_PREFIX% Found %SERIAL_COUNT% serial devices >> "%LOG_FILE%"
)

REM Hide taskbar (optional for true kiosk experience)
echo 🔒 Preparing kiosk environment...
powershell -command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Taskbar { [DllImport(\"user32.dll\")] public static extern int ShowWindow(IntPtr hwnd, int nCmdShow); [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName); public static void Hide() { ShowWindow(FindWindow(\"Shell_TrayWnd\", null), 0); } public static void Show() { ShowWindow(FindWindow(\"Shell_TrayWnd\", null), 9); } }'; [Taskbar]::Hide()" 2>nul

echo 🚀 Starting application in kiosk mode...
echo %LOG_PREFIX% Starting application in kiosk mode >> "%LOG_FILE%"

REM Start the application with kiosk configuration
"%VENV_PYTHON%" -c "
import sys
import os
sys.path.insert(0, os.getcwd())

# Set kiosk mode environment
os.environ['ROLLMACHINE_KIOSK_MODE'] = '1'
os.environ['ROLLMACHINE_FULLSCREEN'] = '1'

try:
    # Try to run kiosk mode if available
    from monitoring.ui.kiosk_ui import MonitoringKioskApp
    print('[KIOSK] Starting kiosk UI...')
    app = MonitoringKioskApp()
    app.run()
except ImportError:
    # Fallback to regular mode with fullscreen
    print('[KIOSK] Kiosk UI not available, using regular mode with fullscreen')
    import monitoring.__main__
except Exception as e:
    print(f'[KIOSK] Error: {e}')
    import monitoring.__main__
"

REM Get exit code
set "EXIT_CODE=%ERRORLEVEL%"

REM Restore taskbar
echo 🔓 Restoring taskbar...
powershell -command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Taskbar { [DllImport(\"user32.dll\")] public static extern int ShowWindow(IntPtr hwnd, int nCmdShow); [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName); public static void Hide() { ShowWindow(FindWindow(\"Shell_TrayWnd\", null), 0); } public static void Show() { ShowWindow(FindWindow(\"Shell_TrayWnd\", null), 9); } }'; [Taskbar]::Show()" 2>nul

REM Check exit code
if %EXIT_CODE% neq 0 (
    echo.
    echo ❌ Application exited with error code %EXIT_CODE%
    echo %LOG_PREFIX% Application exited with error code %EXIT_CODE% >> "%LOG_FILE%"
    echo.
    echo Check the log file for details: %LOG_FILE%
    echo Press any key to exit...
    pause >nul
) else (
    echo %LOG_PREFIX% Application exited normally >> "%LOG_FILE%"
)

exit /b %EXIT_CODE% 