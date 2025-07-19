@echo off
REM Simple startup script for Roll Machine Monitor
REM Just double-click this file to start the application

echo Starting Roll Machine Monitor...
echo.

REM Run the Python script
python run_app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
) 