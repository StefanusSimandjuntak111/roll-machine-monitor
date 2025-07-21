# ===============================================
# Roll Machine Monitor v1.3.1 Installer Builder
# Smart Settings Update Edition
# ===============================================

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Building Roll Machine Monitor v1.3.1 Installer" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Set version and paths
$VERSION = "1.3.1"
$APP_NAME = "RollMachineMonitor"
$OUTPUT_DIR = "..\releases\windows"
$INSTALLER_NAME = "$APP_NAME-v$VERSION-Windows-Installer"

# Create output directory if it doesn't exist
if (-not (Test-Path $OUTPUT_DIR)) {
    Write-Host "Creating output directory: $OUTPUT_DIR" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
}

# Check if Inno Setup is installed
$INNO_COMPILER = $null
$possiblePaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $INNO_COMPILER = $path
        break
    }
}

if (-not $INNO_COMPILER) {
    Write-Host "ERROR: Inno Setup Compiler not found!" -ForegroundColor Red
    Write-Host "Please install Inno Setup 6.2+ from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Using Inno Setup Compiler: $INNO_COMPILER" -ForegroundColor Green
Write-Host ""

# Check if installer script exists
$installerScript = "installer-roll-machine-v1.3.1.iss"
if (-not (Test-Path $installerScript)) {
    Write-Host "ERROR: Installer script not found: $installerScript" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Build the installer
Write-Host "Building installer..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath $INNO_COMPILER -ArgumentList $installerScript -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host "SUCCESS: Installer built successfully!" -ForegroundColor Green
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host ""
        
        $installerPath = "$OUTPUT_DIR\$INSTALLER_NAME.exe"
        if (Test-Path $installerPath) {
            $fileSize = (Get-Item $installerPath).Length
            $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
            
            Write-Host "Installer location: $installerPath" -ForegroundColor White
            Write-Host "File size: $fileSizeMB MB ($fileSize bytes)" -ForegroundColor White
            Write-Host ""
            
            Write-Host "Features included:" -ForegroundColor Cyan
            Write-Host "- Complete application with all features" -ForegroundColor White
            Write-Host "- Smart Settings Update functionality" -ForegroundColor White
            Write-Host "- Length tolerance and formatting" -ForegroundColor White
            Write-Host "- Desktop shortcuts" -ForegroundColor White
            Write-Host "- Start menu entries" -ForegroundColor White
            Write-Host "- Uninstaller" -ForegroundColor White
            Write-Host "- Silent installation support" -ForegroundColor White
            Write-Host ""
            
            Write-Host "Ready for distribution to users!" -ForegroundColor Green
            Write-Host ""
            
            # Open the output directory
            $openFolder = Read-Host "Open output folder? (y/n)"
            if ($openFolder -eq 'y' -or $openFolder -eq 'Y') {
                Start-Process "explorer.exe" -ArgumentList $OUTPUT_DIR
            }
        } else {
            Write-Host "WARNING: Installer file not found at expected location" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "===============================================" -ForegroundColor Red
        Write-Host "ERROR: Failed to build installer!" -ForegroundColor Red
        Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "===============================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check the error messages above." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Red
    Write-Host "ERROR: Exception occurred during build!" -ForegroundColor Red
    Write-Host "===============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit" 