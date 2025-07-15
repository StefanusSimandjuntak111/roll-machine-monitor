# Build Release v1.2.6 for antiX (SysV init)
# Enhanced Settings & Port Management

$VERSION = "v1.2.6"
$PACKAGE_NAME = "rollmachine-monitor-${VERSION}-antix"
$BUILD_DIR = "releases/${PACKAGE_NAME}"
$CURRENT_DIR = Get-Location

Write-Host "🚀 Building Release ${VERSION} for antiX..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Clean previous build
if (Test-Path $BUILD_DIR) {
    Write-Host "🧹 Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $BUILD_DIR
}

# Create build directory
Write-Host "📁 Creating build directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $BUILD_DIR -Force | Out-Null

# Copy application files
Write-Host "📦 Copying application files..." -ForegroundColor Yellow
Copy-Item -Recurse "monitoring-roll-machine" $BUILD_DIR
Copy-Item -Recurse "monitoring" $BUILD_DIR
Copy-Item -Recurse "logs" $BUILD_DIR
Copy-Item -Recurse "exports" $BUILD_DIR

# Copy configuration files
Write-Host "⚙️ Copying configuration files..." -ForegroundColor Yellow
Copy-Item "config.json" $BUILD_DIR
Copy-Item "RELEASE_NOTES_v1.2.6.md" $BUILD_DIR

# Create VERSION file
Write-Host "📝 Creating VERSION file..." -ForegroundColor Yellow
$VERSION | Out-File -FilePath "$BUILD_DIR/VERSION" -Encoding UTF8

# Create package
Write-Host "📦 Creating package..." -ForegroundColor Yellow
Set-Location releases

# Use 7-Zip if available, otherwise use tar
if (Get-Command "7z" -ErrorAction SilentlyContinue) {
    Write-Host "Using 7-Zip to create package..." -ForegroundColor Yellow
    7z a -ttar "${PACKAGE_NAME}.tar" "$PACKAGE_NAME"
    7z a -tgzip "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}.tar"
    Remove-Item "${PACKAGE_NAME}.tar"
} else {
    Write-Host "Using tar to create package..." -ForegroundColor Yellow
    tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
}

# Create checksum
Write-Host "🔍 Creating checksum..." -ForegroundColor Yellow
$hash = Get-FileHash "${PACKAGE_NAME}.tar.gz" -Algorithm SHA256
$hash.Hash | Out-File -FilePath "${PACKAGE_NAME}.tar.gz.sha256" -Encoding UTF8

Set-Location $CURRENT_DIR

Write-Host "✅ Build completed successfully!" -ForegroundColor Green
Write-Host "📦 Package: releases/${PACKAGE_NAME}.tar.gz" -ForegroundColor Cyan
Write-Host "🔍 Checksum: releases/${PACKAGE_NAME}.tar.gz.sha256" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ready for deployment to antiX client!" -ForegroundColor Green
Write-Host ""
Write-Host "Installation commands for client:" -ForegroundColor Yellow
Write-Host "  tar -xzf ${PACKAGE_NAME}.tar.gz" -ForegroundColor White
Write-Host "  cd ${PACKAGE_NAME}" -ForegroundColor White
Write-Host "  sudo ./install-rollmachine.sh" -ForegroundColor White
Write-Host "  sudo reboot" -ForegroundColor White 