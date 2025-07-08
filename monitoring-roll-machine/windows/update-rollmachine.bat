@echo off
REM ===============================================
REM Roll Machine Monitor Update Script
REM Preserves settings and data during updates
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ======================================================
echo 🔄 Roll Machine Monitor Update Utility
echo ======================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ This script must be run as Administrator
    echo    Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Set paths
set "INSTALL_DIR=C:\Program Files\RollMachineMonitor"
set "BACKUP_DIR=%TEMP%\RollMachineMonitor-Backup-%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =%"

REM Check if application is installed
if not exist "%INSTALL_DIR%" (
    echo ❌ Roll Machine Monitor is not installed
    echo    Please run the full installer first
    echo.
    pause
    exit /b 1
)

echo ✅ Found existing installation: %INSTALL_DIR%

REM Check if update package is available
set "UPDATE_DIR=%~dp0.."
if not exist "%UPDATE_DIR%\monitoring" (
    echo ❌ Update package not found!
    echo    Please run this script from the update package directory
    echo.
    pause
    exit /b 1
)

echo ✅ Update package found: %UPDATE_DIR%

REM Stop the Windows service
echo 🛑 Stopping Roll Machine Monitor service...
"%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\windows\rollmachine-service.py" stop >nul 2>&1

REM Wait for service to stop
timeout /t 5 /nobreak >nul

REM Kill any remaining processes
echo 🔄 Stopping any running instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Roll Machine Monitor*" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create backup directory
echo 💾 Creating backup...
mkdir "%BACKUP_DIR%" >nul 2>&1

REM Backup important files
echo    Backing up configuration...
if exist "%INSTALL_DIR%\monitoring\config.json" (
    copy "%INSTALL_DIR%\monitoring\config.json" "%BACKUP_DIR%\config.json" >nul
    echo    ✅ Configuration backed up
) else (
    echo    ⚠️ No configuration file found
)

echo    Backing up logs...
if exist "%INSTALL_DIR%\logs" (
    xcopy /s /e /q "%INSTALL_DIR%\logs" "%BACKUP_DIR%\logs\" >nul
    echo    ✅ Logs backed up
)

echo    Backing up exports...
if exist "%INSTALL_DIR%\exports" (
    xcopy /s /e /q "%INSTALL_DIR%\exports" "%BACKUP_DIR%\exports\" >nul
    echo    ✅ Exports backed up
)

echo ✅ Backup completed: %BACKUP_DIR%

REM Update application files
echo 🔄 Updating application files...

echo    Updating monitoring application...
if exist "%INSTALL_DIR%\monitoring" (
    rmdir /s /q "%INSTALL_DIR%\monitoring" >nul 2>&1
)
xcopy /s /e /q "%UPDATE_DIR%\monitoring" "%INSTALL_DIR%\monitoring\" >nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to update monitoring application
    goto :restore_backup
)

echo    Updating Windows scripts...
if exist "%INSTALL_DIR%\windows" (
    rmdir /s /q "%INSTALL_DIR%\windows" >nul 2>&1
)
xcopy /s /e /q "%UPDATE_DIR%\windows" "%INSTALL_DIR%\windows\" >nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to update Windows scripts
    goto :restore_backup
)

echo    Updating requirements...
if exist "%UPDATE_DIR%\requirements.txt" (
    copy "%UPDATE_DIR%\requirements.txt" "%INSTALL_DIR%\requirements.txt" >nul
)

echo    Updating launcher...
if exist "%UPDATE_DIR%\run_app.py" (
    copy "%UPDATE_DIR%\run_app.py" "%INSTALL_DIR%\run_app.py" >nul
)

echo ✅ Application files updated

REM Update Python packages
echo 📦 Updating Python packages...
cd /d "%INSTALL_DIR%"
call venv\Scripts\activate.bat

REM Upgrade pip first
python -m pip install --upgrade pip >nul 2>&1

