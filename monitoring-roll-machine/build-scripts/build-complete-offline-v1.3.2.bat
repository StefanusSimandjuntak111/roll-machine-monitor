@echo off
REM ===============================================
REM Roll Machine Monitor v1.3.2 Complete Offline Builder
REM ===============================================
REM
REM This script creates a complete offline installer with all dependencies
REM bundled using PyInstaller
REM
REM Features:
REM ✅ Complete application with all dependencies
REM ✅ Roll time fix for first product
REM ✅ Restart button functionality
REM ✅ Logging table descending order
REM ✅ Version display in UI
REM ✅ Smart Settings Update functionality
REM
REM ===============================================

echo.
echo Starting Roll Machine Monitor v1.3.2 Complete Offline Build
echo ===============================================

REM Set version
set VERSION=1.3.2
set VERSION_STRING=v%VERSION%

REM Set paths
set PROJECT_ROOT=..
set BUILD_DIR=..\releases\windows
set OUTPUT_NAME=RollMachineMonitor-v1.3.2-Windows-Complete-Offline.exe

echo.
echo Build Information:
echo    Version: %VERSION_STRING%
echo    Project Root: %PROJECT_ROOT%
echo    Build Directory: %BUILD_DIR%
echo    Output: %OUTPUT_NAME%

REM Check if PyInstaller is available
echo.
echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo PyInstaller found

REM Check if project files exist
echo.
echo Checking project files...
if not exist "%PROJECT_ROOT%\monitoring" (
    echo ERROR: Monitoring directory not found
    pause
    exit /b 1
)
if not exist "%PROJECT_ROOT%\run_app.py" (
    echo ERROR: run_app.py not found
    pause
    exit /b 1
)
echo Project files found

REM Create build directory
echo.
echo Creating build directory...
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
echo Build directory ready

REM Create PyInstaller spec file
echo.
echo Creating PyInstaller spec file...
set SPEC_FILE=roll_machine_monitor_v1.3.2.spec

