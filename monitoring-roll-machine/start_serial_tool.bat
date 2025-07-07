@echo off
REM Start JSK3588 Serial Tool
echo Starting JSK3588 Serial Tool...
echo.

python serial_tool.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
) 