# YourEDR - Build and Test Instructions

## Phase 1 Implementation Status: ✅ COMPLETE

This guide walks you through building, signing, and testing the YourEDR system on your development machine.

---

## 📋 Prerequisites

### Required Software

1. **Windows 10/11 Pro/Enterprise (64-bit)** or **Windows Server 2019/2022**
   - Administrator privileges required
   - Virtualization (Hyper-V) recommended for testing

2. **Visual Studio 2022** (Professional or Enterprise)
   - Workload: "Desktop development with C++"
   - Individual component: "C++ ATL for latest build tools"
   - Download: https://visualstudio.microsoft.com/downloads/

3. **Windows Driver Kit (WDK) 11**
   - Must match your Visual Studio 2022 version
   - Download: https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk

4. **Windows SDK 10.0.22621.0 or newer**
   - Usually installed with WDK
   - Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

5. **WiX Toolset v3.11** (for MSI installer)
   - Download: https://wixtoolset.org/releases/
   - Install: `WiX311.exe` and `WiX311-VS2022.vsix`

6. **PowerShell 5.1 or newer**
   - Included with Windows 10/11

### Hardware Requirements

- **RAM**: 16 GB minimum (32 GB recommended)
- **Storage**: 300 GB free space (SSD recommended)
- **CPU**: Intel VT-x or AMD-V support (for Hyper-V testing)

---

## 🚀 Quick Start Guide

### Step 1: Clone the Repository

```powershell
git clone <repository-url>
cd learnJava
```

### Step 2: Open Solution in Visual Studio

```powershell
# Open the solution
start WindowsEDR.sln
```

**Important**: Right-click the solution and select "Restore NuGet Packages" if prompted.

### Step 3: Build the Project

#### Option A: Command Line (Recommended)

```powershell
# Run the build script
.\scripts\build.ps1 -Configuration Debug

# Or for Release build:
.\scripts\build.ps1 -Configuration Release
```

#### Option B: Visual Studio GUI

1. Set configuration to "Debug" or "Release"
2. Set platform to "x64"
3. Build → Build Solution (Ctrl+Shift+B)

**Expected Output**:
- Driver: `driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys`
- Service: `service\YourEDRService\bin\Debug\YourEDRService.exe`
- MSI: `installer\output\YourEDR_Installer_v1.0.0.msi` (if WiX is installed)

---

## 🔐 Step 4: Code Signing for Testing

Since we don't have a Microsoft-issued certificate yet, we'll use **test signing mode**.

### 4.1 Create Test Certificate

```powershell
# Run as Administrator
.\scripts\create-test-cert.ps1
```

This script will:
- Create a self-signed code signing certificate
- Install it to your certificate stores
- Export it to `installer\assets\YourEDR_TestCert.cer`

### 4.2 Enable Test Signing Mode

⚠️ **WARNING**: This requires a system reboot and reduces system security. Only use on test machines.

```powershell
# Run as Administrator
bcdedit /set testsigning on
shutdown /r /t 0
```

After reboot, you'll see "Test Mode" watermark in the bottom-right corner of your desktop.

### 4.3 Sign the Driver and Service

```powershell
# Run as Administrator
.\scripts\sign.ps1 -Configuration Debug
```

### 4.4 Verify Signatures

```powershell
# Verify driver signature
signtool verify /pa driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys

# Verify service signature
signtool verify /pa service\YourEDRService\bin\Debug\YourEDRService.exe
```

**Expected Output**: "Successfully verified"

---

## 📦 Step 5: Install and Test

### 5.1 Install Locally

```powershell
# Run as Administrator
.\scripts\install-local.ps1 -Configuration Debug
```

This script will:
1. Stop any existing installation
2. Copy driver to `C:\Windows\System32\drivers\`
3. Load the driver using `fltmc`
4. Install the service to `C:\Program Files\YourEDR\`
5. Start the service

### 5.2 Verify Installation

#### Check Driver Status

```powershell
# List loaded mini-filter drivers
fltmc filters | findstr YourEDR
```

**Expected Output**:
```
YourEDRFilter      325100    3    0
```

#### Check Service Status

```powershell
# Query service status
sc query YourEDRService

# Or using PowerShell
Get-Service -Name YourEDRService
```

**Expected Output**: Status = RUNNING

#### Check Logs

```powershell
# View event log files
Get-ChildItem C:\ProgramData\YourEDR\Logs\*.jsonl

# View last 10 events
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl | Select-Object -Last 10
```

---

## 🧪 Step 6: Generate Test Events

### Test File Operations

```powershell
# Create a test file (should generate FileCreate event)
echo "Hello EDR" > C:\test_edr.txt

# Modify the file (should generate FileWrite event)
echo "Testing write" >> C:\test_edr.txt

# Delete the file (should generate FileDelete event)
del C:\test_edr.txt
```

### View Captured Events

```powershell
# View JSON events in real-time
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl -Wait

# Or view last 20 events
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl | Select-Object -Last 20 | ConvertFrom-Json | Format-List
```

**Expected Output**: JSON events with:
- `eventType`: "FileCreate", "FileWrite", "FileDelete"
- `timestamp`: ISO 8601 format
- `processId`: PID of PowerShell
- `filePath`: "C:\test_edr.txt"

---

## 🛠️ Troubleshooting

### Driver Fails to Load

#### Error: "The system cannot find the file specified"

```powershell
# Check if driver file exists
Test-Path C:\Windows\System32\drivers\YourEDRFilter.sys

