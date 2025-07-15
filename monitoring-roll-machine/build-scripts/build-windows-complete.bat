@echo off
REM ===============================================
REM Roll Machine Monitor Windows Build Script v1.3.0
REM Complete All-in-One Windows Installer Builder
REM ===============================================

setlocal EnableDelayedExpansion

REM Setup logging
set LOG_FILE=%~dp0build-log-%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set LOG_FILE=%LOG_FILE: =0%

REM Create log file and redirect output
echo Roll Machine Monitor Windows Build Log > "%LOG_FILE%"
echo Build started: %date% %time% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Function to log messages
:log
echo [%time%] %~1
echo [%time%] %~1 >> "%LOG_FILE%"
goto :eof

REM Function to log errors
:log_error
echo [%time%] ERROR: %~1
echo [%time%] ERROR: %~1 >> "%LOG_FILE%"
goto :eof

echo.
echo ==========================================
echo 🏗️  Roll Machine Monitor Windows Builder v1.3.0
echo ==========================================
echo.
echo 📝 Log file: %LOG_FILE%
echo.

call :log "Build script started"
call :log "Log file: %LOG_FILE%"

REM Set version and paths
set VERSION=1.3.0
set BUILD_DIR=%~dp0
set RELEASE_DIR=%BUILD_DIR%releases\windows
set OFFLINE_BUNDLE_DIR=%BUILD_DIR%RollMachineMonitor-v%VERSION%-Windows-Offline

call :log "Version: %VERSION%"
call :log "Build directory: %BUILD_DIR%"
call :log "Release directory: %RELEASE_DIR%"

REM Change to script directory
echo 🔧 Changing to script directory...
call :log "Changing to script directory"
cd /d "%BUILD_DIR%"
echo ✅ Current directory: %CD%
call :log "Current directory: %CD%"
echo.

REM Validate we're in the correct directory
if not exist "create-offline-windows-bundle.py" (
    call :log_error "create-offline-windows-bundle.py not found!"
    echo.
    echo Expected location: %BUILD_DIR%create-offline-windows-bundle.py
    echo Current directory: %CD%
    echo.
    echo Please run this script from the monitoring-roll-machine directory
    echo.
    call :log "Build failed - missing required files"
    goto :build_failed
)

call :log "Python script found: create-offline-windows-bundle.py"
echo ✅ Python script found: create-offline-windows-bundle.py
echo.

REM Check for Python
echo 🐍 Checking Python installation...
call :log "Checking Python installation"
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_error "Python not found!"
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.9+ and add to PATH
    echo Download from: https://www.python.org/downloads/
    echo.
    call :log "Build failed - Python not found"
    goto :build_failed
)

echo ✅ Python found:
python --version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do call :log "Python version: %%i"
echo.

REM Check for Inno Setup
echo 🔨 Checking Inno Setup...
call :log "Checking Inno Setup"
where iscc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_error "Inno Setup Compiler not found!"
    echo ❌ ERROR: Inno Setup Compiler not found!
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Make sure 'iscc.exe' is in your PATH
    echo.
    call :log "Build failed - Inno Setup not found"
    goto :build_failed
)

echo ✅ Inno Setup Compiler found
iscc /version
for /f "tokens=*" %%i in ('iscc /version 2^>^&1') do call :log "Inno Setup version: %%i"
echo.

REM Check for required files
echo 📁 Checking required files...
call :log "Checking required files"
set MISSING_FILES=0

if not exist "installer-windows.iss" (
    call :log_error "Missing: installer-windows.iss"
    echo ❌ Missing: installer-windows.iss
    set /a "MISSING_FILES+=1"
) else (
    call :log "Found: installer-windows.iss"
    echo ✅ Found: installer-windows.iss
)

if not exist "windows\" (
    call :log_error "Missing: windows\ directory"
    echo ❌ Missing: windows\ directory
    set /a "MISSING_FILES+=1"
) else (
    call :log "Found: windows\ directory"
    echo ✅ Found: windows\ directory
)

