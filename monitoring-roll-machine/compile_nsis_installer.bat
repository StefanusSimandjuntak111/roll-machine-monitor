@echo off
echo ===============================================
echo COMPILING NSIS INSTALLER
echo Monitoring Roll Machine v1.3.5
echo ===============================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Check if NSIS is installed
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: NSIS (makensis) not found!
    echo Please install NSIS from: https://nsis.sourceforge.io/
    echo.
    echo After installation, make sure makensis is in your PATH
    pause
    exit /b 1
)

REM Check if executable exists
if not exist "releases\Monitoring-Roll-Machine-v1.3.5.exe" (
    echo ERROR: Executable not found!
    echo Please run build_complete_installer.bat first
    pause
    exit /b 1
)

REM Check if installer.nsi exists
if not exist "installer.nsi" (
    echo ERROR: installer.nsi not found!
    pause
    exit /b 1
)

echo Compiling NSIS installer...
echo Source: installer.nsi
echo Executable: releases\Monitoring-Roll-Machine-v1.3.5.exe
echo.

REM Compile NSIS installer
makensis installer.nsi
if %errorlevel% neq 0 (
    echo ERROR: NSIS compilation failed!
    pause
    exit /b 1
)

echo.
echo ===============================================
echo NSIS INSTALLER COMPILED SUCCESSFULLY!
echo ===============================================
echo.
echo Installer created: releases\Monitoring-Roll-Machine-Setup-1.3.5.exe
echo.

REM List files in releases directory
if exist "releases" (
    echo Files in releases directory:
    dir releases /b
)

echo.
pause

