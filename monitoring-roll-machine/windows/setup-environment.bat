@echo off
REM ===============================================
REM Roll Machine Monitor Environment Setup v1.3.0
REM ===============================================

REM Check if running as administrator
REM net session >nul 2>&1
REM if %errorLevel% neq 0 (
REM     echo This script requires administrator privileges.
REM     echo Please run the installer as Administrator.
REM     echo.
REM     pause
REM     exit /b 1
REM )

setlocal EnableDelayedExpansion

REM Set application directory
set APP_DIR=%~dp0..
cd /d "%APP_DIR%"

echo ==========================================
echo Setting up Python environment...
echo ==========================================
echo.

REM Wait a moment for Python installation to complete and PATH to update
timeout /t 3 /nobreak >nul

REM Refresh environment variables
call :RefreshPath

REM Check if Python is available (try multiple methods)
set PYTHON_FOUND=0

REM Try python command
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_FOUND=1
    set PYTHON_CMD=python
    goto :python_found
)

REM Try py launcher
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_FOUND=1
    set PYTHON_CMD=py
    goto :python_found
)

REM Try common Python installation paths
for %%p in (
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files (x86)\Python311\python.exe"
    "C:\Program Files (x86)\Python310\python.exe"
    "C:\Program Files (x86)\Python39\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
) do (
    if exist %%p (
        set PYTHON_FOUND=1
        set PYTHON_CMD=%%p
        goto :python_found
    )
)

REM If Python not found, show error
if %PYTHON_FOUND% equ 0 (
    echo ERROR: Python not found!
    echo.
    echo Please ensure Python 3.9+ is installed and available in PATH.
    echo You can download Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:python_found
echo ✅ Python found:
%PYTHON_CMD% --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q "venv" 2>nul
    if exist "venv" (
        echo WARNING: Could not remove old venv directory. Trying to continue...
    )
)

%PYTHON_CMD% -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment!
    echo This might be due to permission issues.
    echo Please ensure you're running as Administrator.
    pause
    exit /b 1
)

echo ✅ Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Failed to activate virtual environment!
    echo Please check the installation.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo ✅ Pip upgraded
echo.

REM Install requirements
echo Installing Python requirements...
if exist "requirements.txt" (
    venv\Scripts\pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install requirements!
        echo This might be due to permission issues or network problems.
        echo Please check requirements.txt and try again.
        pause
        exit /b 1
    )
    echo ✅ Requirements installed
) else (
    echo WARNING: requirements.txt not found, skipping requirements installation
)

echo.
echo ==========================================
echo Environment setup completed successfully!
echo ==========================================
echo.

goto :end

:RefreshPath
REM Refresh PATH from registry
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%b;%PATH%"
goto :eof

:end
endlocal