if not exist "monitoring\" (
    call :log_error "Missing: monitoring\ directory"
    echo ❌ Missing: monitoring\ directory
    set /a "MISSING_FILES+=1"
) else (
    call :log "Found: monitoring\ directory"
    echo ✅ Found: monitoring\ directory
)

if not exist "requirements.txt" (
    call :log_error "Missing: requirements.txt"
    echo ❌ Missing: requirements.txt
    set /a "MISSING_FILES+=1"
) else (
    call :log "Found: requirements.txt"
    echo ✅ Found: requirements.txt
)

if not exist "run_app.py" (
    call :log_error "Missing: run_app.py"
    echo ❌ Missing: run_app.py
    set /a "MISSING_FILES+=1"
) else (
    call :log "Found: run_app.py"
    echo ✅ Found: run_app.py
)

if %MISSING_FILES% gtr 0 (
    call :log_error "%MISSING_FILES% required file(s) missing!"
    echo.
    echo ❌ ERROR: %MISSING_FILES% required file(s) missing!
    echo Please ensure all files are present before building
    call :log "Build failed - missing required files"
    goto :build_failed
)

call :log "All required files found"
echo ✅ All required files found
echo.

REM Create release directory
if not exist "%RELEASE_DIR%" (
    mkdir "%RELEASE_DIR%"
    call :log "Created release directory: %RELEASE_DIR%"
)

REM Step 1: Create offline bundle first
echo 📦 Step 1: Creating offline Windows bundle...
call :log "Step 1: Creating offline Windows bundle"
echo    Running: python create-offline-windows-bundle.py
echo    From directory: %CD%
echo.

python create-offline-windows-bundle.py
if %ERRORLEVEL% neq 0 (
    call :log_error "Offline bundle creation failed (Error: %ERRORLEVEL%)"
    echo ❌ FAILED: Offline bundle creation failed (Error: %ERRORLEVEL%)
    echo.
    echo Troubleshooting steps:
    echo 1. Check internet connection for downloading dependencies
    echo 2. Verify Python modules: urllib.request, zipfile, subprocess
    echo 3. Try running manually: python create-offline-windows-bundle.py
    echo 4. Check if antivirus is blocking downloads
    echo.
    call :log "Build failed - offline bundle creation failed"
    goto :build_failed
)
call :log "Offline bundle created successfully"
echo ✅ Offline bundle created successfully
echo.

REM Step 2: Copy Python installer to main directory for Inno Setup
echo 🐍 Step 2: Preparing Python installer...
call :log "Step 2: Preparing Python installer"
if exist "%OFFLINE_BUNDLE_DIR%\python-installer\python-3.11.7-amd64.exe" (
    if not exist "python-installer" mkdir "python-installer"
    copy "%OFFLINE_BUNDLE_DIR%\python-installer\python-3.11.7-amd64.exe" "python-installer\" >nul
    call :log "Python installer prepared"
    echo ✅ Python installer prepared
) else (
    call :log "WARNING: Python installer not found"
    echo ⚠️  WARNING: Python installer not found
    echo    Expected: %OFFLINE_BUNDLE_DIR%\python-installer\python-3.11.7-amd64.exe
    echo    Will skip automatic Python installation
)
echo.

REM Step 3: Create assets directory and icon
echo 🎨 Step 3: Creating assets...
call :log "Step 3: Creating assets"
if not exist "assets" mkdir "assets"

REM Create a simple icon placeholder (you can replace this with a real icon)
echo Creating icon placeholder...
echo # This is a placeholder icon file > "assets\rollmachine-icon.ico"
echo # Replace with actual .ico file for production > "assets\rollmachine-icon.ico"
call :log "Assets created"
echo ✅ Assets created
echo.

REM Step 4: Create info files for installer
echo 📝 Step 4: Creating installer information files...
call :log "Step 4: Creating installer information files"

