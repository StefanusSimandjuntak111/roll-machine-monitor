# ===============================================
# GitHub Release Creator for Roll Machine Monitor
# ===============================================

param(
    [string]$Version = "1.3.1",
    [string]$Repository = "StefanusSimandjuntak111/roll-machine-monitor",
    [string]$InstallerPath = "..\releases\windows\RollMachineMonitor-v1.3.1-Windows-Installer.exe"
)

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Creating GitHub Release for v$Version" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
$ghInstalled = $null
try {
    $ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
} catch {
    $ghInstalled = $null
}

if (-not $ghInstalled) {
    Write-Host "GitHub CLI (gh) not found!" -ForegroundColor Red
    Write-Host "Please install GitHub CLI from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Create release manually on GitHub website" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/$Repository/releases" -ForegroundColor White
    Write-Host "2. Click 'Create a new release'" -ForegroundColor White
    Write-Host "3. Tag: v$Version" -ForegroundColor White
    Write-Host "4. Title: Roll Machine Monitor v$Version - Smart Settings Update" -ForegroundColor White
    Write-Host "5. Copy content from: docs/GITHUB_RELEASE_v$Version.md" -ForegroundColor White
    Write-Host "6. Upload installer: $InstallerPath" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if installer exists
if (-not (Test-Path $InstallerPath)) {
    Write-Host "Installer not found: $InstallerPath" -ForegroundColor Red
    Write-Host "Please build the installer first using:" -ForegroundColor Yellow
    Write-Host "  .\build-installer-v$Version.ps1" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if release notes exist
$releaseNotesPath = "..\docs\GITHUB_RELEASE_v$Version.md"
if (-not (Test-Path $releaseNotesPath)) {
    Write-Host "Release notes not found: $releaseNotesPath" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Read release notes
$releaseNotes = Get-Content $releaseNotesPath -Raw

Write-Host "Repository: $Repository" -ForegroundColor Green
Write-Host "Version: v$Version" -ForegroundColor Green
Write-Host "Installer: $InstallerPath" -ForegroundColor Green
Write-Host "Release Notes: $releaseNotesPath" -ForegroundColor Green
Write-Host ""

# Confirm release creation
$confirm = Read-Host "Create GitHub release for v$Version? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Release creation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Creating GitHub release..." -ForegroundColor Yellow

try {
    # Create release with GitHub CLI
    $releaseTitle = "Roll Machine Monitor v$Version - Smart Settings Update"
    
    # Create the release
    $releaseCmd = "gh release create v$Version --title `"$releaseTitle`" --notes `"$releaseNotes`" --repo $Repository"
    Write-Host "Command: $releaseCmd" -ForegroundColor Gray
    
    Invoke-Expression $releaseCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host "SUCCESS: GitHub release created!" -ForegroundColor Green
        Write-Host "===============================================" -ForegroundColor Green
        Write-Host ""
        
        # Upload installer asset
        Write-Host "Uploading installer asset..." -ForegroundColor Yellow
        $uploadCmd = "gh release upload v$Version `"$InstallerPath`" --repo $Repository"
        Invoke-Expression $uploadCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Installer uploaded successfully!" -ForegroundColor Green
        } else {
            Write-Host "Warning: Failed to upload installer" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "Release URL: https://github.com/$Repository/releases/tag/v$Version" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Release created successfully!" -ForegroundColor Green
        Write-Host "Users can now download the installer from GitHub." -ForegroundColor White
        Write-Host ""
        
        # Open release URL
        $openBrowser = Read-Host "Open release page in browser? (y/n)"
        if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
            Start-Process "https://github.com/$Repository/releases/tag/v$Version"
        }
        
    } else {
        Write-Host ""
        Write-Host "===============================================" -ForegroundColor Red
        Write-Host "ERROR: Failed to create GitHub release!" -ForegroundColor Red
        Write-Host "===============================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "1. GitHub CLI authentication (gh auth login)" -ForegroundColor White
        Write-Host "2. Repository access permissions" -ForegroundColor White
        Write-Host "3. Tag already exists (delete if needed)" -ForegroundColor White
        Write-Host ""
    }
    
} catch {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Red
    Write-Host "ERROR: Exception occurred!" -ForegroundColor Red
    Write-Host "===============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual release creation:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/$Repository/releases" -ForegroundColor White
    Write-Host "2. Click 'Create a new release'" -ForegroundColor White
    Write-Host "3. Tag: v$Version" -ForegroundColor White
    Write-Host "4. Title: $releaseTitle" -ForegroundColor White
    Write-Host "5. Copy content from: $releaseNotesPath" -ForegroundColor White
    Write-Host "6. Upload installer: $InstallerPath" -ForegroundColor White
    Write-Host ""
}

Read-Host "Press Enter to exit" 