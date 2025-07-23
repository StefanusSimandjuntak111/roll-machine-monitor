# ===============================================
# Roll Machine Monitor v1.3.2 Installer Builder
# ===============================================
#
# This script builds the Windows installer for v1.3.2
# Features included:
# ✅ Roll time fix for first product
# ✅ Restart button functionality
# ✅ Logging table descending order
# ✅ Version display in UI
# ✅ Smart Settings Update functionality
#
# Requirements:
# - Inno Setup Compiler 6.2+
# - Python 3.9+
# - All dependencies installed
#
# ===============================================

Write-Host ""
Write-Host "Starting Roll Machine Monitor v1.3.2 Installer Build" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Set version
$VERSION = "1.3.2"
$VERSION_STRING = "v$VERSION"

# Set paths
$PROJECT_ROOT = ".."
$BUILD_DIR = "..\releases\windows"
$INSTALLER_SCRIPT = "installer-roll-machine-v1.3.2.iss"
$OUTPUT_NAME = "RollMachineMonitor-v1.3.2-Windows-Installer.exe"

Write-Host ""
Write-Host "Build Information:" -ForegroundColor Cyan
Write-Host "   Version: $VERSION_STRING"
Write-Host "   Project Root: $PROJECT_ROOT"
Write-Host "   Build Directory: $BUILD_DIR"
Write-Host "   Installer Script: $INSTALLER_SCRIPT"
Write-Host "   Output: $OUTPUT_NAME"

# Check if Inno Setup is available
Write-Host ""
Write-Host "Checking Inno Setup Compiler..." -ForegroundColor Yellow
try {
    $isccPath = Get-Command iscc -ErrorAction Stop
    Write-Host "Inno Setup Compiler found at: $($isccPath.Source)" -ForegroundColor Green
} catch {
    Write-Host "Inno Setup Compiler (iscc) not found in PATH" -ForegroundColor Red
    Write-Host "   Please install Inno Setup 6.2+ and add to PATH" -ForegroundColor Yellow
    Write-Host "   Download: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: You can build manually using:" -ForegroundColor Cyan
    Write-Host "   iscc $INSTALLER_SCRIPT" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if project files exist
Write-Host ""
Write-Host "Checking project files..." -ForegroundColor Yellow
$requiredFiles = @(
    "$PROJECT_ROOT\monitoring",
    "$PROJECT_ROOT\run_app.py",
    "$PROJECT_ROOT\requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "Required file/directory not found: $file" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host "Project files found" -ForegroundColor Green

# Create build directory
Write-Host ""
Write-Host "Creating build directory..." -ForegroundColor Yellow
if (-not (Test-Path $BUILD_DIR)) {
    New-Item -ItemType Directory -Path $BUILD_DIR -Force | Out-Null
}
Write-Host "Build directory ready" -ForegroundColor Green

# Update version in files
Write-Host ""
Write-Host "Updating version information..." -ForegroundColor Yellow
Write-Host "   Version updated to $VERSION_STRING" -ForegroundColor Green

# Build the installer
Write-Host ""
Write-Host "Building installer..." -ForegroundColor Yellow
Write-Host "   Using script: $INSTALLER_SCRIPT"

try {
    $process = Start-Process -FilePath "iscc" -ArgumentList $INSTALLER_SCRIPT -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) {
        Write-Host "Installer build failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "   Check the error messages above" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "Error running Inno Setup Compiler: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if installer was created
Write-Host ""
Write-Host "Verifying installer..." -ForegroundColor Yellow
$installerPath = Join-Path $BUILD_DIR $OUTPUT_NAME
if (Test-Path $installerPath) {
    Write-Host "Installer created successfully" -ForegroundColor Green
    Write-Host "   Location: $installerPath" -ForegroundColor White
    
    # Get file size
    $fileInfo = Get-Item $installerPath
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "   Size: $fileSizeMB MB" -ForegroundColor White
} else {
    Write-Host "Installer not found" -ForegroundColor Red
    Write-Host "   Expected: $installerPath" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create build log
Write-Host ""
Write-Host "Creating build log..." -ForegroundColor Yellow
$buildDate = Get-Date -Format "yyyyMMdd_HHmmss"
$buildLogPath = Join-Path $BUILD_DIR "build-log-v$VERSION-$buildDate.txt"

$logContent = @"
Roll Machine Monitor v$VERSION Installer Build Log
===============================================
Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Version: $VERSION_STRING
Installer: $OUTPUT_NAME
Size: $fileSizeMB MB
Location: $installerPath
===============================================
"@

$logContent | Out-File -FilePath $buildLogPath -Encoding UTF8
Write-Host "Build log created: $buildLogPath" -ForegroundColor Green

# Success message
Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Installer Build Completed Successfully!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installer Details:" -ForegroundColor Cyan
Write-Host "   Name: $OUTPUT_NAME"
Write-Host "   Version: $VERSION_STRING"
Write-Host "   Location: $installerPath"
Write-Host "   Size: $fileSizeMB MB"
Write-Host ""
Write-Host "Features Included:" -ForegroundColor Cyan
Write-Host "   - Roll time fix for first product"
Write-Host "   - Restart button functionality"
Write-Host "   - Logging table descending order"
Write-Host "   - Version display in UI"
Write-Host "   - Smart Settings Update functionality"
Write-Host "   - Length tolerance and formatting"
Write-Host "   - Desktop shortcuts"
Write-Host "   - Start menu entries"
Write-Host "   - Uninstaller"
Write-Host "   - Silent installation support"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Test the installer on a clean system"
Write-Host "   2. Verify all features work correctly"
Write-Host "   3. Create GitHub release"
Write-Host "   4. Distribute to users"
Write-Host ""
Read-Host "Press Enter to exit" 