@echo off
REM ===============================================
REM Build Complete Release v1.3.0 for antiX
REM Windows Builder Script
REM ===============================================

setlocal EnableDelayedExpansion

set VERSION=v1.3.0
set PACKAGE_NAME=rollmachine-monitor-%VERSION%-complete-antix
set BUILD_DIR=releases\%PACKAGE_NAME%

echo.
echo =======================================================
echo 🚀 Building Complete Release %VERSION% for antiX
echo =======================================================
echo.

REM Clean previous build
if exist "%BUILD_DIR%" (
    echo ✅ Cleaning previous build...
    rmdir /s /q "%BUILD_DIR%"
)

REM Create build directories
echo ✅ Creating build directories...
mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\monitoring-roll-machine"
mkdir "%BUILD_DIR%\logs"
mkdir "%BUILD_DIR%\exports"

REM Copy core application files
echo ✅ Copying core application files...
xcopy /s /e /q monitoring "%BUILD_DIR%\monitoring-roll-machine\monitoring\"
if exist requirements.txt copy requirements.txt "%BUILD_DIR%\monitoring-roll-machine\"
if exist run_app.py copy run_app.py "%BUILD_DIR%\monitoring-roll-machine\"
if exist README.md copy README.md "%BUILD_DIR%\"

REM Copy installer scripts
echo ✅ Copying installer scripts...
copy install-complete-antix.sh "%BUILD_DIR%\"
copy install-offline-bundle.sh "%BUILD_DIR%\"

REM Create release notes
echo ✅ Creating release notes...
echo # Roll Machine Monitor %VERSION% Release Notes > "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo. >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ## 🎉 Complete All-in-One Installer for antiX Linux >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo. >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo This release provides a complete automated installer that: >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo. >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Installs all system dependencies >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Creates Python virtual environment >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Installs all Python requirements >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Sets up desktop shortcuts >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Creates SysV init scripts (no systemd) >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Sets up kiosk user and auto-start >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Configures watchdog monitoring >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Supports offline installation >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo - ✅ Includes update mechanism >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo. >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ### Installation >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ```bash >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo sudo ./install-complete-antix.sh >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ``` >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo. >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ### Update Existing Installation >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ```bash >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo sudo ./install-complete-antix.sh --update >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"
echo ``` >> "%BUILD_DIR%\RELEASE_NOTES_%VERSION%.md"

REM Create version file
echo ✅ Creating version file...
echo %VERSION% > "%BUILD_DIR%\VERSION"
echo BUILT: %DATE% %TIME% >> "%BUILD_DIR%\VERSION"
echo TARGET: antiX Linux (SysV init) >> "%BUILD_DIR%\VERSION"
echo TYPE: Complete All-in-One Release >> "%BUILD_DIR%\VERSION"

REM Create installation guide
echo ✅ Creating installation guide...
echo # Installation Guide - Roll Machine Monitor %VERSION% > "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo ## Quick Start >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo 1. Extract the package: >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ```bash >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    tar -xzf %PACKAGE_NAME%.tar.gz >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    cd %PACKAGE_NAME% >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ``` >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo 2. Install everything automatically: >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ```bash >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    sudo ./install-complete-antix.sh >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ``` >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo 3. For updates (preserves settings): >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ```bash >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    sudo ./install-complete-antix.sh --update >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo    ``` >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo ## Features >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo. >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Desktop shortcuts for regular and kiosk modes >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Automatic service setup with SysV init scripts >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Kiosk user (username: kiosk, password: kiosk123) >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Watchdog process monitoring >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Complete offline installation support >> "%BUILD_DIR%\INSTALL_GUIDE.md"
echo - Logs in /opt/rollmachine-monitor/logs/ >> "%BUILD_DIR%\INSTALL_GUIDE.md"

REM Create deployment script for Linux environments
echo ✅ Creating deployment helper...
echo #!/bin/bash > "%BUILD_DIR%\deploy-to-antix.sh"
echo # Deployment helper for antiX systems >> "%BUILD_DIR%\deploy-to-antix.sh"
echo echo "🚀 Deploying Roll Machine Monitor to antiX..." >> "%BUILD_DIR%\deploy-to-antix.sh"
echo echo "1. Extracting package..." >> "%BUILD_DIR%\deploy-to-antix.sh"
echo tar -xzf %PACKAGE_NAME%.tar.gz >> "%BUILD_DIR%\deploy-to-antix.sh"
echo cd %PACKAGE_NAME% >> "%BUILD_DIR%\deploy-to-antix.sh"
echo echo "2. Starting installation..." >> "%BUILD_DIR%\deploy-to-antix.sh"
echo sudo ./install-complete-antix.sh >> "%BUILD_DIR%\deploy-to-antix.sh"

echo.
echo =======================================================
echo 🎉 Build Completed Successfully! 🎉
echo =======================================================
echo.
echo 📦 Package Directory: %BUILD_DIR%
echo 📁 Contents:
echo    ✅ Complete application source code
echo    ✅ All-in-one installer script
echo    ✅ Offline bundle creator
echo    ✅ Desktop integration files
echo    ✅ SysV init scripts
echo    ✅ Documentation and guides
echo.
echo 🚀 Next Steps:
echo 1. Copy the %BUILD_DIR% folder to your antiX system
echo 2. Run: sudo ./install-complete-antix.sh
echo 3. Or create offline bundle: ./install-offline-bundle.sh
echo.
echo 📋 Installation Methods:
echo    Online:  sudo ./install-complete-antix.sh
echo    Update:  sudo ./install-complete-antix.sh --update
echo    Offline: ./install-offline-bundle.sh (then transfer)
echo.
echo ✅ Ready for deployment to antiX systems!

pause 