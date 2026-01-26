@echo off
REM Build script for Monitoring Roll Machine v1.4.4 Installer
REM This script builds the complete installer package

echo ========================================
echo Building Monitoring Roll Machine v1.4.4
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Run the build script
python build_v1.4.4.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL
    echo ========================================
    echo.
    echo Installer location: releases\Monitoring-Roll-Machine-v1.4.4-Setup.exe
    echo.
)

pause
