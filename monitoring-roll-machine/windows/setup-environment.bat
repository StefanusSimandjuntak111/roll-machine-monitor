@echo off
REM ===============================================
REM Roll Machine Monitor Environment Setup
REM Windows Virtual Environment and Requirements
REM ===============================================

setlocal EnableDelayedExpansion

echo.
echo ======================================================
echo 🐍 Setting up Python Environment for Roll Machine Monitor
echo ======================================================
echo.

REM Get the installation directory (parent of windows folder)
set "APP_DIR=%~dp0.."
set "VENV_DIR=%APP_DIR%\venv"
set "PYTHON_CMD=python"

REM Try to find Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 🔍 Python not found in PATH, trying py launcher...
    py --version >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo ❌ Python not found! Please install Python 3.8+ first.
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
)

echo ✅ Python found: %PYTHON_CMD%

REM Remove old virtual environment if it exists
if exist "%VENV_DIR%" (
    echo 🧹 Removing old virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

REM Create new virtual environment
echo 📦 Creating Python virtual environment...
%PYTHON_CMD% -m venv "%VENV_DIR%"
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to create virtual environment
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Warning: Failed to upgrade pip, continuing...
)

REM Install requirements
if exist "%APP_DIR%\requirements.txt" (
    echo 📥 Installing Python requirements...
    pip install -r "%APP_DIR%\requirements.txt"
    if !ERRORLEVEL! neq 0 (
        echo ❌ Failed to install requirements
        exit /b 1
    )
) else (
    echo 📥 Installing essential packages...
    pip install PySide6>=6.6.0 pyqtgraph>=0.13.3 pyserial>=3.5 python-dotenv>=1.0.0 pyyaml>=6.0.1 appdirs>=1.4.4 qrcode>=7.4.2 Pillow>=10.0.0 pywin32>=306
    if !ERRORLEVEL! neq 0 (
        echo ❌ Failed to install essential packages
        exit /b 1
    )
)

REM Create necessary directories
echo 📁 Creating application directories...
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\exports" mkdir "%APP_DIR%\exports"
if not exist "%APP_DIR%\monitoring\logs" mkdir "%APP_DIR%\monitoring\logs"
if not exist "%APP_DIR%\monitoring\exports" mkdir "%APP_DIR%\monitoring\exports"

REM Set proper permissions (Windows)
echo 🔒 Setting directory permissions...
icacls "%APP_DIR%\logs" /grant Users:(OI)(CI)F >nul 2>&1
icacls "%APP_DIR%\exports" /grant Users:(OI)(CI)F >nul 2>&1
icacls "%APP_DIR%\monitoring\logs" /grant Users:(OI)(CI)F >nul 2>&1
icacls "%APP_DIR%\monitoring\exports" /grant Users:(OI)(CI)F >nul 2>&1

REM Test the installation
echo 🧪 Testing Python environment...
python -c "import sys; print(f'Python {sys.version}')"
if %ERRORLEVEL% neq 0 (
    echo ❌ Python test failed
    exit /b 1
)

echo 🧪 Testing PySide6...
python -c "import PySide6; print(f'PySide6 {PySide6.__version__}')"
if %ERRORLEVEL% neq 0 (
    echo ❌ PySide6 test failed
    exit /b 1
)

echo 🧪 Testing pyserial...
python -c "import serial; print(f'pyserial {serial.__version__}')"
if %ERRORLEVEL% neq 0 (
    echo ❌ pyserial test failed
    exit /b 1
)

REM Deactivate virtual environment
deactivate

echo.
echo ======================================================
echo 🎉 Environment Setup Completed Successfully!
echo ======================================================
echo.
echo ✅ Python virtual environment created: %VENV_DIR%
echo ✅ All requirements installed
echo ✅ Application directories created
echo ✅ Permissions set
echo.
echo 🚀 Roll Machine Monitor is ready to use!
echo.

exit /b 0 