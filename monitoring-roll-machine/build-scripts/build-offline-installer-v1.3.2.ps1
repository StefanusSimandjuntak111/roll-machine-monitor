# ===============================================
# Roll Machine Monitor v1.3.2 Complete Offline Builder
# ===============================================
#
# This script creates a complete offline installer with all dependencies
# bundled using PyInstaller
#
# Features:
# ✅ Complete application with all dependencies
# ✅ Roll time fix for first product
# ✅ Restart button functionality
# ✅ Logging table descending order
# ✅ Version display in UI
# ✅ Smart Settings Update functionality
#
# ===============================================

Write-Host ""
Write-Host "Starting Roll Machine Monitor v1.3.2 Complete Offline Build" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Set version
$VERSION = "1.3.2"
$VERSION_STRING = "v$VERSION"

# Set paths
$PROJECT_ROOT = ".."
$BUILD_DIR = "..\releases\windows"
$OUTPUT_NAME = "RollMachineMonitor-v1.3.2-Windows-Complete-Offline.exe"

Write-Host ""
Write-Host "Build Information:" -ForegroundColor Yellow
Write-Host "   Version: $VERSION_STRING"
Write-Host "   Project Root: $PROJECT_ROOT"
Write-Host "   Build Directory: $BUILD_DIR"
Write-Host "   Output: $OUTPUT_NAME"

# Check if PyInstaller is available
Write-Host ""
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    Write-Host "PyInstaller found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to check PyInstaller" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if project files exist
Write-Host ""
Write-Host "Checking project files..." -ForegroundColor Yellow
if (-not (Test-Path "$PROJECT_ROOT\monitoring")) {
    Write-Host "ERROR: Monitoring directory not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
if (-not (Test-Path "$PROJECT_ROOT\run_app.py")) {
    Write-Host "ERROR: run_app.py not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Project files found" -ForegroundColor Green

# Create build directory
Write-Host ""
Write-Host "Creating build directory..." -ForegroundColor Yellow
if (-not (Test-Path $BUILD_DIR)) {
    New-Item -ItemType Directory -Path $BUILD_DIR -Force | Out-Null
}
Write-Host "Build directory ready" -ForegroundColor Green

# Create PyInstaller spec file
Write-Host ""
Write-Host "Creating PyInstaller spec file..." -ForegroundColor Yellow
$SPEC_FILE = "roll_machine_monitor_v1.3.2.spec"

$specContent = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['$PROJECT_ROOT/run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('$PROJECT_ROOT/monitoring', 'monitoring'),
        ('$PROJECT_ROOT/requirements.txt', '.'),
        ('$PROJECT_ROOT/README.md', '.'),
        ('$PROJECT_ROOT/scripts', 'scripts'),
        ('$PROJECT_ROOT/tools', 'tools'),
        ('$PROJECT_ROOT/windows', 'windows'),
        ('$PROJECT_ROOT/docs', 'docs'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'pyqtgraph',
        'serial',
        'yaml',
        'appdirs',
        'qrcode',
        'PIL',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RollMachineMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RollMachineMonitor',
)
"@

$specContent | Out-File -FilePath $SPEC_FILE -Encoding UTF8
Write-Host "Spec file created: $SPEC_FILE" -ForegroundColor Green

# Build with PyInstaller
Write-Host ""
Write-Host "Building with PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller --clean $SPEC_FILE

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if build was successful
Write-Host ""
Write-Host "Checking build output..." -ForegroundColor Yellow
if (-not (Test-Path "dist\RollMachineMonitor")) {
    Write-Host "ERROR: Build output not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Build output found" -ForegroundColor Green

# Create installer using Inno Setup
Write-Host ""
Write-Host "Creating installer with Inno Setup..." -ForegroundColor Yellow
if (Test-Path "build-offline-installer-v1.3.2.iss") {
    iscc build-offline-installer-v1.3.2.iss
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Inno Setup build failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "WARNING: Inno Setup script not found, skipping installer creation" -ForegroundColor Yellow
}

# Check if installer was created
Write-Host ""
Write-Host "Checking installer..." -ForegroundColor Yellow
if (Test-Path "$BUILD_DIR\$OUTPUT_NAME") {
    Write-Host "Installer created successfully" -ForegroundColor Green
    $fileInfo = Get-Item "$BUILD_DIR\$OUTPUT_NAME"
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "Size: $fileSizeMB MB" -ForegroundColor Green
} else {
    Write-Host "WARNING: Installer not found" -ForegroundColor Yellow
}

# Clean up
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path $SPEC_FILE) { Remove-Item $SPEC_FILE -Force }
if (Test-Path "*.spec") { Remove-Item "*.spec" -Force }

Write-Host "Cleanup completed" -ForegroundColor Green

# Success message
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Build Completed Successfully!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files created:" -ForegroundColor Yellow
Write-Host "   - PyInstaller bundle: dist\RollMachineMonitor\"
Write-Host "   - Installer: $BUILD_DIR\$OUTPUT_NAME"
Write-Host ""
Write-Host "Features included:" -ForegroundColor Yellow
Write-Host "   - Complete application with all dependencies"
Write-Host "   - Roll time fix for first product"
Write-Host "   - Restart button functionality"
Write-Host "   - Logging table descending order"
Write-Host "   - Version display in UI"
Write-Host "   - Smart Settings Update functionality"
Write-Host ""

Read-Host "Press Enter to exit" 