#
# YourEDR Code Signing Script
# Signs driver and service executables for testing
#
# For development/testing: Uses test certificate
# For production: Use EV certificate
#
# Usage: .\sign.ps1 [-Configuration Debug|Release] [-UseProdCert]
#

param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    [switch]$UseProdCert,
    [string]$ProdCertThumbprint = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionDir = Split-Path -Parent $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YourEDR Code Signing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Files to sign
$DriverSys = Join-Path $SolutionDir "driver\YourEDRFilter\bin\$Configuration\YourEDRFilter.sys"
$ServiceExe = Join-Path $SolutionDir "service\YourEDRService\bin\$Configuration\YourEDRService.exe"
$DriverCat = Join-Path $SolutionDir "driver\YourEDRFilter\bin\$Configuration\YourEDRFilter.cat"

# Check if files exist
if (-not (Test-Path $DriverSys)) {
    Write-Error "Driver not found: $DriverSys. Run build.ps1 first."
    exit 1
}

if (-not (Test-Path $ServiceExe)) {
    Write-Error "Service not found: $ServiceExe. Run build.ps1 first."
    exit 1
}

if ($UseProdCert) {
    # Production signing with EV certificate
    Write-Host "Using production EV certificate..." -ForegroundColor Yellow

    if ([string]::IsNullOrEmpty($ProdCertThumbprint)) {
        Write-Error "Production certificate thumbprint not provided. Use -ProdCertThumbprint parameter."
        exit 1
    }

    Write-Host "Signing with certificate: $ProdCertThumbprint"

    # Sign driver
    Write-Host "Signing driver..." -ForegroundColor Yellow
    signtool sign /v /sha1 $ProdCertThumbprint /t http://timestamp.digicert.com /fd sha256 $DriverSys
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Driver signing failed"
        exit 1
    }

    # Sign service
    Write-Host "Signing service..." -ForegroundColor Yellow
    signtool sign /v /sha1 $ProdCertThumbprint /t http://timestamp.digicert.com /fd sha256 $ServiceExe
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Service signing failed"
        exit 1
    }

    Write-Host "Production signing completed" -ForegroundColor Green

} else {
    # Test signing for development
    Write-Host "Using test certificate for development..." -ForegroundColor Yellow
    Write-Host "NOTE: Test signing requires 'Test Mode' to be enabled on target system" -ForegroundColor Red
    Write-Host "      Run: bcdedit /set testsigning on" -ForegroundColor Red
    Write-Host ""

    # Check if test certificate exists
    $TestCertName = "YourEDR Test Certificate"
    $TestCert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*$TestCertName*" } | Select-Object -First 1

    if (-not $TestCert) {
        Write-Host "Test certificate not found. Creating..." -ForegroundColor Yellow
        & "$ScriptDir\create-test-cert.ps1"
        $TestCert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*$TestCertName*" } | Select-Object -First 1
    }

    if (-not $TestCert) {
        Write-Error "Failed to create test certificate"
        exit 1
    }

    $CertThumbprint = $TestCert.Thumbprint
    Write-Host "Using test certificate: $CertThumbprint" -ForegroundColor Cyan
    Write-Host ""

    # Sign driver
    Write-Host "Signing driver..." -ForegroundColor Yellow
    signtool sign /v /sha1 $CertThumbprint /t http://timestamp.digicert.com /fd sha256 $DriverSys
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Driver signing failed. This is expected if the certificate is not properly configured."
    }

    # Sign service
    Write-Host "Signing service..." -ForegroundColor Yellow
    signtool sign /v /sha1 $CertThumbprint /t http://timestamp.digicert.com /fd sha256 $ServiceExe
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Service signing failed. This is expected if the certificate is not properly configured."
    }

    Write-Host "Test signing completed" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Signing completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verify signatures:" -ForegroundColor Yellow
Write-Host "  signtool verify /pa $DriverSys" -ForegroundColor Gray
Write-Host "  signtool verify /pa $ServiceExe" -ForegroundColor Gray
Write-Host ""
