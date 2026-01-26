# Build script for Monitoring Roll Machine v1.4.3 Installer
# PowerShell version for better Windows integration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Monitoring Roll Machine v1.4.3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the build script
Write-Host "Starting build process..." -ForegroundColor Yellow
python build_v1.4.3.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installer location: releases\Monitoring-Roll-Machine-v1.4.3-Setup.exe" -ForegroundColor Cyan
    Write-Host ""
    
    # Ask if user wants to open the releases folder
    $openFolder = Read-Host "Open releases folder? (Y/N)"
    if ($openFolder -eq "Y" -or $openFolder -eq "y") {
        $releasesPath = Join-Path $PSScriptRoot "releases"
        if (Test-Path $releasesPath) {
            explorer $releasesPath
        }
    }
}

Read-Host "Press Enter to exit"
