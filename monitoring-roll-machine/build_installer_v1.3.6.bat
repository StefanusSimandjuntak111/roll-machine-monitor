@echo off
REM Build installer for Monitoring Roll Machine v1.3.6
REM This script builds the NSIS installer with Zebra printer fix

echo ========================================
echo Building Monitoring Roll Machine v1.3.6
echo ========================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: NSIS (makensis) is not installed or not in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/
    echo and make sure makensis.exe is in your PATH
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "installer_v1.3.6.nsi" (
    echo ERROR: installer_v1.3.6.nsi not found
    pause
    exit /b 1
)

if not exist "dist\MonitoringRollMachine.exe" (
    echo ERROR: dist\MonitoringRollMachine.exe not found
    echo Please build the application first using build_all_v1.3.6.bat
    pause
    exit /b 1
)

if not exist "LICENSE.txt" (
    echo ERROR: LICENSE.txt not found
    pause
    exit /b 1
)

REM Create version info file
echo Creating version_info.txt...
(
echo VERSION=1.3.6
echo BUILD_DATE=%date%
echo BUILD_TIME=%time%
echo BUILD_TYPE=Release
echo FEATURES=Zebra Printer Fix, Enhanced Printing, Improved Error Handling
) > version_info.txt

REM Build the installer
echo.
echo Building NSIS installer...
echo.

makensis /V2 installer_v1.3.6.nsi

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Installer built successfully!
    echo ========================================
    echo.
    echo Output file: Monitoring-Roll-Machine-v1.3.6-Setup.exe
    echo.
    echo Features included:
    echo - Fixed Zebra ZD230 printer compatibility
    echo - Enhanced printing system
    echo - Improved error handling
    echo - Update capability from previous versions
    echo.
    
    REM Check if installer was created
    if exist "Monitoring-Roll-Machine-v1.3.6-Setup.exe" (
        echo Installer size:
        dir "Monitoring-Roll-Machine-v1.3.6-Setup.exe" | findstr "Monitoring-Roll-Machine-v1.3.6-Setup.exe"
        echo.
        echo You can now distribute this installer to users.
    ) else (
        echo WARNING: Installer file was not created successfully.
    )
) else (
    echo.
    echo ========================================
    echo ERROR: Installer build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo - Missing required files
    echo - NSIS syntax errors
    echo - File permissions
    echo.
)

echo.
echo Build process completed.
pause
