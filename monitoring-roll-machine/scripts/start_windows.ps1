# Windows PowerShell startup script for Roll Machine Monitor
# This script sets up the environment and starts the application

Write-Host "Starting Roll Machine Monitor for Windows..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
$venvPath = "venv_windows"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Host "Virtual environment created successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
try {
    & $activateScript
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate virtual environment"
    }
} catch {
    Write-Host "ERROR: Failed to activate virtual environment: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if needed
$pyside6Path = Join-Path $venvPath "Lib\site-packages\PySide6"
if (-not (Test-Path $pyside6Path)) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        Write-Host "Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install dependencies: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Start the application
Write-Host "Starting application..." -ForegroundColor Green
Write-Host ""

try {
    # Set Python path and run application
    python -c "import sys; sys.path.insert(0, '.'); from monitoring.ui.main_window import main; main()"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Application exited with error code $LASTEXITCODE" -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to start application: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} 