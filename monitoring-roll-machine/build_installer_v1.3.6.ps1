# Build installer for Monitoring Roll Machine v1.3.6
# PowerShell script to build NSIS installer with Zebra printer fix

Write-Host "========================================" -ForegroundColor Green
Write-Host "Building Monitoring Roll Machine v1.3.6" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if NSIS is installed
try {
    $null = Get-Command makensis -ErrorAction Stop
    Write-Host "✓ NSIS found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: NSIS (makensis) is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install NSIS from https://nsis.sourceforge.io/" -ForegroundColor Yellow
    Write-Host "and make sure makensis.exe is in your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required files exist
$requiredFiles = @(
    "installer_v1.3.6.nsi",
    "dist\MonitoringRollMachine.exe",
    "LICENSE.txt"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "ERROR: $file not found" -ForegroundColor Red
        if ($file -eq "dist\MonitoringRollMachine.exe") {
            Write-Host "Please build the application first using build_all_v1.3.6.bat" -ForegroundColor Yellow
        }
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        Write-Host "✓ $file found" -ForegroundColor Green
    }
}

# Create version info file
Write-Host ""
Write-Host "Creating version_info.txt..." -ForegroundColor Cyan
$buildDate = Get-Date -Format "yyyy-MM-dd"
$buildTime = Get-Date -Format "HH:mm:ss"

@"
VERSION=1.3.6
BUILD_DATE=$buildDate
BUILD_TIME=$buildTime
BUILD_TYPE=Release
FEATURES=Zebra Printer Fix, Enhanced Printing, Improved Error Handling
"@ | Out-File -FilePath "version_info.txt" -Encoding UTF8

Write-Host "✓ version_info.txt created" -ForegroundColor Green

# Build the installer
Write-Host ""
Write-Host "Building NSIS installer..." -ForegroundColor Cyan
Write-Host ""

try {
    # Run makensis with verbose output
    $process = Start-Process -FilePath "makensis" -ArgumentList "/V2", "installer_v1.3.6.nsi" -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "SUCCESS: Installer built successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Output file: Monitoring-Roll-Machine-v1.3.6-Setup.exe" -ForegroundColor White
        Write-Host ""
        Write-Host "Features included:" -ForegroundColor Yellow
        Write-Host "- Fixed Zebra ZD230 printer compatibility" -ForegroundColor White
        Write-Host "- Enhanced printing system" -ForegroundColor White
        Write-Host "- Improved error handling" -ForegroundColor White
        Write-Host "- Update capability from previous versions" -ForegroundColor White
        Write-Host ""
        
        # Check if installer was created
        if (Test-Path "Monitoring-Roll-Machine-v1.3.6-Setup.exe") {
            $installerSize = (Get-Item "Monitoring-Roll-Machine-v1.3.6-Setup.exe").Length
            $installerSizeMB = [math]::Round($installerSize / 1MB, 2)
            Write-Host "Installer size: $installerSizeMB MB" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now distribute this installer to users." -ForegroundColor Green
        } else {
            Write-Host "WARNING: Installer file was not created successfully." -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "ERROR: Installer build failed!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check the error messages above." -ForegroundColor Yellow
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "- Missing required files" -ForegroundColor White
        Write-Host "- NSIS syntax errors" -ForegroundColor White
        Write-Host "- File permissions" -ForegroundColor White
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run makensis" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Build process completed." -ForegroundColor Cyan
Read-Host "Press Enter to exit"
