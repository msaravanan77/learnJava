# Windows EDR System - Development & Testing Guide

## Document Purpose

This guide provides step-by-step instructions for developing and testing the Windows EDR system **WITHOUT** needing Microsoft's EV code signing certificate or WHQL certification. You'll learn how to use test signing mode to load your unsigned driver during development.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Enabling Test Signing Mode](#enabling-test-signing-mode)
3. [Creating Test Certificates](#creating-test-certificates)
4. [Building and Signing the Driver](#building-and-signing-the-driver)
5. [Loading and Testing the Driver](#loading-and-testing-the-driver)
6. [Kernel Debugging Setup](#kernel-debugging-setup)
7. [Testing Workflows](#testing-workflows)
8. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Hardware Requirements

**Development Machine**:
- Windows 10/11 Pro/Enterprise (64-bit)
- 16GB+ RAM
- 100GB+ free disk space
- Intel VT-x or AMD-V (for Hyper-V)

**Test Machine** (Virtual or Physical):
- Windows 10/11 (any edition)
- 4GB+ RAM
- 60GB disk space
- **Separate from development machine** (recommended)

### Software Installation

#### 1. Install Visual Studio 2022

```powershell
# Download VS 2022 Community/Professional/Enterprise
# Required workloads:
# - Desktop development with C++
# - .NET desktop development (for management tools)

# Verify installation
"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe" /?
```

#### 2. Install Windows Driver Kit (WDK) 11

```powershell
# Download from:
# https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk

# Run installer
wdksetup.exe /features + /ceip off

# Verify installation
dir "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\inf2cat.exe"
```

#### 3. Install WinDbg Preview

```powershell
# Install from Microsoft Store or:
winget install Microsoft.WinDbg

# Verify
where windbgx
```

#### 4. Install Additional Tools

```powershell
# Install vcpkg for C++ dependencies
git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
cd C:\vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install

# Install JSON library
.\vcpkg install nlohmann-json:x64-windows

# Install WiX Toolset (for MSI creation)
winget install WiXToolset.WiX
```

---

## Enabling Test Signing Mode

### What is Test Signing?

Windows normally requires all kernel-mode drivers to be signed by Microsoft through WHQL certification. **Test signing mode** allows you to load drivers signed with your own test certificate during development.

### Enable Test Signing (Development Machine)

**Option 1: Standard Method** (Recommended)

```powershell
# Open PowerShell as Administrator

# Enable test signing
bcdedit /set testsigning on

# Verify
bcdedit | findstr testsigning
# Should show: testsigning             Yes

# Reboot (required)
shutdown /r /t 0
```

After reboot, you'll see "Test Mode" watermark in bottom-right corner of desktop.

**Option 2: With Driver Signature Enforcement Disabled** (Less Secure, Use Only If Needed)

```powershell
# Enable test signing
bcdedit /set testsigning on

# Disable driver signature enforcement (OPTIONAL, not recommended)
bcdedit /set nointegritychecks on

# Reboot
shutdown /r /t 0
```

**⚠️ WARNING**: `nointegritychecks` disables important security features. Only use temporarily for debugging specific issues.

### Enable Test Signing (Test VM)

Same steps as above. Run on your test machine/VM.

### Disable Test Signing (When Done Testing)

```powershell
# Disable test signing
bcdedit /set testsigning off

# Re-enable integrity checks (if you disabled them)
bcdedit /set nointegritychecks off

# Reboot
shutdown /r /t 0
```

---

## Creating Test Certificates

### Method 1: PowerShell (Easiest)

```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=YourCompany Driver Test Certificate" `
    -KeySpec Signature `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(5) `
    -CertStoreLocation "Cert:\CurrentUser\My"

# Display certificate thumbprint
Write-Host "Certificate Thumbprint: $($cert.Thumbprint)"

# Export certificate (for distribution to test machines)
$certPath = "C:\certs"
New-Item -ItemType Directory -Path $certPath -Force

Export-Certificate -Cert $cert -FilePath "$certPath\YourEDR-TestCert.cer"

Write-Host "Certificate exported to: $certPath\YourEDR-TestCert.cer"
```

### Method 2: makecert.exe (WDK Tool)

```powershell
# Navigate to WDK bin directory
cd "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"

# Create certificate
.\makecert.exe -r -pe -ss My -n "CN=YourCompany Driver Test" `
    -eku 1.3.6.1.5.5.7.3.3 -len 2048 -h 0 -cy authority `
    -a sha256 -sky signature -sv YourEDR.pvk YourEDR.cer

# Create PFX (for signing)
.\pvk2pfx.exe -pvk YourEDR.pvk -spc YourEDR.cer -pfx YourEDR.pfx -po YourPassword123
```

### Install Certificate to Trusted Root (Required)

**On Development Machine**:

```powershell
# Import to Trusted Root Certification Authorities
$certPath = "C:\certs\YourEDR-TestCert.cer"
Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root"

# Verify installation
Get-ChildItem Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*YourCompany*"}
```

**On Test Machine**:

```powershell
# Copy certificate to test machine
# Then import
Import-Certificate -FilePath "YourEDR-TestCert.cer" -CertStoreLocation "Cert:\LocalMachine\Root"
```

**⚠️ IMPORTANT**: Certificate MUST be in "Trusted Root Certification Authorities" store, not just "Personal" store.

---

## Building and Signing the Driver

### Build the Driver

**Method 1: Visual Studio**

1. Open `WindowsEDR.sln`
2. Set configuration to **Debug** (for development) or **Release** (for testing)
3. Right-click `YourEDRFilter` project → Build
4. Output: `driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys`

**Method 2: Command Line**

```powershell
# Build driver only
msbuild driver\YourEDRFilter\YourEDRFilter.vcxproj `
    /p:Configuration=Debug /p:Platform=x64

# Or build entire solution
msbuild WindowsEDR.sln /p:Configuration=Debug /p:Platform=x64
```

### Sign the Driver

**Option 1: Using PowerShell Script** (Recommended)

```powershell
# Use provided script
.\scripts\sign.ps1 -Configuration Debug

# Or manually specify certificate
.\scripts\sign.ps1 -Configuration Debug -CertThumbprint "YOUR_CERT_THUMBPRINT"
```

**Option 2: Manual Signing**

```powershell
# Get certificate thumbprint
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*YourCompany*"}
$thumbprint = $cert.Thumbprint

# Sign driver
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
$driverPath = "driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys"

& $signtool sign /v /s My /sha1 $thumbprint /fd SHA256 /t http://timestamp.digicert.com $driverPath

# Verify signature
& $signtool verify /v /pa $driverPath
```

**Expected Output**:
```
Successfully signed: YourEDRFilter.sys
Signature verified successfully
```

### Create Catalog File

```powershell
# Navigate to driver directory
cd driver\YourEDRFilter

# Create catalog from INF
$inf2cat = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\inf2cat.exe"
& $inf2cat /driver:. /os:10_X64,10_VB_X64

# Sign catalog
& $signtool sign /v /s My /sha1 $thumbprint /fd SHA256 /t http://timestamp.digicert.com YourEDRFilter.cat
```

---

## Loading and Testing the Driver

### Install the Driver

**Method 1: Using INF** (Recommended)

```powershell
# Open PowerShell as Administrator

# Copy driver to System32\drivers
$driverSource = "driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys"
$driverDest = "C:\Windows\System32\drivers\YourEDRFilter.sys"
Copy-Item $driverSource $driverDest -Force

# Copy INF and CAT
Copy-Item "driver\YourEDRFilter\YourEDRFilter.inf" "C:\Windows\System32\drivers\" -Force
Copy-Item "driver\YourEDRFilter\YourEDRFilter.cat" "C:\Windows\System32\drivers\" -Force

# Install driver using INF
rundll32.exe setupapi.dll,InstallHinfSection DefaultInstall 132 C:\Windows\System32\drivers\YourEDRFilter.inf
```

**Method 2: Using fltmc (Manual)**

```powershell
# Copy driver
Copy-Item "driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys" "C:\Windows\System32\drivers\" -Force

# Load driver
fltmc load YourEDRFilter

# Verify
fltmc filters
# Should show:
# Filter Name       Num Instances    Altitude    Frame
# YourEDRFilter              0        325100        0
```

### Start the Driver

```powershell
# If installed via INF
sc start YourEDRFilter

# Or via fltmc
fltmc load YourEDRFilter

# Check status
sc query YourEDRFilter
fltmc filters
```

### Verify Driver is Loaded

```powershell
# Method 1: fltmc
fltmc filters
# Look for YourEDRFilter in list

# Method 2: driverquery
driverquery /v | findstr YourEDR

# Method 3: PowerShell
Get-Service | Where-Object {$_.Name -like "*YourEDR*"}
```

### View Driver Debug Output

**Option 1: DebugView** (Real-Time)

```powershell
# Download DebugView from Sysinternals
# https://learn.microsoft.com/en-us/sysinternals/downloads/debugview

# Run as Administrator
# Capture → Capture Kernel
# Edit → Filter/Highlight → Enter "YourEDR"

# In driver code, use:
# KdPrint(("YourEDR: Message here\n"));
```

**Option 2: WinDbg (Kernel Debugging)**

See [Kernel Debugging Setup](#kernel-debugging-setup) section below.

---

## Kernel Debugging Setup

### Local Kernel Debugging (Hyper-V VM)

#### Host Machine Setup

```powershell
# Enable Hyper-V (if not already)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Create VM
New-VM -Name "EDR-Test-01" `
    -MemoryStartupBytes 4GB `
    -Generation 2 `
    -NewVHDPath "C:\VMs\EDR-Test-01.vhdx" `
    -NewVHDSizeBytes 60GB

# Configure COM port for debugging
Set-VMComPort -VMName "EDR-Test-01" -Number 1 -Path "\\.\pipe\edr-debug"

# Install Windows on VM (use ISO)
Set-VMDvdDrive -VMName "EDR-Test-01" -Path "C:\ISOs\Windows10.iso"
Start-VM -Name "EDR-Test-01"
```

#### Guest VM Setup (Inside VM)

```powershell
# Enable kernel debugging
bcdedit /debug on
bcdedit /dbgsettings serial debugport:1 baudrate:115200

# Enable test signing
bcdedit /set testsigning on

# Reboot
shutdown /r /t 0
```

#### Start Debugging from Host

```powershell
# Launch WinDbg
windbgx -k com:pipe,port=\\.\pipe\edr-debug,resets=0,reconnect

# Or use classic WinDbg
windbg -k com:pipe,port=\\.\pipe\edr-debug,resets=0,reconnect
```

### Network Kernel Debugging (Physical Machine)

#### Target Machine (Test Machine)

```powershell
# Configure network debugging
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.1.100 port:50000 key:1.2.3.4.5.6.7.8

# Enable test signing
bcdedit /set testsigning on

# Reboot
shutdown /r /t 0
```

#### Debugger Machine (Development Machine)

```powershell
# Launch WinDbg
windbgx -k net:port=50000,key=1.2.3.4.5.6.7.8

# Wait for target to boot and connect
```

### WinDbg Commands for Driver Debugging

```
// Load symbols
.sympath SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols
.reload

// List all drivers
lm

// Find your driver
lm v m YourEDRFilter

// Set breakpoint
bp YourEDRFilter!DriverEntry

// Set breakpoint in PreCreate
bp YourEDRFilter!PreCreateOperation

// Continue execution
g

// When breakpoint hit:
// View stack
k

// View local variables
dv

// Step over
p

// Step into
t

// List filter drivers
!fltkd.filters

// View your filter details
!fltkd.filter <address>

// View filter instances
!fltkd.instances <address>

// View filter volumes
!fltkd.volumes
```

---

## Testing Workflows

### Test 1: Verify Driver Loads

```powershell
# Load driver
fltmc load YourEDRFilter

# Check if loaded
fltmc filters | findstr YourEDR

# Expected output:
# YourEDRFilter              0        325100        0

# Unload driver
fltmc unload YourEDRFilter
```

**✅ Success Criteria**: Driver loads without error, appears in filter list.

### Test 2: Basic File Monitoring

```powershell
# Ensure driver is loaded
fltmc filters | findstr YourEDR

# Create test file
New-Item -ItemType File -Path "C:\test.txt" -Value "Test content"

# Check debug output in DebugView
# Should see: "YourEDR: PreCreate called for C:\test.txt"

# Modify file
Add-Content -Path "C:\test.txt" -Value "More content"

# Check debug output
# Should see: "YourEDR: PreWrite called for C:\test.txt"

# Delete file
Remove-Item "C:\test.txt"

# Check debug output
# Should see: "YourEDR: PreSetInformation called for C:\test.txt"
```

**✅ Success Criteria**: Debug messages appear for file operations.

### Test 3: User-Mode Service Communication

```powershell
# Start service
sc start YourEDRService

# Check service status
sc query YourEDRService

# Generate file activity
1..100 | ForEach-Object {
    New-Item "C:\temp\test_$_.txt" -ItemType File -Value "Test"
    Remove-Item "C:\temp\test_$_.txt"
}

# Check JSON logs
Get-Content "C:\ProgramData\YourEDR\Logs\events_*.jsonl" | ConvertFrom-Json | Select-Object -First 10

# Expected output: JSON events for file operations
```

**✅ Success Criteria**: Events appear in JSON log files.

### Test 4: Process Monitoring

```powershell
# Start notepad (test process creation)
Start-Process notepad.exe

# Check JSON logs
Get-Content "C:\ProgramData\YourEDR\Logs\events_*.jsonl" -Tail 5 | ConvertFrom-Json | Where-Object {$_.event_type -eq "process_create"}

# Should show:
# {
#   "event_type": "process_create",
#   "process_id": 12345,
#   "parent_process_id": 67890,
#   "image_path": "C:\\Windows\\System32\\notepad.exe",
#   "command_line": "notepad.exe",
#   ...
# }

# Kill process
Stop-Process -Name notepad

# Check for process_exit event
Get-Content "C:\ProgramData\YourEDR\Logs\events_*.jsonl" -Tail 1 | ConvertFrom-Json
```

**✅ Success Criteria**: Process creation and exit events logged.

### Test 5: Log Rotation

```powershell
# Generate large volume of events
1..10000 | ForEach-Object {
    New-Item "C:\temp\test_$_.txt" -ItemType File
    Remove-Item "C:\temp\test_$_.txt"
}

# Check log files
Get-ChildItem "C:\ProgramData\YourEDR\Logs\" | Select-Object Name, Length

# Should see multiple files if rotation occurred:
# events_20250119_120000.jsonl (100MB)
# events_20250119_120100.jsonl (current)
```

**✅ Success Criteria**: Log files rotate at 100MB.

### Test 6: Performance Testing

```powershell
# Monitor CPU usage
$process = Get-Process YourEDRService
$cpu = (Get-Counter "\Process(YourEDRService)\% Processor Time").CounterSamples.CookedValue

Write-Host "CPU Usage: $cpu%"

# Should be < 3% under normal load
# Should be < 5% under stress load

# Monitor memory
Write-Host "Memory (MB): $($process.WorkingSet64 / 1MB)"

# Should be < 200MB
```

**✅ Success Criteria**: CPU < 3%, Memory < 200MB.

### Test 7: Driver Verifier (Stability)

```powershell
# Enable Driver Verifier
verifier /standard /driver YourEDRFilter.sys

# Reboot
shutdown /r /t 0

# Run stress tests (after reboot)
.\tests\stress\stress_test.ps1 -Duration 1 -Threads 10

# Check for any bugchecks (should be none)
# Review C:\Windows\Minidump\ (should be empty)

# Disable Driver Verifier (after testing)
verifier /reset
shutdown /r /t 0
```

**✅ Success Criteria**: No crashes during 1-hour stress test with Verifier enabled.

---

## Troubleshooting

### Issue 1: "Driver signature cannot be verified"

**Cause**: Test signing not enabled or certificate not in Trusted Root.

**Solution**:
```powershell
# Check test signing
bcdedit | findstr testsigning
# Should show: testsigning             Yes

# If not enabled:
bcdedit /set testsigning on
shutdown /r /t 0

# Check certificate is in Trusted Root
Get-ChildItem Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*YourCompany*"}

# If not found, import:
Import-Certificate -FilePath "YourEDR-TestCert.cer" -CertStoreLocation "Cert:\LocalMachine\Root"
```

### Issue 2: "The system cannot find the file specified" (fltmc load)

**Cause**: Driver not in System32\drivers or wrong name.

**Solution**:
```powershell
# Verify driver exists
Test-Path "C:\Windows\System32\drivers\YourEDRFilter.sys"

# Check file name matches INF
Get-Content "driver\YourEDRFilter\YourEDRFilter.inf" | Select-String "ServiceBinary"
# Should show: ServiceBinary  = %12%\YourEDRFilter.sys

# Ensure exact name match (case-sensitive)
```

### Issue 3: Driver loads but no events captured

**Cause**: Callbacks not registered or service not connected.

**Solution**:
```powershell
# Check if filter attached to volumes
fltmc instances

# Should show YourEDRFilter attached to C:, D:, etc.

# Check service is running
sc query YourEDRService

# If not running:
sc start YourEDRService

# Check debug output
# Open DebugView as Administrator
# Capture -> Capture Kernel
# Should see: "YourEDR: DriverEntry completed successfully"
```

### Issue 4: BSOD (Blue Screen of Death)

**Cause**: Bug in kernel code (memory corruption, invalid pointer, etc.).

**Solution**:
```powershell
# Analyze crash dump
# Copy C:\Windows\Minidump\*.dmp to development machine

# Open in WinDbg
windbgx -z "path\to\MEMORY.DMP"

# Analyze
!analyze -v

# Look for your driver in stack trace
kv

# Common causes:
# - Dereferencing NULL pointer
# - Accessing invalid memory
# - IRQL violations
# - Memory leaks

# Fix identified bug, rebuild, re-sign, reload
```

### Issue 5: "Access Denied" when loading driver

**Cause**: Not running as Administrator.

**Solution**:
```powershell
# Always use Administrator PowerShell
# Right-click PowerShell -> Run as Administrator

# Verify elevation
[Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'
# Should return: True
```

### Issue 6: JSON logs have invalid format

**Cause**: Service JSON serialization bug.

**Solution**:
```powershell
# Test JSON parsing
Get-Content "C:\ProgramData\YourEDR\Logs\events_*.jsonl" | ForEach-Object {
    try {
        $_ | ConvertFrom-Json | Out-Null
    } catch {
        Write-Host "Invalid JSON: $_"
        Write-Host "Error: $($_.Exception.Message)"
    }
}

# Fix serialization bug in service code
# Rebuild service
msbuild service\YourEDRService\YourEDRService.vcxproj /t:Rebuild

# Restart service
sc stop YourEDRService
sc start YourEDRService
```

### Issue 7: "Test Mode" watermark annoys me

**Cause**: Test signing enabled (required for development).

**Solution**:
```powershell
# Option 1: Remove watermark with third-party tool (NOT RECOMMENDED)
# Option 2: Accept watermark during development
# Option 3: Use a separate test VM (watermark only on VM)
# Option 4: Get EV certificate for production release
```

---

## Production Deployment (Post-Development)

Once development is complete and you're ready for production:

1. **Obtain EV Code Signing Certificate**:
   - Purchase from DigiCert, Sectigo, etc. ($300-500/year)
   - Register with Hardware Dev Center

2. **Run WHQL Tests**:
   - Install HLK (Hardware Lab Kit)
   - Run all filter driver tests
   - Fix any failures

3. **Submit to Microsoft**:
   - Create HLK package (.hlkx)
   - Upload to Hardware Dev Center
   - Wait 2-5 business days for approval

4. **Receive Signed Driver**:
   - Download Microsoft-signed driver
   - Can now deploy to production without test signing

5. **Deploy to Production**:
   - Users do NOT need test signing enabled
   - Driver will load on standard Windows installations
   - MSI installer handles all deployment

---

## Summary

This guide covered:

✅ Enabling test signing mode for development
✅ Creating and installing test certificates
✅ Building and signing your driver
✅ Loading and testing the driver without Microsoft signing
✅ Setting up kernel debugging (local and network)
✅ Comprehensive testing workflows
✅ Troubleshooting common issues

**Key Takeaways**:
- Test signing allows development without EV certificate
- Always test on separate machine/VM (not your main PC)
- Use Driver Verifier for stability testing
- Read debug output in DebugView or WinDbg
- Production deployment requires EV certificate and WHQL

**Next Steps**:
1. Set up your test environment following this guide
2. Build the driver and service
3. Run through all test workflows
4. Start implementing Phase 1 features

**Need Help?** Check [Troubleshooting](#troubleshooting) section or review [Caveats & Best Practices](05-caveats-challenges-best-practices.md).