echo Welcome to Roll Machine Monitor v%VERSION%! > INSTALL_INFO_WINDOWS.txt
echo. >> INSTALL_INFO_WINDOWS.txt
echo This installer will set up: >> INSTALL_INFO_WINDOWS.txt
echo - Python environment and dependencies >> INSTALL_INFO_WINDOWS.txt
echo - Desktop shortcuts and Start menu entries >> INSTALL_INFO_WINDOWS.txt
echo - Windows service for auto-start >> INSTALL_INFO_WINDOWS.txt
echo - All required files and configuration >> INSTALL_INFO_WINDOWS.txt
echo - Offline installation support >> INSTALL_INFO_WINDOWS.txt
echo. >> INSTALL_INFO_WINDOWS.txt
echo Installation typically takes 2-5 minutes. >> INSTALL_INFO_WINDOWS.txt
echo. >> INSTALL_INFO_WINDOWS.txt
echo System Requirements: >> INSTALL_INFO_WINDOWS.txt
echo - Windows 10 x64 or Windows 11 >> INSTALL_INFO_WINDOWS.txt
echo - 4 GB RAM (2 GB minimum) >> INSTALL_INFO_WINDOWS.txt
echo - 1 GB free disk space >> INSTALL_INFO_WINDOWS.txt
echo - USB or built-in COM ports >> INSTALL_INFO_WINDOWS.txt

echo Installation completed successfully! > POST_INSTALL_INFO_WINDOWS.txt
echo. >> POST_INSTALL_INFO_WINDOWS.txt
echo You can now: >> POST_INSTALL_INFO_WINDOWS.txt
echo - Launch from Desktop shortcut or Start menu >> POST_INSTALL_INFO_WINDOWS.txt
echo - Use "Roll Machine Monitor (Kiosk)" for fullscreen mode >> POST_INSTALL_INFO_WINDOWS.txt
echo - Check logs folder for troubleshooting >> POST_INSTALL_INFO_WINDOWS.txt
echo - Configure settings via Start menu shortcuts >> POST_INSTALL_INFO_WINDOWS.txt
echo - Update the application via Start menu shortcut >> POST_INSTALL_INFO_WINDOWS.txt
echo. >> POST_INSTALL_INFO_WINDOWS.txt
echo The Windows service is installed and will start automatically. >> POST_INSTALL_INFO_WINDOWS.txt
echo. >> POST_INSTALL_INFO_WINDOWS.txt
echo For support, visit: >> POST_INSTALL_INFO_WINDOWS.txt
echo https://github.com/StefanusSimandjuntak111/roll-machine-monitor >> POST_INSTALL_INFO_WINDOWS.txt

call :log "Installer info files created"
echo ✅ Installer info files created
echo.

REM Step 5: Build installer with Inno Setup
echo 🔨 Step 5: Building Windows installer...
call :log "Step 5: Building Windows installer with Inno Setup"
echo    Running: iscc installer-windows.iss
echo    From directory: %CD%
echo.

iscc installer-windows.iss
if %ERRORLEVEL% neq 0 (
    call :log_error "Inno Setup compilation failed (Error: %ERRORLEVEL%)"
    echo ❌ FAILED: Inno Setup compilation failed (Error: %ERRORLEVEL%)
    echo.
    echo Troubleshooting steps:
    echo 1. Check Inno Setup installation
    echo 2. Verify installer-windows.iss syntax
    echo 3. Check if all source files exist
    echo 4. Ensure sufficient disk space
    echo.
    call :log "Build failed - Inno Setup compilation failed"
    goto :build_failed
)

call :log "Windows installer built successfully"
echo ✅ Windows installer built successfully
echo.

