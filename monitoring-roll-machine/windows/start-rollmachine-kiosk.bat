@echo off
REM ===============================================
REM Roll Machine Monitor Kiosk Launcher v1.3.0
REM ===============================================

setlocal EnableDelayedExpansion

REM Set application directory
set APP_DIR=%~dp0..
cd /d "%APP_DIR%"

echo ==========================================
echo Starting Roll Machine Monitor (Kiosk Mode)...
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

REM Check if main application file exists
if not exist "run_app.py" (
    echo ERROR: Application file not found!
    echo Please ensure the application is properly installed.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Failed to activate virtual environment!
    echo Please check the installation.
    pause
    exit /b 1
)

REM Start the application in kiosk mode
echo Starting application in kiosk mode...
echo.
venv\Scripts\python.exe run_app.py --kiosk

REM Check if application exited with error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo Please check the logs for more information.
    echo.
    pause
)

endlocal
