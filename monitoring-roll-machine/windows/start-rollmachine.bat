@echo off
REM ===============================================
REM Roll Machine Monitor Startup Script
REM Windows Regular Mode
REM ===============================================

setlocal EnableDelayedExpansion

REM Get the installation directory (parent of windows folder)
set "APP_DIR=%~dp0.."
set "VENV_PYTHON=%APP_DIR%\venv\Scripts\python.exe"
set "LOG_FILE=%APP_DIR%\logs\startup.log"

REM Ensure log directory exists
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"

REM Function to log messages
set "LOG_PREFIX=[%DATE% %TIME%] [STARTUP]"

echo %LOG_PREFIX% Starting Roll Machine Monitor... >> "%LOG_FILE%"
echo.
echo ======================================================
echo 🚀 Starting Roll Machine Monitor
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
echo %LOG_PREFIX% Using Python: %VENV_PYTHON% >> "%LOG_FILE%"

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

echo 🚀 Starting application...
echo %LOG_PREFIX% Starting application in regular mode >> "%LOG_FILE%"

REM Start the application
"%VENV_PYTHON%" -m monitoring

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Application exited with error code %ERRORLEVEL%
    echo %LOG_PREFIX% Application exited with error code %ERRORLEVEL% >> "%LOG_FILE%"
    echo.
    echo Check the log file for details: %LOG_FILE%
    echo Press any key to exit...
    pause >nul
) else (
    echo %LOG_PREFIX% Application exited normally >> "%LOG_FILE%"
)

exit /b %ERRORLEVEL% 