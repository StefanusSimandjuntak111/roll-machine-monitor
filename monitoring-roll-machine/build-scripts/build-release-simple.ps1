# Build Release v1.2.6 for antiX (Simple Version)
# Enhanced Settings & Port Management

$VERSION = "v1.2.6"
$PACKAGE_NAME = "rollmachine-monitor-${VERSION}-antix"
$BUILD_DIR = "releases/${PACKAGE_NAME}"

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

Write-Host "✅ Build completed successfully!" -ForegroundColor Green
Write-Host "📦 Package directory: $BUILD_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ready for manual packaging!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Navigate to releases directory" -ForegroundColor White
Write-Host "2. Create tar.gz manually or use 7-Zip" -ForegroundColor White
Write-Host "3. Upload to client" -ForegroundColor White 