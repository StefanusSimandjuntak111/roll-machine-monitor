@echo off
echo Compiling Roll Machine Monitor Installer...

REM Set path to Inno Setup Compiler
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

REM Check if compiler exists
if not exist %ISCC% (
    echo Error: Inno Setup Compiler not found at %ISCC%
    echo Please install Inno Setup 6 from https://jrsoftware.org/isdl.php
    goto :end
)

echo Found Inno Setup Compiler: %ISCC%
echo.

REM Create necessary directories
if not exist "..\releases\windows" mkdir "..\releases\windows"

REM Compile the installer
echo Compiling installer...
%ISCC% installer-windows.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Compilation successful!
    echo Installer created at: ..\releases\windows\RollMachineMonitor-v1.3.0-Windows-Installer.exe
) else (
    echo.
    echo Error: Compilation failed with error code %ERRORLEVEL%
)

:end
pause 