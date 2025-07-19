@echo off
REM ===============================================
REM Roll Machine Monitor Updater v1.3.0
REM ===============================================

setlocal EnableDelayedExpansion

REM Set application directory
set APP_DIR=%~dp0..
cd /d "%APP_DIR%"

echo ==========================================
echo Roll Machine Monitor Updater
echo ==========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check if application is installed
if not exist "monitoring\config.json" (
    echo ERROR: Roll Machine Monitor not found!
    echo Please install the application first.
    echo.
    pause
    exit /b 1
)

REM Get current version
set CURRENT_VERSION=Unknown
if exist "monitoring\config.json" (
    for /f "tokens=2 delims=:," %%i in ('findstr /C:"version" monitoring\config.json') do (
        set CURRENT_VERSION=%%i
        set CURRENT_VERSION=!CURRENT_VERSION:"=!
        set CURRENT_VERSION=!CURRENT_VERSION: =!
    )
)

echo Current version: %CURRENT_VERSION%
echo.

REM Stop running application and service
echo Stopping application and service...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Roll Machine Monitor*" >nul 2>&1
sc stop RollMachineMonitor >nul 2>&1
timeout /t 3 >nul

REM Create backup directory
set BACKUP_DIR=%APP_DIR%\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

echo Creating backup in: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

REM Backup important files
echo Backing up configuration and data...
if exist "monitoring\config.json" copy "monitoring\config.json" "%BACKUP_DIR%\"
if exist "logs" xcopy "logs" "%BACKUP_DIR%\logs\" /E /I /Y >nul
if exist "exports" xcopy "exports" "%BACKUP_DIR%\exports\" /E /I /Y >nul

echo ✅ Backup completed
echo.

REM Download update (placeholder - implement actual download logic)
echo Checking for updates...
echo.
echo NOTE: This is a placeholder for the update mechanism.
echo In a real implementation, this would:
echo 1. Check for updates from the server
echo 2. Download the new installer
echo 3. Run the installer with update parameters
echo 4. Restore configuration from backup
echo.
echo For now, please download the latest installer manually from:
echo https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
echo.

REM Restore configuration
echo Restoring configuration from backup...
if exist "%BACKUP_DIR%\config.json" (
    copy "%BACKUP_DIR%\config.json" "monitoring\" >nul
    echo ✅ Configuration restored
) else (
    echo WARNING: No configuration backup found
)

echo.
echo ==========================================
echo Update process completed!
echo ==========================================
echo.
echo Backup location: %BACKUP_DIR%
echo.
echo You can now start the application normally.
echo.

endlocal
