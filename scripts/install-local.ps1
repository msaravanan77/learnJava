#
# YourEDR Local Installation Script
# Installs driver and service for testing
#
# NOTE: Requires administrator privileges and test signing mode
#

#Requires -RunAsAdministrator

param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionDir = Split-Path -Parent $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YourEDR Local Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check test signing mode
$TestSigningEnabled = (bcdedit /enum) -match "testsigning\s+Yes"
if (-not $TestSigningEnabled) {
    Write-Warning "Test signing is not enabled!"
    Write-Warning "The driver may fail to load."
    Write-Host ""
    Write-Host "To enable test signing:" -ForegroundColor Yellow
    Write-Host "  bcdedit /set testsigning on" -ForegroundColor Gray
    Write-Host "  shutdown /r /t 0" -ForegroundColor Gray
    Write-Host ""

    $Response = Read-Host "Continue anyway? (y/n)"
    if ($Response -ne "y") {
        exit 1
    }
}

# File paths
$DriverSys = Join-Path $SolutionDir "driver\YourEDRFilter\bin\$Configuration\YourEDRFilter.sys"
$DriverInf = Join-Path $SolutionDir "driver\YourEDRFilter\YourEDRFilter.inf"
$ServiceExe = Join-Path $SolutionDir "service\YourEDRService\bin\$Configuration\YourEDRService.exe"

# Check if files exist
if (-not (Test-Path $DriverSys)) {
    Write-Error "Driver not found: $DriverSys. Run build.ps1 first."
    exit 1
}

if (-not (Test-Path $ServiceExe)) {
    Write-Error "Service not found: $ServiceExe. Run build.ps1 first."
    exit 1
}

Write-Host "Files to install:" -ForegroundColor Cyan
Write-Host "  Driver:  $DriverSys"
Write-Host "  Service: $ServiceExe"
Write-Host ""

# Stop existing service and driver if running
Write-Host "Stopping existing installation (if any)..." -ForegroundColor Yellow

try {
    $Service = Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue
    if ($Service -and $Service.Status -eq "Running") {
        Write-Host "  Stopping service..." -ForegroundColor Gray
        Stop-Service -Name "YourEDRService" -Force
    }
} catch {
    # Service doesn't exist or already stopped
}

try {
    $DriverLoaded = fltmc filters | Select-String "YourEDRFilter"
    if ($DriverLoaded) {
        Write-Host "  Unloading driver..." -ForegroundColor Gray
        fltmc unload YourEDRFilter 2>&1 | Out-Null
        Start-Sleep -Seconds 2
    }
} catch {
    # Driver not loaded
}

Write-Host "Stopped" -ForegroundColor Green
Write-Host ""

# Copy driver to System32\drivers
Write-Host "Installing driver..." -ForegroundColor Yellow

$DriverDestDir = "$env:SystemRoot\System32\drivers"
$DriverDest = Join-Path $DriverDestDir "YourEDRFilter.sys"

Copy-Item -Path $DriverSys -Destination $DriverDest -Force
Write-Host "  Copied driver to: $DriverDest" -ForegroundColor Gray

# Install driver INF (this creates the service entry)
Write-Host "  Installing INF..." -ForegroundColor Gray
$InfInstallOutput = pnputil /add-driver $DriverInf /install 2>&1
Write-Host "  $InfInstallOutput" -ForegroundColor DarkGray

# Alternatively, create service manually if INF install fails
try {
    sc.exe create YourEDRFilter type=filesys start=demand binPath=$DriverDest 2>&1 | Out-Null
} catch {
    # Service may already exist
}

Write-Host "Driver installed" -ForegroundColor Green
Write-Host ""

# Load driver
Write-Host "Loading driver..." -ForegroundColor Yellow

try {
    fltmc load YourEDRFilter
    Start-Sleep -Seconds 2

    $DriverStatus = fltmc filters | Select-String "YourEDRFilter"
    if ($DriverStatus) {
        Write-Host "Driver loaded successfully!" -ForegroundColor Green
        Write-Host "  Status: $DriverStatus" -ForegroundColor Gray
    } else {
        Write-Warning "Driver may not have loaded correctly"
    }
} catch {
    Write-Error "Failed to load driver: $_"
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check driver signature: signtool verify /pa $DriverSys" -ForegroundColor Gray
    Write-Host "  2. Check driver logs: Get-EventLog -LogName System -Source 'YourEDRFilter' -Newest 10" -ForegroundColor Gray
    Write-Host "  3. Enable kernel debugging for more details" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Install service
Write-Host "Installing service..." -ForegroundColor Yellow

$InstallDir = "C:\Program Files\YourEDR\bin"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

Copy-Item -Path $ServiceExe -Destination $InstallDir -Force
Write-Host "  Copied service to: $InstallDir" -ForegroundColor Gray

$ServiceExePath = Join-Path $InstallDir "YourEDRService.exe"

# Install service using the executable's built-in installer
Write-Host "  Registering service..." -ForegroundColor Gray
& $ServiceExePath install

# Create log directory
$LogDir = "C:\ProgramData\YourEDR\Logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "  Created log directory: $LogDir" -ForegroundColor Gray
}

Write-Host "Service installed" -ForegroundColor Green
Write-Host ""

# Start service
Write-Host "Starting service..." -ForegroundColor Yellow

try {
    & $ServiceExePath start
    Start-Sleep -Seconds 2

    $Service = Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue
    if ($Service -and $Service.Status -eq "Running") {
        Write-Host "Service started successfully!" -ForegroundColor Green
        Write-Host "  Status: $($Service.Status)" -ForegroundColor Gray
    } else {
        Write-Warning "Service may not have started correctly"
    }
} catch {
    Write-Error "Failed to start service: $_"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verification:" -ForegroundColor Yellow
Write-Host "  Driver status:  fltmc filters | findstr YourEDR" -ForegroundColor Gray
Write-Host "  Service status: sc query YourEDRService" -ForegroundColor Gray
Write-Host "  View logs:      Get-Content '$LogDir\*.jsonl' | Select-Object -Last 10" -ForegroundColor Gray
Write-Host ""
Write-Host "Testing:" -ForegroundColor Yellow
Write-Host "  Create a file to generate events:" -ForegroundColor Gray
Write-Host "  echo 'test' > C:\test.txt" -ForegroundColor Gray
Write-Host "  Get-Content '$LogDir\*.jsonl' | Select-Object -Last 5" -ForegroundColor Gray
Write-Host ""
