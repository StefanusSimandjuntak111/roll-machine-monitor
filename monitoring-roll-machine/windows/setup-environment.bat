@echo off
echo ========================================
echo Setting up Python Environment
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+ first.
    echo You can download it from: https://www.python.org/downloads/
    echo.
    echo After installing Python, run this installer again.
    pause
    exit /b 1
)

echo Python found. Version:
python --version
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q "venv" 2>nul
)

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Python Environment Setup Complete!
echo ========================================
echo.
echo Virtual environment created in: venv\
echo Requirements installed from: requirements.txt
echo.
echo You can now run the application using:
echo   python run_app.py
echo.
pause

