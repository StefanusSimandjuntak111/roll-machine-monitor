@echo off
echo Roll Machine Monitor - Update Script v1.3.4
echo ==============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator...
) else (
    echo Please run this script as administrator
    pause
    exit /b 1
)

REM Check if application is installed
reg query "HKLM\SOFTWARE\RollMachineMonitor" >nul 2>&1
if %errorLevel% == 0 (
    echo Found existing installation.
    for /f "tokens=3" %%i in ('reg query "HKLM\SOFTWARE\RollMachineMonitor" /v "Version" 2^>nul ^| find "Version"') do set CURRENT_VERSION=%%i
    echo Current version: %CURRENT_VERSION%
    
    if "%CURRENT_VERSION%"=="1.3.4" (
        echo Already running the latest version.
        pause
        exit /b 0
    )
    
    echo Updating to version 1.3.4...
    
    REM Create backup
    set INSTALL_DIR=%ProgramFiles%\RollMachineMonitor
    if exist "%INSTALL_DIR%" (
        echo Creating backup...
        set BACKUP_DIR=%INSTALL_DIR%\backup
        if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
        copy "%INSTALL_DIR%\RollMachineMonitor-v%CURRENT_VERSION%.exe" "%BACKUP_DIR%\RollMachineMonitor-v%CURRENT_VERSION%.exe.backup" >nul
    )
) else (
    echo No existing installation found. Installing fresh copy...
)

REM Extract and run installer
echo Extracting installer...
powershell -Command "Expand-Archive -Path 'RollMachineMonitor-v1.3.4-Installer.zip' -DestinationPath '%TEMP%\RollMachineMonitor-install' -Force"

echo Running installer...
cd /d "%TEMP%\RollMachineMonitor-install"
call install.bat

echo.
echo Update completed successfully!
echo.
pause
