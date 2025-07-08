@echo off
REM ===============================================
REM Roll Machine Monitor Windows Build Script v1.3.0
REM Builds complete Windows installer package
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ==========================================
echo 🏗️  Roll Machine Monitor Windows Builder
echo ==========================================
echo.

REM Set version and paths
set VERSION=1.3.0
set BUILD_DIR=%~dp0
set RELEASE_DIR=%BUILD_DIR%releases\windows
set OFFLINE_BUNDLE_DIR=%BUILD_DIR%RollMachineMonitor-v%VERSION%-Windows-Offline

REM Check for Inno Setup
where iscc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Inno Setup Compiler not found!
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Make sure 'iscc.exe' is in your PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Inno Setup Compiler found
echo.

REM Create release directory
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

REM Step 1: Create offline bundle first
echo 📦 Step 1: Creating offline Windows bundle...
echo.
python create-offline-windows-bundle.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to create offline bundle
    pause
    exit /b 1
)
echo ✅ Offline bundle created successfully
echo.

REM Step 2: Copy Python installer to main directory for Inno Setup
echo 🐍 Step 2: Preparing Python installer...
if exist "%OFFLINE_BUNDLE_DIR%\python-installer\python-3.11.7-amd64.exe" (
    if not exist "python-installer" mkdir "python-installer"
    copy "%OFFLINE_BUNDLE_DIR%\python-installer\python-3.11.7-amd64.exe" "python-installer\" >nul
    echo ✅ Python installer prepared
) else (
    echo ⚠️  Warning: Python installer not found, will skip automatic Python installation
)
echo.

REM Step 3: Create assets directory if it doesn't exist
echo 🎨 Step 3: Creating assets...
if not exist "assets" mkdir "assets"
echo # Application icon placeholder > "assets\rollmachine-icon.ico"
echo ✅ Assets created
echo.

REM Step 4: Create info files for installer
echo 📝 Step 4: Creating installer information files...

echo Welcome to Roll Machine Monitor v%VERSION%! > INSTALL_INFO_WINDOWS.txt
echo. >> INSTALL_INFO_WINDOWS.txt
echo This installer will set up: >> INSTALL_INFO_WINDOWS.txt
echo - Python environment and dependencies >> INSTALL_INFO_WINDOWS.txt
echo - Desktop shortcuts and Start menu entries >> INSTALL_INFO_WINDOWS.txt
echo - Windows service for auto-start >> INSTALL_INFO_WINDOWS.txt
echo - All required files and configuration >> INSTALL_INFO_WINDOWS.txt
echo. >> INSTALL_INFO_WINDOWS.txt
echo Installation typically takes 2-5 minutes. >> INSTALL_INFO_WINDOWS.txt

echo Installation completed successfully! > POST_INSTALL_INFO_WINDOWS.txt
echo. >> POST_INSTALL_INFO_WINDOWS.txt
echo You can now: >> POST_INSTALL_INFO_WINDOWS.txt
echo - Launch from Desktop shortcut or Start menu >> POST_INSTALL_INFO_WINDOWS.txt
echo - Use "Roll Machine Monitor (Kiosk)" for fullscreen mode >> POST_INSTALL_INFO_WINDOWS.txt
echo - Check logs folder for troubleshooting >> POST_INSTALL_INFO_WINDOWS.txt
echo - Configure settings via Start menu shortcuts >> POST_INSTALL_INFO_WINDOWS.txt
echo. >> POST_INSTALL_INFO_WINDOWS.txt
echo The Windows service is installed and will start automatically. >> POST_INSTALL_INFO_WINDOWS.txt

echo ✅ Installer info files created
echo.

REM Step 5: Build installer with Inno Setup
echo 🔨 Step 5: Building Windows installer...
echo.
iscc installer-windows.iss
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build installer
    pause
    exit /b 1
)

echo ✅ Windows installer built successfully!
echo.

REM Step 6: Create comprehensive release package
echo 📦 Step 6: Creating final release package...

set FINAL_RELEASE_DIR=%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Complete
if exist "%FINAL_RELEASE_DIR%" rmdir /s /q "%FINAL_RELEASE_DIR%"
mkdir "%FINAL_RELEASE_DIR%"

REM Copy installer executable
copy "%RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Installer.exe" "%FINAL_RELEASE_DIR%\" >nul

REM Copy offline bundle
if exist "%OFFLINE_BUNDLE_DIR%.zip" (
    copy "%OFFLINE_BUNDLE_DIR%.zip" "%FINAL_RELEASE_DIR%\" >nul
)

REM Create installation guide
echo # Roll Machine Monitor v%VERSION% - Windows Installation Guide > "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo ## Quick Installation >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo 1. Run `RollMachineMonitor-v%VERSION%-Windows-Installer.exe` as Administrator >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo 2. Follow the installation wizard >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo 3. Choose installation components (Full recommended) >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo 4. Launch from Desktop shortcut >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo ## Features >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Automatic Python installation >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ All dependencies included >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Windows service setup >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Desktop shortcuts >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Kiosk mode support >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Automatic updates >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo - ✅ Complete uninstaller >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo ## Offline Installation >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo. >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo For computers without internet, use: >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"
echo `RollMachineMonitor-v%VERSION%-Windows-Offline.zip` >> "%FINAL_RELEASE_DIR%\INSTALLATION_GUIDE.md"

REM Create version info
echo Version: %VERSION% > "%FINAL_RELEASE_DIR%\VERSION"
echo Build Date: %DATE% %TIME% >> "%FINAL_RELEASE_DIR%\VERSION"
echo Builder: Windows Build Script >> "%FINAL_RELEASE_DIR%\VERSION"

echo ✅ Final release package created
echo.

REM Step 7: Calculate checksums
echo 🔐 Step 7: Calculating checksums...
cd "%FINAL_RELEASE_DIR%"
certutil -hashfile "RollMachineMonitor-v%VERSION%-Windows-Installer.exe" SHA256 > "CHECKSUMS.txt"
if exist "RollMachineMonitor-v%VERSION%-Windows-Offline.zip" (
    certutil -hashfile "RollMachineMonitor-v%VERSION%-Windows-Offline.zip" SHA256 >> "CHECKSUMS.txt"
)
cd "%BUILD_DIR%"
echo ✅ Checksums calculated
echo.

REM Cleanup temporary files
echo 🧹 Cleaning up temporary files...
del INSTALL_INFO_WINDOWS.txt >nul 2>&1
del POST_INSTALL_INFO_WINDOWS.txt >nul 2>&1
if exist "python-installer" rmdir /s /q "python-installer"
echo ✅ Cleanup completed
echo.

REM Final summary
echo ==========================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo 📁 Release Location: %FINAL_RELEASE_DIR%
echo.
echo 📦 Files Created:
echo   - RollMachineMonitor-v%VERSION%-Windows-Installer.exe (Main installer)
if exist "%FINAL_RELEASE_DIR%\RollMachineMonitor-v%VERSION%-Windows-Offline.zip" (
    echo   - RollMachineMonitor-v%VERSION%-Windows-Offline.zip (Offline bundle)
)
echo   - INSTALLATION_GUIDE.md (Installation instructions)
echo   - VERSION (Version information)
echo   - CHECKSUMS.txt (File integrity verification)
echo.
echo 🚀 Ready for distribution!
echo.
pause 