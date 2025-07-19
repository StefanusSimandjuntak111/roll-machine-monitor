@echo off
REM ===============================================
REM Roll Machine Monitor Service Installer v1.3.0
REM ===============================================

setlocal EnableDelayedExpansion

REM Set application directory
set APP_DIR=%~dp0..
cd /d "%APP_DIR%"

echo ==========================================
echo Installing Roll Machine Monitor Service...
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run the installer to set up the environment properly.
    echo.
    pause
    exit /b 1
)

REM Check if service already exists and remove it
sc query RollMachineMonitor >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Service already exists. Stopping and removing old service...
    sc stop RollMachineMonitor >nul 2>&1
    timeout /t 3 >nul
    sc delete RollMachineMonitor >nul 2>&1
    timeout /t 2 >nul
)

REM Create the service
echo Creating Windows service...
sc create RollMachineMonitor binPath= "\"%APP_DIR%\venv\Scripts\python.exe\" \"%APP_DIR%\run_app.py\"" start= auto DisplayName= "Roll Machine Monitor" Description= "Industrial monitoring application for JSK3588 roll machines"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create service!
    echo This might be due to permission issues.
    echo Please ensure the installer is run as Administrator.
    pause
    exit /b 1
)

echo ✅ Service created successfully
echo.

REM Configure service recovery options
echo Configuring service recovery options...
sc failure RollMachineMonitor reset= 86400 actions= restart/60000/restart/60000/restart/60000

if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to configure service recovery options
) else (
    echo ✅ Service recovery configured
)

echo.

REM Start the service
echo Starting service...
sc start RollMachineMonitor

if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to start service automatically
    echo Service will start on next system boot
) else (
    echo ✅ Service started successfully
)

echo.
echo ==========================================
echo Service installation completed!
echo ==========================================
echo.
echo Service name: RollMachineMonitor
echo Service status: Auto-start
echo Recovery: Automatic restart on failure
echo.
echo You can manage the service using:
echo - Services.msc
echo - sc query RollMachineMonitor
echo - sc start/stop RollMachineMonitor
echo.

endlocal
