@echo off
echo ========================================
echo Starting Roll Machine Monitor (Kiosk Mode)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found.
    echo Please run setup-environment.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Starting Roll Machine Monitor in Kiosk Mode...
echo This will run in fullscreen mode for production use.
echo.
echo Press Ctrl+C to exit kiosk mode.
echo.

python run_app.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)
