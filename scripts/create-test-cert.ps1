#
# Create Test Certificate for Driver Signing
# This certificate is for DEVELOPMENT/TESTING ONLY
#
# NOTE: Requires administrator privileges
#

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Create Test Certificate" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$CertName = "YourEDR Test Certificate"
$CertDnsName = "YourCompany Driver Test"

# Check if certificate already exists
$ExistingCert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*$CertName*" }

if ($ExistingCert) {
    Write-Host "Test certificate already exists:" -ForegroundColor Yellow
    Write-Host "  Subject: $($ExistingCert.Subject)"
    Write-Host "  Thumbprint: $($ExistingCert.Thumbprint)"
    Write-Host "  Valid Until: $($ExistingCert.NotAfter)"
    Write-Host ""

    $Response = Read-Host "Do you want to create a new certificate? (y/n)"
    if ($Response -ne "y") {
        Write-Host "Keeping existing certificate" -ForegroundColor Green
        exit 0
    }

    # Remove existing certificate
    Write-Host "Removing existing certificate..." -ForegroundColor Yellow
    $ExistingCert | Remove-Item
}

# Create new self-signed certificate
Write-Host "Creating new test certificate..." -ForegroundColor Yellow

$Cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=$CertName" `
    -DnsName $CertDnsName `
    -KeyUsage DigitalSignature `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(5)

if (-not $Cert) {
    Write-Error "Failed to create certificate"
    exit 1
}

Write-Host "Certificate created successfully!" -ForegroundColor Green
Write-Host "  Subject: $($Cert.Subject)"
Write-Host "  Thumbprint: $($Cert.Thumbprint)"
Write-Host "  Valid Until: $($Cert.NotAfter)"
Write-Host ""

# Export certificate to file (for installing on other machines)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionDir = Split-Path -Parent $ScriptDir
$CertOutputDir = Join-Path $SolutionDir "installer\assets"

if (-not (Test-Path $CertOutputDir)) {
    New-Item -ItemType Directory -Path $CertOutputDir -Force | Out-Null
}

$CertFile = Join-Path $CertOutputDir "YourEDR_TestCert.cer"

Write-Host "Exporting certificate to file..." -ForegroundColor Yellow
Export-Certificate -Cert $Cert -FilePath $CertFile -Force | Out-Null
Write-Host "Certificate exported to: $CertFile" -ForegroundColor Cyan
Write-Host ""

# Install certificate to Trusted Root and Trusted Publishers
Write-Host "Installing certificate to Trusted Root and Trusted Publishers..." -ForegroundColor Yellow

try {
    # Import to Trusted Root
    Import-Certificate -FilePath $CertFile -CertStoreLocation "Cert:\LocalMachine\Root" -ErrorAction SilentlyContinue | Out-Null

    # Import to Trusted Publishers (required for driver installation)
    Import-Certificate -FilePath $CertFile -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher" -ErrorAction SilentlyContinue | Out-Null

    Write-Host "Certificate installed to system stores" -ForegroundColor Green
} catch {
    Write-Warning "Failed to install certificate to system stores. You may need to do this manually."
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Certificate creation completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Red
Write-Host "  1. Enable test signing mode (requires reboot):" -ForegroundColor Yellow
Write-Host "     bcdedit /set testsigning on" -ForegroundColor Gray
Write-Host "     shutdown /r /t 0" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. After reboot, you can sign your driver:" -ForegroundColor Yellow
Write-Host "     .\scripts\sign.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. To install on other machines, import the certificate:" -ForegroundColor Yellow
Write-Host "     certutil -addstore Root $CertFile" -ForegroundColor Gray
Write-Host "     certutil -addstore TrustedPublisher $CertFile" -ForegroundColor Gray
Write-Host ""
