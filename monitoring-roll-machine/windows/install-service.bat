@echo off
echo ========================================
echo Installing Windows Service
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please run the installer as administrator.
    echo.
    pause
    exit /b 1
)

echo Administrator privileges confirmed.
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found.
    echo Please run setup-environment.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

echo Creating Windows service...
echo Service Name: RollMachineMonitor
echo Service Display Name: Roll Machine Monitor
echo Service Description: Industrial monitoring application for JSK3588 roll machines
echo.

REM Create the service using sc command
sc create "RollMachineMonitor" binPath= "\"%CD%\venv\Scripts\python.exe\" \"%CD%\run_app.py\"" DisplayName= "Roll Machine Monitor" start= auto

if %errorlevel% equ 0 (
    echo Service created successfully!
    echo.
    echo Starting service...
    sc start "RollMachineMonitor"
    if %errorlevel% equ 0 (
        echo Service started successfully!
    ) else (
        echo Warning: Service created but could not be started.
        echo You may need to start it manually or check the configuration.
    )
) else (
    echo Failed to create service. Error code: %errorlevel%
    echo.
    echo Please check:
    echo 1. You have administrator privileges
    echo 2. The virtual environment exists
    echo 3. The Python executable path is correct
)

echo.
echo Service installation complete.
pause