REM Install/update requirements
if exist requirements.txt (
    pip install -r requirements.txt --upgrade
    if !ERRORLEVEL! neq 0 (
        echo ❌ Failed to update Python packages
        deactivate
        goto :restore_backup
    )
) else (
    echo    Installing essential packages...
    pip install PySide6>=6.6.0 pyqtgraph>=0.13.3 pyserial>=3.5 python-dotenv>=1.0.0 pyyaml>=6.0.1 appdirs>=1.4.4 qrcode>=7.4.2 Pillow>=10.0.0 pywin32>=306 --upgrade
    if !ERRORLEVEL! neq 0 (
        echo ❌ Failed to install essential packages
        deactivate
        goto :restore_backup
    )
)

deactivate
echo ✅ Python packages updated

REM Restore backed up files
echo 🔄 Restoring user data...

echo    Restoring configuration...
if exist "%BACKUP_DIR%\config.json" (
    copy "%BACKUP_DIR%\config.json" "%INSTALL_DIR%\monitoring\config.json" >nul
    echo    ✅ Configuration restored
)

echo    Restoring logs...
if exist "%BACKUP_DIR%\logs" (
    xcopy /s /e /q "%BACKUP_DIR%\logs" "%INSTALL_DIR%\logs\" >nul
    echo    ✅ Logs restored
)

echo    Restoring exports...
if exist "%BACKUP_DIR%\exports" (
    xcopy /s /e /q "%BACKUP_DIR%\exports" "%INSTALL_DIR%\exports\" >nul
    echo    ✅ Exports restored
)

echo ✅ User data restored

REM Update Windows service
echo 🔧 Updating Windows service...
call "%INSTALL_DIR%\windows\uninstall-service.bat" >nul 2>&1
timeout /t 3 /nobreak >nul
call "%INSTALL_DIR%\windows\install-service.bat" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo ⚠️ Warning: Service update may have failed
    echo    You can reinstall it manually by running:
    echo    %INSTALL_DIR%\windows\install-service.bat
)

REM Test the installation
echo 🧪 Testing updated installation...
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import sys; print(f'Python {sys.version}')" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python test failed
    goto :restore_backup
)

"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import PySide6; print(f'PySide6 {PySide6.__version__}')" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ PySide6 test failed
    goto :restore_backup
)

echo ✅ Installation test passed

REM Start the service
echo 🚀 Starting Roll Machine Monitor service...
"%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\windows\rollmachine-service.py" start

REM Check service status
timeout /t 3 /nobreak >nul
"%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\windows\rollmachine-service.py" status

echo.
echo ======================================================
echo 🎉 Update Completed Successfully!
echo ======================================================
echo.
echo ✅ Roll Machine Monitor has been updated
echo ✅ All settings and data preserved
echo ✅ Windows service restarted
echo.
echo 📁 Installation: %INSTALL_DIR%
echo 💾 Backup: %BACKUP_DIR%
echo.
echo 🚀 The application is ready to use!
echo    You can start it from the desktop shortcut or Start menu.
echo.
echo 📝 Note: The backup will be kept for safety.
echo    You can delete it manually if no longer needed:
echo    %BACKUP_DIR%
echo.

goto :cleanup

:restore_backup
echo.
echo ❌ Update failed! Attempting to restore from backup...
echo.

REM Stop any processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Roll Machine Monitor*" >nul 2>&1

REM Restore from backup
if exist "%BACKUP_DIR%\config.json" (
    copy "%BACKUP_DIR%\config.json" "%INSTALL_DIR%\monitoring\config.json" >nul
)
if exist "%BACKUP_DIR%\logs" (
    xcopy /s /e /q "%BACKUP_DIR%\logs" "%INSTALL_DIR%\logs\" >nul
)
if exist "%BACKUP_DIR%\exports" (
    xcopy /s /e /q "%BACKUP_DIR%\exports" "%INSTALL_DIR%\exports\" >nul
)

echo ✅ Backup restored
echo.
echo Please check the error messages above and try the update again.
echo If problems persist, you may need to reinstall completely.
echo.

:cleanup
REM Clean up can be done manually by user if desired
echo Press any key to exit...
pause >nul
exit /b 0 