REM Step 6: Create offline installer package
echo 📦 Step 6: Creating offline installer package...
call :log "Step 6: Creating offline installer package"
if exist "%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Installer.exe" (
    call :log "Installer found, creating offline package"
    echo Creating offline package...
    
    REM Create offline package directory
    set OFFLINE_PACKAGE_DIR=%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Complete
    if exist "%OFFLINE_PACKAGE_DIR%" rmdir /s /q "%OFFLINE_PACKAGE_DIR%"
    mkdir "%OFFLINE_PACKAGE_DIR%"
    call :log "Created offline package directory: %OFFLINE_PACKAGE_DIR%"
    
    REM Copy installer
    copy "%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Installer.exe" "%OFFLINE_PACKAGE_DIR%\"
    call :log "Copied installer to offline package"
    
    REM Copy offline bundle
    if exist "%OFFLINE_BUNDLE_DIR%" (
        xcopy "%OFFLINE_BUNDLE_DIR%" "%OFFLINE_PACKAGE_DIR%\offline-bundle\" /E /I /Y >nul
        call :log "Copied offline bundle to package"
    )
    
    REM Create installation guide
    echo Roll Machine Monitor v%VERSION% - Windows Installation Guide > "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo ================================================================ >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo. >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo ## Installation Options >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo. >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo ### Online Installation (Recommended) >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo Run: RollMachineMonitor-v%VERSION%-Windows-Installer.exe >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo - Requires internet connection >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo - Downloads Python if needed >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo - Smaller download size >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo. >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo ### Offline Installation >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo Use the offline-bundle folder for complete offline installation >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo - No internet required >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUGIDE.md"
    echo - Includes all dependencies >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    echo - Larger package size >> "%OFFLINE_PACKAGE_DIR%\INSTALLATION_GUIDE.md"
    
    REM Create version file
    echo %VERSION% > "%OFFLINE_PACKAGE_DIR%\VERSION"
    
    REM Create checksums
    echo Creating checksums...
    call :log "Creating checksums"
    cd /d "%OFFLINE_PACKAGE_DIR%"
    for %%f in (*.exe) do (
        certutil -hashfile "%%f" SHA256 > "%%f.sha256" 2>nul
        call :log "Created checksum for %%f"
    )
    cd /d "%BUILD_DIR%"
    
    call :log "Offline package created successfully"
    echo ✅ Offline package created: %OFFLINE_PACKAGE_DIR%
) else (
    call :log_error "Installer not found!"
    echo ❌ ERROR: Installer not found!
    call :log "Build failed - installer not found"
    goto :build_failed
)

echo.

REM Step 7: Create final release package
echo 📦 Step 7: Creating final release package...
call :log "Step 7: Creating final release package"
set FINAL_RELEASE_DIR=%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Complete

REM Create README for the release
echo # Roll Machine Monitor v%VERSION% - Windows Complete Package > "%FINAL_RELEASE_DIR%\README.md"
echo. >> "%FINAL_RELEASE_DIR%\README.md"
echo This package contains everything needed to install Roll Machine Monitor on Windows. >> "%FINAL_RELEASE_DIR%\README.md"
echo. >> "%FINAL_RELEASE_DIR%\README.md"
echo ## Contents >> "%FINAL_RELEASE_DIR%\README.md"
echo - RollMachineMonitor-v%VERSION%-Windows-Installer.exe (Online installer) >> "%FINAL_RELEASE_DIR%\README.md"
echo - offline-bundle/ (Complete offline package) >> "%FINAL_RELEASE_DIR%\README.md"
echo - INSTALLATION_GUIDE.md (Installation instructions) >> "%FINAL_RELEASE_DIR%\README.md"
echo - VERSION (Version information) >> "%FINAL_RELEASE_DIR%\README.md"
echo. >> "%FINAL_RELEASE_DIR%\README.md"
echo ## Quick Start >> "%FINAL_RELEASE_DIR%\README.md"
echo 1. Run RollMachineMonitor-v%VERSION%-Windows-Installer.exe as Administrator >> "%FINAL_RELEASE_DIR%\README.md"
echo 2. Follow the installation wizard >> "%FINAL_RELEASE_DIR%\README.md"
echo 3. Launch from Desktop shortcut or Start menu >> "%FINAL_RELEASE_DIR%\README.md"
echo. >> "%FINAL_RELEASE_DIR%\README.md"
echo ## System Requirements >> "%FINAL_RELEASE_DIR%\README.md"
echo - Windows 10 x64 or Windows 11 >> "%FINAL_RELEASE_DIR%\README.md"
echo - 4 GB RAM (2 GB minimum) >> "%FINAL_RELEASE_DIR%\README.md"
echo - 1 GB free disk space >> "%FINAL_RELEASE_DIR%\README.md"
echo - USB or built-in COM ports >> "%FINAL_RELEASE_DIR%\README.md"
echo. >> "%FINAL_RELEASE_DIR%\README.md"
echo ## Support >> "%FINAL_RELEASE_DIR%\README.md"
echo For support, visit: https://github.com/StefanusSimandjuntak111/roll-machine-monitor >> "%FINAL_RELEASE_DIR%\README.md"

