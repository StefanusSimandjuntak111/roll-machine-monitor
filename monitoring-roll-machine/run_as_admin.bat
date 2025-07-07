@echo off
REM Run Roll Machine Monitor with elevated permissions
REM This script will request admin privileges and run the application

echo Requesting administrator privileges...
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Already running as administrator.
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo Starting Roll Machine Monitor with admin privileges...
echo.

REM Change to the correct directory
cd /d "%~dp0monitoring-roll-machine"

REM Set PYTHONPATH to include current directory
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Activate virtual environment if it exists
if exist "venv_windows\Scripts\activate.bat" (
    call venv_windows\Scripts\activate.bat
)

REM Run the application with proper path
python -c "import sys; sys.path.insert(0, '.'); from monitoring.ui.main_window import main; main()"

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
) 