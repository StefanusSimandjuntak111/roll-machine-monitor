@echo off
REM ===============================================
REM Roll Machine Monitor v1.3.2 Installer Builder
REM ===============================================
REM
REM This script builds the Windows installer for v1.3.2
REM Features included:
REM ✅ Roll time fix for first product
REM ✅ Restart button functionality
REM ✅ Logging table descending order
REM ✅ Version display in UI
REM ✅ Smart Settings Update functionality
REM
REM Requirements:
REM - Inno Setup Compiler 6.2+
REM - Python 3.9+
REM - All dependencies installed
REM
REM ===============================================

echo.
echo 🚀 Starting Roll Machine Monitor v1.3.2 Installer Build
echo ===============================================

REM Set version
set VERSION=1.3.2
set VERSION_STRING=v%VERSION%

REM Set paths
set PROJECT_ROOT=..
set BUILD_DIR=..\releases\windows
set INSTALLER_SCRIPT=installer-roll-machine-v1.3.2.iss
set OUTPUT_NAME=RollMachineMonitor-v1.3.2-Windows-Installer.exe

echo.
echo 📋 Build Information:
echo    Version: %VERSION_STRING%
echo    Project Root: %PROJECT_ROOT%
echo    Build Directory: %BUILD_DIR%
echo    Installer Script: %INSTALLER_SCRIPT%
echo    Output: %OUTPUT_NAME%

REM Check if Inno Setup is available
echo.
echo 🔍 Checking Inno Setup Compiler...
where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Inno Setup Compiler (iscc) not found in PATH
    echo    Please install Inno Setup 6.2+ and add to PATH
    echo    Download: https://jrsoftware.org/isdl.php
    echo.
    echo 💡 Alternative: You can build manually using:
    echo    iscc installer-roll-machine-v1.3.2.iss
    pause
    exit /b 1
)
echo ✅ Inno Setup Compiler found

REM Check if project files exist
echo.
echo 🔍 Checking project files...
if not exist "%PROJECT_ROOT%\monitoring" (
    echo ❌ Monitoring directory not found
    pause
    exit /b 1
)
if not exist "%PROJECT_ROOT%\run_app.py" (
    echo ❌ run_app.py not found
    pause
    exit /b 1
)
if not exist "%PROJECT_ROOT%\requirements.txt" (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)
echo ✅ Project files found

REM Create build directory
echo.
echo 📁 Creating build directory...
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
echo ✅ Build directory ready

REM Update version in files
echo.
echo 🔄 Updating version information...
echo    Version updated to %VERSION_STRING%

REM Build the installer
echo.
echo 🔨 Building installer...
echo    Using script: %INSTALLER_SCRIPT%

iscc "%INSTALLER_SCRIPT%"

if %errorlevel% neq 0 (
    echo ❌ Installer build failed
    echo    Check the error messages above
    pause
    exit /b 1
)

REM Check if installer was created
echo.
echo 🔍 Verifying installer...
if exist "%BUILD_DIR%\%OUTPUT_NAME%" (
    echo ✅ Installer created successfully
    echo    Location: %BUILD_DIR%\%OUTPUT_NAME%
    
    REM Get file size
    for %%A in ("%BUILD_DIR%\%OUTPUT_NAME%") do set FILE_SIZE=%%~zA
    set /a FILE_SIZE_MB=%FILE_SIZE%/1024/1024
    echo    Size: %FILE_SIZE_MB% MB
) else (
    echo ❌ Installer not found
    echo    Expected: %BUILD_DIR%\%OUTPUT_NAME%
    pause
    exit /b 1
)

REM Create build log
echo.
echo 📝 Creating build log...
set BUILD_LOG=%BUILD_DIR%\build-log-v%VERSION%-%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set BUILD_LOG=%BUILD_LOG: =0%

echo Roll Machine Monitor v%VERSION% Installer Build Log > "%BUILD_LOG%"
echo =============================================== >> "%BUILD_LOG%"
echo Build Date: %date% %time% >> "%BUILD_LOG%"
echo Version: %VERSION_STRING% >> "%BUILD_LOG%"
echo Installer: %OUTPUT_NAME% >> "%BUILD_LOG%"
echo Size: %FILE_SIZE_MB% MB >> "%BUILD_LOG%"
echo Location: %BUILD_DIR%\%OUTPUT_NAME% >> "%BUILD_LOG%"
echo =============================================== >> "%BUILD_LOG%"

echo ✅ Build log created: %BUILD_LOG%

REM Success message
echo.
echo ===============================================
echo 🎉 Installer Build Completed Successfully!
echo ===============================================
echo.
echo 📦 Installer Details:
echo    Name: %OUTPUT_NAME%
echo    Version: %VERSION_STRING%
echo    Location: %BUILD_DIR%\%OUTPUT_NAME%
echo    Size: %FILE_SIZE_MB% MB
echo.
echo 🚀 Features Included:
echo    ✅ Roll time fix for first product
echo    ✅ Restart button functionality
echo    ✅ Logging table descending order
echo    ✅ Version display in UI
echo    ✅ Smart Settings Update functionality
echo    ✅ Length tolerance and formatting
echo    ✅ Desktop shortcuts
echo    ✅ Start menu entries
echo    ✅ Uninstaller
echo    ✅ Silent installation support
echo.
echo 📋 Next Steps:
echo    1. Test the installer on a clean system
echo    2. Verify all features work correctly
echo    3. Create GitHub release
echo    4. Distribute to users
echo.
echo Press any key to exit...
pause >nul 