REM Create release notes
echo # Roll Machine Monitor v%VERSION% - Release Notes > "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo. >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo ## What's New >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Complete Windows installer with Inno Setup >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Automatic Python 3.11 installation >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Windows service integration >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Desktop and Start menu shortcuts >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Kiosk mode support >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Offline installation support >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Silent installation support >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo - Automatic updates support >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo. >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo ## Installation >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo Run the installer as Administrator for best results. >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo. >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo ## Known Issues >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"
echo None at this time. >> "%FINAL_RELEASE_DIR%\RELEASE_NOTES.md"

call :log "Final release package created"
echo ✅ Final release package created
echo.

REM Step 8: Cleanup temporary files
echo 🧹 Step 8: Cleaning up temporary files...
call :log "Step 8: Cleaning up temporary files"
if exist "python-installer" rmdir /s /q "python-installer"
if exist "INSTALL_INFO_WINDOWS.txt" del "INSTALL_INFO_WINDOWS.txt"
if exist "POST_INSTALL_INFO_WINDOWS.txt" del "POST_INSTALL_INFO_WINDOWS.txt"
call :log "Cleanup completed"
echo ✅ Cleanup completed
echo.

REM Step 9: Display results
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo 📁 Output files:
echo    %RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Installer.exe
echo    %FINAL_RELEASE_DIR%\
echo.
echo 📦 Package contents:
echo    - Online installer (requires internet)
echo    - Offline bundle (complete package)
echo    - Installation guide
echo    - Release notes
echo    - Version information
echo.
echo 📝 Log file: %LOG_FILE%
echo.
echo 🚀 Ready for distribution!
echo.
echo 💡 Tips:
echo    - Test the installer on a clean Windows VM
echo    - Verify all shortcuts and services work
echo    - Check that Python environment is properly set up
echo    - Test both regular and kiosk modes
echo.

call :log "Build completed successfully"
call :log "Output files:"
call :log "  - %RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Installer.exe"
call :log "  - %FINAL_RELEASE_DIR%\"
call :log "Build end time: %date% %time%"

goto :build_success

:build_failed
echo.
echo ==========================================
echo ❌ BUILD FAILED!
echo ==========================================
echo.
echo 📝 Check the log file for details: %LOG_FILE%
echo.
echo 🔧 Troubleshooting:
echo    1. Check if all required files are present
echo    2. Verify Python and Inno Setup are installed
echo    3. Ensure you have internet connection for dependencies
echo    4. Check if antivirus is blocking the build process
echo.
call :log "Build failed - see log file for details"
call :log "Build end time: %date% %time%"
goto :end

:build_success
echo.
echo ==========================================
echo ✅ BUILD SUCCESSFUL!
echo ==========================================
echo.
echo 📝 Log file: %LOG_FILE%
echo 📁 Output directory: %FINAL_RELEASE_DIR%
echo.
call :log "Build successful - see log file for details"

:end
echo.
echo Press any key to exit...
pause >nul