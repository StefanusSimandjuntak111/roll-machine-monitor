@echo off
REM ===============================================
REM Uninstall Roll Machine Monitor Windows Service
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ======================================================
echo 🗑️ Uninstalling Roll Machine Monitor Windows Service
echo ======================================================
echo.

REM Get the installation directory (parent of windows folder)
set "APP_DIR=%~dp0.."
set "VENV_PYTHON=%APP_DIR%\venv\Scripts\python.exe"
set "SERVICE_SCRIPT=%~dp0rollmachine-service.py"

REM Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ This script must be run as Administrator
    echo    Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Check if virtual environment exists
if not exist "%VENV_PYTHON%" (
    echo ❌ Python virtual environment not found!
    echo    Expected: %VENV_PYTHON%
    echo    Cannot uninstall service without Python environment
    echo.
    pause
    exit /b 1
)

echo ✅ Python virtual environment found

REM Check if service script exists
if not exist "%SERVICE_SCRIPT%" (
    echo ❌ Service script not found!
    echo    Expected: %SERVICE_SCRIPT%
    echo    Cannot uninstall service without service script
    echo.
    pause
    exit /b 1
)

echo ✅ Service script found

REM Check current service status
echo 🔍 Checking current service status...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" status

REM Stop the service
echo 🛑 Stopping service...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" stop
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Warning: Failed to stop service (may not be running)
) else (
    echo ✅ Service stopped successfully
)

REM Wait a moment for service to fully stop
echo ⏳ Waiting for service to stop completely...
timeout /t 3 /nobreak >nul

REM Remove the service
echo 🗑️ Removing Windows service...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" remove
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to remove service
    echo    The service may not be installed or may require manual removal
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo 🎉 Service Uninstallation Completed!
echo ======================================================
echo.
echo ✅ Roll Machine Monitor Service has been removed
echo ✅ Service will no longer start automatically with Windows
echo.
echo 📝 Note: Application files and data remain intact
echo    Only the Windows service has been removed
echo.
echo 🔄 To reinstall the service later, run:
echo    install-service.bat
echo.

pause 