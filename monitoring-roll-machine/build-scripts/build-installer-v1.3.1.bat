@echo off
REM ===============================================
REM Roll Machine Monitor v1.3.1 Installer Builder
REM Smart Settings Update Edition
REM ===============================================

echo.
echo ===============================================
echo Building Roll Machine Monitor v1.3.1 Installer
echo ===============================================
echo.

REM Set version
set VERSION=1.3.1
set APP_NAME=RollMachineMonitor
set OUTPUT_DIR=..\releases\windows
set INSTALLER_NAME=%APP_NAME%-v%VERSION%-Windows-Installer

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" (
    echo Creating output directory: %OUTPUT_DIR%
    mkdir "%OUTPUT_DIR%"
)

REM Check if Inno Setup is installed
set INNO_COMPILER="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_COMPILER% (
    set INNO_COMPILER="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist %INNO_COMPILER% (
    echo ERROR: Inno Setup Compiler not found!
    echo Please install Inno Setup 6.2+ from: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Using Inno Setup Compiler: %INNO_COMPILER%
echo.

REM Build the installer
echo Building installer...
%INNO_COMPILER% installer-roll-machine-v1.3.1.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo SUCCESS: Installer built successfully!
    echo ===============================================
    echo.
    echo Installer location: %OUTPUT_DIR%\%INSTALLER_NAME%.exe
    echo.
    echo Features included:
    echo - Complete application with all features
    echo - Smart Settings Update functionality
    echo - Length tolerance and formatting
    echo - Desktop shortcuts
    echo - Start menu entries
    echo - Uninstaller
    echo - Silent installation support
    echo.
    
    REM Show file size
    for %%A in ("%OUTPUT_DIR%\%INSTALLER_NAME%.exe") do (
        echo File size: %%~zA bytes
    )
    
    echo.
    echo Ready for distribution to users!
    echo.
) else (
    echo.
    echo ===============================================
    echo ERROR: Failed to build installer!
    echo ===============================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause 