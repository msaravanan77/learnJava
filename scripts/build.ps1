#
# YourEDR Build Script
# Builds driver, service, and MSI installer
#
# Usage: .\build.ps1 [-Configuration Debug|Release] [-SkipDriver] [-SkipService] [-SkipInstaller]
#

param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    [switch]$SkipDriver,
    [switch]$SkipService,
    [switch]$SkipInstaller,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionDir = Split-Path -Parent $ScriptDir
$SolutionFile = Join-Path $SolutionDir "WindowsEDR.sln"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YourEDR Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration: $Configuration"
Write-Host "Solution: $SolutionFile"
Write-Host ""

# Check if Visual Studio is installed
$msbuildPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" `
    -latest -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe `
    -prerelease | Select-Object -First 1

if (-not $msbuildPath) {
    Write-Error "MSBuild not found. Please install Visual Studio 2022 with WDK."
    exit 1
}

Write-Host "Using MSBuild: $msbuildPath" -ForegroundColor Green
Write-Host ""

# Clean if requested
if ($Clean) {
    Write-Host "Cleaning solution..." -ForegroundColor Yellow
    & $msbuildPath $SolutionFile /t:Clean /p:Configuration=$Configuration /p:Platform=x64
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Clean failed"
        exit 1
    }
    Write-Host "Clean completed" -ForegroundColor Green
    Write-Host ""
}

# Build driver
if (-not $SkipDriver) {
    Write-Host "Building kernel driver..." -ForegroundColor Yellow
    $DriverProject = Join-Path $SolutionDir "driver\YourEDRFilter\YourEDRFilter.vcxproj"

    & $msbuildPath $DriverProject `
        /p:Configuration=$Configuration `
        /p:Platform=x64 `
        /p:DeployExtension=false `
        /verbosity:minimal

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Driver build failed"
        exit 1
    }

    Write-Host "Driver build completed" -ForegroundColor Green
    Write-Host ""
}

# Build service
if (-not $SkipService) {
    Write-Host "Building user-mode service..." -ForegroundColor Yellow
    $ServiceProject = Join-Path $SolutionDir "service\YourEDRService\YourEDRService.vcxproj"

    & $msbuildPath $ServiceProject `
        /p:Configuration=$Configuration `
        /p:Platform=x64 `
        /verbosity:minimal

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Service build failed"
        exit 1
    }

    Write-Host "Service build completed" -ForegroundColor Green
    Write-Host ""
}

# Build MSI installer
if (-not $SkipInstaller) {
    Write-Host "Building MSI installer..." -ForegroundColor Yellow

    # Check if WiX is installed
    $wixPath = "${env:ProgramFiles(x86)}\WiX Toolset v3.11\bin"
    if (-not (Test-Path $wixPath)) {
        Write-Warning "WiX Toolset not found at $wixPath"
        Write-Warning "Please install WiX Toolset v3.11 from https://wixtoolset.org/"
        Write-Warning "Skipping MSI build..."
    } else {
        $InstallerProject = Join-Path $SolutionDir "installer\WiX\YourEDR.wixproj"

        & $msbuildPath $InstallerProject `
            /p:Configuration=$Configuration `
            /p:Platform=x64 `
            /verbosity:minimal

        if ($LASTEXITCODE -ne 0) {
            Write-Error "MSI installer build failed"
            exit 1
        }

        Write-Host "MSI installer build completed" -ForegroundColor Green
        $MsiPath = Join-Path $SolutionDir "installer\output\YourEDR_Installer_v1.0.0.msi"
        if (Test-Path $MsiPath) {
            Write-Host "MSI file: $MsiPath" -ForegroundColor Cyan
        }
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output locations:" -ForegroundColor Cyan
Write-Host "  Driver:  $SolutionDir\driver\YourEDRFilter\bin\$Configuration\" -ForegroundColor Gray
Write-Host "  Service: $SolutionDir\service\YourEDRService\bin\$Configuration\" -ForegroundColor Gray
Write-Host "  MSI:     $SolutionDir\installer\output\" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Sign the driver using: .\scripts\sign.ps1" -ForegroundColor Gray
Write-Host "  2. Install locally using: .\scripts\install-local.ps1" -ForegroundColor Gray
Write-Host ""