# If not, copy manually
Copy-Item driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys C:\Windows\System32\drivers\
```

#### Error: "The digital signature for this file couldn't be verified"

```powershell
# Verify test signing is enabled
bcdedit /enum | Select-String testsigning

# Should show: testsigning             Yes

# If not, enable and reboot
bcdedit /set testsigning on
shutdown /r /t 0
```

#### Error: "The specified procedure could not be found"

- Driver dependencies missing
- **Fix**: Install latest Windows SDK and WDK

### Service Fails to Start

#### Check Event Logs

```powershell
# Check system event log for errors
Get-EventLog -LogName System -Source "Service Control Manager" -Newest 10 | Where-Object {$_.Message -like "*YourEDR*"}

# Check application event log
Get-EventLog -LogName Application -Newest 20
```

#### Check Service Configuration

```powershell
# View service details
sc qc YourEDRService

# Expected: START_TYPE = AUTO_START, DEPENDENCIES = YourEDRFilter
```

### No Events Being Logged

#### Verify Driver is Capturing Events

```powershell
# Check driver statistics via DebugView or kernel debugger
# (Requires WinDbg setup - see docs/technical/06-development-testing-guide.md)
```

#### Check Log Directory Permissions

```powershell
# Verify log directory exists and is writable
$LogDir = "C:\ProgramData\YourEDR\Logs"
Test-Path $LogDir
(Get-Acl $LogDir).Access
```

---

## 🔍 Advanced Testing

### Enable Kernel Debugging

For detailed driver debugging, see: [docs/technical/06-development-testing-guide.md](docs/technical/06-development-testing-guide.md)

### Stress Testing

```powershell
# Generate high-volume file operations
1..1000 | ForEach-Object {
    echo "Test $_" > "C:\test_$_.txt"
}

# Check if driver is keeping up
fltmc filters | findstr YourEDR
```

### Performance Monitoring

```powershell
# Monitor CPU usage
Get-Process YourEDRService | Select-Object CPU, WorkingSet

# Monitor driver memory
# (Requires Performance Monitor or WinDbg)
```

---

## 🧹 Uninstallation

### Stop and Uninstall

```powershell
# Stop service
sc stop YourEDRService

# Unload driver
fltmc unload YourEDRFilter

# Uninstall service
& "C:\Program Files\YourEDR\bin\YourEDRService.exe" uninstall

# Delete driver
del C:\Windows\System32\drivers\YourEDRFilter.sys

# Delete service files
rmdir /s "C:\Program Files\YourEDR"

# Delete logs (optional)
rmdir /s "C:\ProgramData\YourEDR"
```

### Disable Test Signing (Optional)

```powershell
# Run as Administrator
bcdedit /set testsigning off
shutdown /r /t 0
```

---

## 📊 MSI Installer Testing

### Build MSI (Requires WiX)

```powershell
# Build MSI installer
.\scripts\build.ps1 -Configuration Release

# MSI output location
$MsiPath = "installer\output\YourEDR_Installer_v1.0.0.msi"
```

### Install via MSI

```powershell
# Install (silent mode)
msiexec /i $MsiPath /qn /l*v install.log

# Or with UI
msiexec /i $MsiPath
```

### Uninstall via MSI

```powershell
# Uninstall (silent mode)
msiexec /x $MsiPath /qn /l*v uninstall.log

# Or via Control Panel
control appwiz.cpl
```

---

## 📚 Additional Resources

- **Getting Started**: [docs/technical/01-getting-started.md](docs/technical/01-getting-started.md)
- **Testing Guide**: [docs/technical/06-development-testing-guide.md](docs/technical/06-development-testing-guide.md)
- **Troubleshooting**: [docs/technical/05-caveats-challenges-best-practices.md](docs/technical/05-caveats-challenges-best-practices.md)
- **Architecture**: [docs/architecture/01-high-level-architecture.md](docs/architecture/01-high-level-architecture.md)

---

## ⚠️ Important Notes

1. **Test Mode Warning**: Test signing mode reduces system security. Only use on isolated test machines.

2. **Driver BSOD Risk**: Kernel drivers can cause Blue Screen of Death (BSOD). Always test in a VM first.

3. **No Production Use**: Phase 1 is for development/testing only. Do NOT use in production.

4. **Performance**: First run may be slow. Performance improves after Windows caches the driver.

5. **Event Volume**: File monitoring generates high event volume. Configure exclusions in `config/default_config.json`.

---

## ✅ Success Criteria

You've successfully set up YourEDR when:

- ✅ Driver loads without errors: `fltmc filters | findstr YourEDR`
- ✅ Service is running: `sc query YourEDRService`
- ✅ JSON log files are created: `ls C:\ProgramData\YourEDR\Logs\`
- ✅ File operations generate events visible in logs
- ✅ No BSODs or system crashes after 30 minutes of testing

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `C:\ProgramData\YourEDR\Logs\`
2. **Event Viewer**: System and Application logs
3. **Review documentation**: See `docs/` directory
4. **Kernel debugging**: Follow [06-development-testing-guide.md](docs/technical/06-development-testing-guide.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-19
**Status**: Phase 1 Complete - Ready for Testing
