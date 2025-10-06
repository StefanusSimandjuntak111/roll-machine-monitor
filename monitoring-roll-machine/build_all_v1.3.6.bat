@echo off
REM Complete build script for Monitoring Roll Machine v1.3.6
REM This script builds the application and creates the installer

echo ========================================
echo Complete Build - Monitoring Roll Machine v1.3.6
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "monitoring\version.py" (
    echo ERROR: Please run this script from the monitoring-roll-machine directory
    pause
    exit /b 1
)

REM Step 1: Update version info
echo Step 1: Updating version information...
echo VERSION=1.3.6 > version_info.txt
echo BUILD_DATE=%date% >> version_info.txt
echo BUILD_TIME=%time% >> version_info.txt
echo BUILD_TYPE=Release >> version_info.txt
echo FEATURES=Zebra Printer Fix, Enhanced Printing, Improved Error Handling >> version_info.txt
echo ✓ Version info updated

REM Step 2: Check Python environment
echo.
echo Step 2: Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python found

REM Step 3: Install/upgrade dependencies
echo.
echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

REM Step 4: Build executable using PyInstaller
echo.
echo Step 4: Building executable...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

pyinstaller --onefile --windowed --name "MonitoringRollMachine" --icon "monitoring\ui\assets\icon.ico" --add-data "monitoring;monitoring" --add-data "config.json;." run_app.py

if %errorlevel% neq 0 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)
echo ✓ Executable built successfully

REM Step 5: Check if executable was created
if not exist "dist\MonitoringRollMachine.exe" (
    echo ERROR: Executable was not created
    pause
    exit /b 1
)

REM Step 6: Build installer
echo.
echo Step 6: Building installer...

REM Check if NSIS is available
where makensis >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: NSIS (makensis) is not installed
    echo Installer will not be built
    echo Please install NSIS from https://nsis.sourceforge.io/
    echo and run build_installer_v1.3.6.bat manually
    goto :end
)

REM Build the installer
makensis /V2 installer_v1.3.6.nsi
if %errorlevel% neq 0 (
    echo ERROR: Failed to build installer
    pause
    exit /b 1
)
echo ✓ Installer built successfully

REM Step 7: Show results
echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Output files:
if exist "dist\MonitoringRollMachine.exe" (
    echo ✓ MonitoringRollMachine.exe
    for %%I in ("dist\MonitoringRollMachine.exe") do echo   Size: %%~zI bytes
)
if exist "Monitoring-Roll-Machine-v1.3.6-Setup.exe" (
    echo ✓ Monitoring-Roll-Machine-v1.3.6-Setup.exe
    for %%I in ("Monitoring-Roll-Machine-v1.3.6-Setup.exe") do echo   Size: %%~zI bytes
)
echo.
echo Features included:
echo - Fixed Zebra ZD230 printer compatibility
echo - Enhanced printing system  
echo - Improved error handling
echo - Update capability from previous versions
echo.
echo You can now distribute the installer to users.

:end
echo.
echo Build process completed.
pause