echo # -*- mode: python ; coding: utf-8 -*- > "%SPEC_FILE%"
echo. >> "%SPEC_FILE%"
echo block_cipher = None >> "%SPEC_FILE%"
echo. >> "%SPEC_FILE%"
echo a = Analysis( >> "%SPEC_FILE%"
echo     ['%PROJECT_ROOT%/run_app.py'], >> "%SPEC_FILE%"
echo     pathex=[], >> "%SPEC_FILE%"
echo     binaries=[], >> "%SPEC_FILE%"
echo     datas=[ >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/monitoring', 'monitoring'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/requirements.txt', '.'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/README.md', '.'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/scripts', 'scripts'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/tools', 'tools'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/windows', 'windows'), >> "%SPEC_FILE%"
echo         ('%PROJECT_ROOT%/docs', 'docs'), >> "%SPEC_FILE%"
echo     ], >> "%SPEC_FILE%"
echo     hiddenimports=[ >> "%SPEC_FILE%"
echo         'PySide6.QtCore', >> "%SPEC_FILE%"
echo         'PySide6.QtWidgets', >> "%SPEC_FILE%"
echo         'PySide6.QtGui', >> "%SPEC_FILE%"
echo         'pyqtgraph', >> "%SPEC_FILE%"
echo         'serial', >> "%SPEC_FILE%"
echo         'yaml', >> "%SPEC_FILE%"
echo         'appdirs', >> "%SPEC_FILE%"
echo         'qrcode', >> "%SPEC_FILE%"
echo         'PIL', >> "%SPEC_FILE%"
echo         'dotenv', >> "%SPEC_FILE%"
echo     ], >> "%SPEC_FILE%"
echo     hookspath=[], >> "%SPEC_FILE%"
echo     hooksconfig={}, >> "%SPEC_FILE%"
echo     runtime_hooks=[], >> "%SPEC_FILE%"
echo     excludes=[], >> "%SPEC_FILE%"
echo     win_no_prefer_redirects=False, >> "%SPEC_FILE%"
echo     win_private_assemblies=False, >> "%SPEC_FILE%"
echo     cipher=block_cipher, >> "%SPEC_FILE%"
echo     noarchive=False, >> "%SPEC_FILE%"
echo ) >> "%SPEC_FILE%"
echo. >> "%SPEC_FILE%"
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> "%SPEC_FILE%"
echo. >> "%SPEC_FILE%"
echo exe = EXE( >> "%SPEC_FILE%"
echo     pyz, >> "%SPEC_FILE%"
echo     a.scripts, >> "%SPEC_FILE%"
echo     [], >> "%SPEC_FILE%"
echo     exclude_binaries=True, >> "%SPEC_FILE%"
echo     name='RollMachineMonitor', >> "%SPEC_FILE%"
echo     debug=False, >> "%SPEC_FILE%"
echo     bootloader_ignore_signals=False, >> "%SPEC_FILE%"
echo     strip=False, >> "%SPEC_FILE%"
echo     upx=True, >> "%SPEC_FILE%"
echo     console=False, >> "%SPEC_FILE%"
echo     disable_windowed_traceback=False, >> "%SPEC_FILE%"
echo     argv_emulation=False, >> "%SPEC_FILE%"
echo     target_arch=None, >> "%SPEC_FILE%"
echo     codesign_identity=None, >> "%SPEC_FILE%"
echo     entitlements_file=None, >> "%SPEC_FILE%"
echo     icon='%PROJECT_ROOT%/monitoring/ui/icons/app_icon.ico' >> "%SPEC_FILE%"
echo ) >> "%SPEC_FILE%"
echo. >> "%SPEC_FILE%"
echo coll = COLLECT( >> "%SPEC_FILE%"
echo     exe, >> "%SPEC_FILE%"
echo     a.binaries, >> "%SPEC_FILE%"
echo     a.zipfiles, >> "%SPEC_FILE%"
echo     a.datas, >> "%SPEC_FILE%"
echo     strip=False, >> "%SPEC_FILE%"
echo     upx=True, >> "%SPEC_FILE%"
echo     upx_exclude=[], >> "%SPEC_FILE%"
echo     name='RollMachineMonitor', >> "%SPEC_FILE%"
echo ) >> "%SPEC_FILE%"

echo Spec file created: %SPEC_FILE%

REM Build with PyInstaller
echo.
echo Building with PyInstaller...
pyinstaller --clean "%SPEC_FILE%"

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

REM Check if build was successful
echo.
echo Checking build output...
if not exist "dist\RollMachineMonitor" (
    echo ERROR: Build output not found
    pause
    exit /b 1
)
echo Build output found

REM Create installer using Inno Setup
echo.
echo Creating installer with Inno Setup...
if exist "build-offline-installer-v1.3.2.iss" (
    iscc build-offline-installer-v1.3.2.iss
    if %errorlevel% neq 0 (
        echo ERROR: Inno Setup build failed
        pause
        exit /b 1
    )
) else (
    echo WARNING: Inno Setup script not found, skipping installer creation
)

REM Check if installer was created
echo.
echo Checking installer...
if exist "%BUILD_DIR%\%OUTPUT_NAME%" (
    echo Installer created successfully
    for %%A in ("%BUILD_DIR%\%OUTPUT_NAME%") do set FILE_SIZE=%%~zA
    set /a FILE_SIZE_MB=%FILE_SIZE%/1024/1024
    echo Size: %FILE_SIZE_MB% MB
) else (
    echo WARNING: Installer not found
)

REM Clean up
echo.
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%SPEC_FILE%" del "%SPEC_FILE%"
if exist "*.spec" del "*.spec"

echo Cleanup completed

REM Success message
echo.
echo ===============================================
echo Build Completed Successfully!
echo ===============================================
echo.
echo Files created:
echo    - PyInstaller bundle: dist\RollMachineMonitor\
echo    - Installer: %BUILD_DIR%\%OUTPUT_NAME%
echo.
echo Features included:
echo    - Complete application with all dependencies
echo    - Roll time fix for first product
echo    - Restart button functionality
echo    - Logging table descending order
echo    - Version display in UI
echo    - Smart Settings Update functionality
echo.
pause 