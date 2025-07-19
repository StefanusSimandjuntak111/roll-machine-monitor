@echo off
REM Windows startup script for Roll Machine Monitor
REM This script sets up the environment and starts the application

echo Starting Roll Machine Monitor for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv_windows\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv_windows
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_windows\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv_windows\Lib\site-packages\PySide6" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set PYTHONPATH to include current directory
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Start the application
echo Starting application...
python -c "import sys; sys.path.insert(0, '.'); from monitoring.ui.main_window import main; main()"

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
) 