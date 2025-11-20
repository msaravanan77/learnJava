# YourEDR Build and Verification Guide

**Version**: 2.0
**Date**: 2025-11-19
**Purpose**: Comprehensive guide to build, install, and verify YourEDR system

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Process](#build-process)
3. [Installation](#installation)
4. [Verification Steps](#verification-steps)
5. [Troubleshooting](#troubleshooting)
6. [Performance Validation](#performance-validation)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Windows 10/11 | 64-bit | Target OS |
| Visual Studio 2022 | Community/Pro/Enterprise | Compilation |
| Windows SDK | 10.0.22621.0 or later | Windows APIs |
| WDK (Windows Driver Kit) | 10.0.22621.0 or later | Driver development |
| PowerShell | 5.1 or later | Build scripts |

### Installation Steps

```powershell
# Install Visual Studio 2022
# Download from: https://visualstudio.microsoft.com/downloads/
# Workloads: "Desktop development with C++"

# Install WDK
# Download from: https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk
# Install matching SDK version first

# Verify installations
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" /?
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" /?
```

### System Configuration

```powershell
# Enable test signing (REQUIRED for development)
bcdedit /set testsigning on

# Reboot required
Restart-Computer
```

**⚠️ WARNING**: Test signing reduces system security. Only use on development systems.

---

## Build Process

### Quick Build (Automated)

```powershell
# Clone repository
git clone https://github.com/yourorg/learnJava.git
cd learnJava

# Build everything (Debug configuration)
.\scripts\build.ps1 -Configuration Debug

# Build for Release
.\scripts\build.ps1 -Configuration Release -Clean
```

### Manual Build Steps

#### 1. Build Kernel Driver

```powershell
cd driver\YourEDRFilter

# Build Debug x64
msbuild YourEDRFilter.vcxproj /p:Configuration=Debug /p:Platform=x64 /t:Rebuild

# Build Release x64
msbuild YourEDRFilter.vcxproj /p:Configuration=Release /p:Platform=x64 /t:Rebuild

# Verify output
dir x64\Debug\YourEDRFilter.sys
dir x64\Release\YourEDRFilter.sys
```

**Expected Output**:
- `YourEDRFilter.sys` - Kernel driver binary
- `YourEDRFilter.inf` - Driver installation file
- `YourEDRFilter.pdb` - Debug symbols

#### 2. Build User-Mode Service

```powershell
cd ..\..\service\YourEDRService

# Build Debug
msbuild YourEDRService.vcxproj /p:Configuration=Debug /p:Platform=x64 /t:Rebuild

# Build Release
msbuild YourEDRService.vcxproj /p:Configuration=Release /p:Platform=x64 /t:Rebuild

# Verify output
dir x64\Debug\YourEDRService.exe
dir x64\Release\YourEDRService.exe
```

#### 3. Sign Driver (Test Certificate)

```powershell
cd ..\..

# Create test certificate (first time only)
.\scripts\create-test-cert.ps1

# Sign driver
.\scripts\sign.ps1 -Configuration Debug

# Verify signature
signtool verify /pa driver\YourEDRFilter\x64\Debug\YourEDRFilter.sys
```

**Expected Output**:
```
Successfully verified: driver\YourEDRFilter\x64\Debug\YourEDRFilter.sys
```

#### 4. Build MSI Installer (Optional)

```powershell
# Requires WiX Toolset 3.11+
# Download from: https://wixtoolset.org/

# Build installer
msbuild installer\WiX\YourEDR.wixproj /p:Configuration=Release /p:Platform=x64

# Output
dir installer\WiX\bin\Release\YourEDR.msi
```

---

## Installation

### Method 1: Automated Installation (Recommended)

```powershell
# Run installation script (requires Administrator)
.\scripts\install-local.ps1

# This will:
# 1. Stop existing service (if running)
# 2. Unload existing driver (if loaded)
# 3. Copy files to system directories
# 4. Install driver via INF
# 5. Load driver with fltmc
# 6. Install and start service
```

### Method 2: Manual Installation

#### Step 1: Install Driver

```powershell
# Copy driver to system directory
Copy-Item -Path "driver\YourEDRFilter\x64\Debug\YourEDRFilter.sys" `
          -Destination "C:\Windows\System32\drivers\" -Force

Copy-Item -Path "driver\YourEDRFilter\x64\Debug\YourEDRFilter.inf" `
          -Destination "C:\Windows\System32\drivers\" -Force

# Install driver via INF
pnputil /add-driver "C:\Windows\System32\drivers\YourEDRFilter.inf" /install

# Load driver
fltmc load YourEDRFilter
```

#### Step 2: Install Service

```powershell
# Create service directory
New-Item -Path "C:\Program Files\YourEDR\bin" -ItemType Directory -Force

# Copy service executable
Copy-Item -Path "service\YourEDRService\x64\Debug\YourEDRService.exe" `
          -Destination "C:\Program Files\YourEDR\bin\" -Force

# Install service
& "C:\Program Files\YourEDR\bin\YourEDRService.exe" install

# Start service
& "C:\Program Files\YourEDR\bin\YourEDRService.exe" start

# Verify service
Get-Service -Name "YourEDRService"
```

---

## Verification Steps

### Level 1: Basic Verification

#### 1.1 Check Driver Status

```powershell
# List loaded filters
fltmc filters

# Expected output:
# Filter Name                     Num Instances    Altitude    Frame
# ------------------------------  -------------  ------------  -----
# YourEDRFilter                           3        325100         0
```

**✓ PASS**: Driver appears in list with altitude 325100
**✗ FAIL**: Driver not listed → Check installation logs

#### 1.2 Check Driver Instances

```powershell
fltmc instances -f YourEDRFilter

# Expected: Instances attached to volumes (C:, D:, etc.)
```

#### 1.3 Check Service Status

```powershell
Get-Service -Name "YourEDRService"

# Expected:
# Status   Name               DisplayName
# ------   ----               -----------
# Running  YourEDRService     YourEDR Service
```

**✓ PASS**: Status is "Running"
**✗ FAIL**: Check event logs

#### 1.4 Check Log Directory

```powershell
Get-ChildItem -Path "C:\ProgramData\YourEDR\Logs"

# Expected: events_YYYYMMDD_HHMMSS.jsonl files
```

### Level 2: Functional Verification

#### 2.1 File System Monitoring

```powershell
# Test file creation
$testFile = "$env:TEMP\verify_youredr_$(Get-Random).txt"
"Test content" | Out-File -FilePath $testFile -Force

# Wait for event processing
Start-Sleep -Seconds 1

# Check logs
$logPath = "C:\ProgramData\YourEDR\Logs"
$latestLog = Get-ChildItem -Path $logPath -Filter "events_*.jsonl" |
             Sort-Object LastWriteTime -Descending |
             Select-Object -First 1

$events = Get-Content -Path $latestLog.FullName -Tail 50 | ConvertFrom-Json

$fileEvent = $events | Where-Object {
    $_.eventType -eq "FileCreate" -and
    $_.filePath -like "*verify_youredr_*"
}

if ($fileEvent) {
    Write-Host "✓ PASS: File create event captured" -ForegroundColor Green
    $fileEvent | ConvertTo-Json -Depth 3
} else {
    Write-Host "✗ FAIL: File create event NOT captured" -ForegroundColor Red
}

# Cleanup
Remove-Item -Path $testFile -Force
```

#### 2.2 Network Monitoring

```powershell
# Test network connection
try {
    Invoke-WebRequest -Uri "http://example.com" -UseBasicParsing -TimeoutSec 5 | Out-Null
} catch {}

Start-Sleep -Seconds 1

# Check logs
$latestLog = Get-ChildItem -Path "C:\ProgramData\YourEDR\Logs" -Filter "events_*.jsonl" |
             Sort-Object LastWriteTime -Descending |
             Select-Object -First 1

$events = Get-Content -Path $latestLog.FullName -Tail 100 | ConvertFrom-Json

$networkEvent = $events | Where-Object {
    $_.eventType -eq "NetworkConnect" -and
    $_.remotePort -eq 80
}

if ($networkEvent) {
    Write-Host "✓ PASS: Network event captured" -ForegroundColor Green
    $networkEvent | Select-Object -First 1 | ConvertTo-Json -Depth 3
} else {
    Write-Host "✗ FAIL: Network event NOT captured" -ForegroundColor Red
    Write-Host "  Note: Network monitoring must be enabled in driver config"
}
```

### Level 3: Automated Test Suite

```powershell
# Run comprehensive tests
.\tests\run_all_tests.ps1 -GenerateReport

# Expected: All tests pass (or >95% pass rate for E2E)
```

---

## Troubleshooting

### Driver Won't Load

**Symptom**: `fltmc load YourEDRFilter` fails

**Possible Causes**:

1. **Test signing not enabled**
   ```powershell
   bcdedit /enum | Select-String "testsigning"
   # Should show: testsigning Yes
   ```
   **Fix**: `bcdedit /set testsigning on` and reboot

2. **Driver not signed**
   ```powershell
   signtool verify /pa YourEDRFilter.sys
   ```
   **Fix**: Run `.\scripts\sign.ps1`

3. **Driver file corrupt**
   **Fix**: Rebuild driver

4. **Check Event Viewer**
   ```powershell
   Get-WinEvent -LogName System -MaxEvents 50 |
       Where-Object { $_.Message -like "*YourEDR*" }
   ```

### Service Won't Start

**Symptom**: Service status is "Stopped"

**Checks**:

1. **Driver dependency**
   ```powershell
   fltmc filters | Select-String "YourEDRFilter"
   ```
   Service requires driver to be loaded first

2. **Check service logs**
   ```powershell
   Get-EventLog -LogName Application -Source "YourEDRService" -Newest 20
   ```

3. **Manual start for debugging**
   ```powershell
   & "C:\Program Files\YourEDR\bin\YourEDRService.exe"
   # Run without "install" argument to see console output
   ```

### No Events Appearing

**Symptom**: Log files empty or no recent events

**Checks**:

1. **Service running**
   ```powershell
   Get-Service YourEDRService
   ```

2. **Log permissions**
   ```powershell
   Test-Path "C:\ProgramData\YourEDR\Logs"
   icacls "C:\ProgramData\YourEDR\Logs"
   ```

3. **Driver statistics**
   ```powershell
   # Use IOCTL to check if events are being queued
   # See integration tests for example code
   ```

4. **Configuration check**
   ```powershell
   Get-Content "C:\Program Files\YourEDR\config\default_config.json"
   # Ensure monitoring is enabled
   ```

---

## Performance Validation

### Baseline Performance Test

```powershell
# Before installing YourEDR
Measure-Command {
    1..1000 | ForEach-Object {
        "Test" | Out-File -FilePath "$env:TEMP\perf_test_$_.txt" -Force
        Remove-Item -Path "$env:TEMP\perf_test_$_.txt" -Force
    }
}
# Record baseline time

# After installing YourEDR
Measure-Command {
    1..1000 | ForEach-Object {
        "Test" | Out-File -FilePath "$env:TEMP\perf_test_$_.txt" -Force
        Remove-Item -Path "$env:TEMP\perf_test_$_.txt" -Force
    }
}
# Compare with baseline

# Expected overhead: <20%
```

### Memory Usage Check

```powershell
# Service memory
Get-Process -Name "YourEDRService" | Select-Object WS, PM, VM

# Expected:
# - Working Set (WS): <20 MB under normal load
# - Private Memory (PM): <15 MB

# Driver memory (kernel pool)
# Use PoolMon from WDK:
& "C:\Program Files (x86)\Windows Kits\10\Tools\x64\poolmon.exe" -i YEDR

# Expected: <5 MB non-paged pool
```

### Event Throughput Test

```powershell
.\tests\stress\high_volume\test_high_event_rate.ps1 -NumOperations 10000

# Expected:
# - >5,000 operations/sec
# - <0.1% event drop rate
# - No memory leaks
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Build in Release configuration
- [ ] Sign driver with EV certificate (not test certificate)
- [ ] Test on clean Windows installation
- [ ] Run full test suite - all tests pass
- [ ] Performance validation complete
- [ ] Security review complete
- [ ] Documentation updated
- [ ] Rollback plan prepared

---

## Summary Verification Script

```powershell
# Quick verification script
Write-Host "YourEDR System Verification" -ForegroundColor Cyan

# 1. Driver
$driverOk = (fltmc filters | Select-String "YourEDRFilter") -ne $null
Write-Host "Driver Loaded: $(if ($driverOk) { '✓ YES' } else { '✗ NO' })" `
    -ForegroundColor $(if ($driverOk) { 'Green' } else { 'Red' })

# 2. Service
$serviceOk = (Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue)?.Status -eq "Running"
Write-Host "Service Running: $(if ($serviceOk) { '✓ YES' } else { '✗ NO' })" `
    -ForegroundColor $(if ($serviceOk) { 'Green' } else { 'Red' })

# 3. Logs
$logsOk = Test-Path "C:\ProgramData\YourEDR\Logs\events_*.jsonl"
Write-Host "Logs Present: $(if ($logsOk) { '✓ YES' } else { '✗ NO' })" `
    -ForegroundColor $(if ($logsOk) { 'Green' } else { 'Red' })

# 4. Recent events
if ($logsOk) {
    $latestLog = Get-ChildItem -Path "C:\ProgramData\YourEDR\Logs" -Filter "events_*.jsonl" |
                 Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $recentEvents = Get-Content -Path $latestLog.FullName -Tail 10
    Write-Host "Recent Events: $($recentEvents.Count)" -ForegroundColor Cyan
}

# Overall status
$allOk = $driverOk -and $serviceOk -and $logsOk
Write-Host "`nOverall Status: $(if ($allOk) { '✓ OPERATIONAL' } else { '✗ ISSUES DETECTED' })" `
    -ForegroundColor $(if ($allOk) { 'Green' } else { 'Red' })
```

---

**Document End**

**Last Updated**: 2025-11-19
**Maintained by**: Development Team
