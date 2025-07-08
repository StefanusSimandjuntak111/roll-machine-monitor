@echo off
REM ===============================================
REM Install Roll Machine Monitor Windows Service
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ======================================================
echo 🔧 Installing Roll Machine Monitor Windows Service
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
    echo    Please run setup-environment.bat first
    echo.
    pause
    exit /b 1
)

echo ✅ Python virtual environment found

REM Check if service script exists
if not exist "%SERVICE_SCRIPT%" (
    echo ❌ Service script not found!
    echo    Expected: %SERVICE_SCRIPT%
    echo.
    pause
    exit /b 1
)

echo ✅ Service script found

REM Stop existing service if it exists
echo 🛑 Stopping existing service (if any)...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" stop >nul 2>&1

REM Remove existing service if it exists
echo 🧹 Removing existing service (if any)...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" remove >nul 2>&1

REM Install the service
echo 📦 Installing Windows service...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install service
    echo.
    pause
    exit /b 1
)

REM Start the service
echo 🚀 Starting service...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" start
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start service
    echo.
    pause
    exit /b 1
)

REM Check service status
echo 🔍 Checking service status...
"%VENV_PYTHON%" "%SERVICE_SCRIPT%" status

echo.
echo ======================================================
echo 🎉 Service Installation Completed!
echo ======================================================
echo.
echo ✅ Roll Machine Monitor Service has been installed
echo ✅ Service is set to start automatically with Windows
echo ✅ Service is currently running
echo.
echo 📋 Service Management Commands:
echo    Start:   "%VENV_PYTHON%" "%SERVICE_SCRIPT%" start
echo    Stop:    "%VENV_PYTHON%" "%SERVICE_SCRIPT%" stop
echo    Restart: "%VENV_PYTHON%" "%SERVICE_SCRIPT%" restart
echo    Status:  "%VENV_PYTHON%" "%SERVICE_SCRIPT%" status
echo.
echo 📝 Service logs are saved to:
echo    %APP_DIR%\logs\service.log
echo.

pause 