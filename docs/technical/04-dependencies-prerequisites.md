# Windows EDR System - Dependencies, Prerequisites & Development Environment

## Document Overview

This document provides a comprehensive guide to all dependencies, prerequisites, tools, and development environment setup required for building a production-grade Windows EDR system with kernel mini-filter drivers.

---

## 1. Development Environment Requirements

### 1.1 Hardware Requirements

#### Development Workstation
- **CPU**: Intel/AMD x64 processor with VT-x/AMD-V support (for Hyper-V)
- **RAM**: Minimum 16 GB (32 GB recommended for running VMs)
- **Storage**:
  - 100 GB free SSD space (OS + tools)
  - 200 GB additional for VMs and symbols
- **Network**: Stable internet connection for symbol server access

#### Test Machines (Physical or Virtual)
- **VM Option**: 2-4 Hyper-V or VMware VMs
  - 4 GB RAM per VM minimum
  - 60 GB disk per VM
- **Physical Option**: Dedicated test machines for hardware-specific testing
  - Required for boot-start drivers (ELAM)
  - Needed for performance benchmarking

### 1.2 Operating System Requirements

#### Development Host
- **OS**: Windows 10/11 Pro/Enterprise (64-bit) or Windows Server 2019/2022
- **Version**: Build 19041 or later (20H1+)
- **Features Required**:
  - Hyper-V (for kernel debugging)
  - WSL 2 (optional, for Linux tools)
  - Developer Mode enabled

#### Target Test Systems
- Windows 10 (1809+), Windows 11 (all versions)
- Windows Server 2016, 2019, 2022
- Both x64 architectures (ARM64 not covered in Phase 1)

---

## 2. Software Dependencies

### 2.1 Core Development Tools

#### Visual Studio 2022 (Required)
- **Edition**: Enterprise, Professional, or Community
- **Version**: 17.4 or later
- **Workloads**:
  - Desktop development with C++
  - .NET desktop development (for management tools)
- **Individual Components**:
  - MSVC v143 (latest)
  - C++ ATL for latest v143 build tools
  - C++ MFC for latest v143 build tools
  - C++ Clang tools for Windows
  - C++/CLI support for v143 build tools
  - Windows 11 SDK (10.0.22621.0 or later)

**Installation:**
```powershell
# Using Visual Studio Installer CLI
vs_enterprise.exe --add Microsoft.VisualStudio.Workload.NativeDesktop `
                  --add Microsoft.VisualStudio.Workload.ManagedDesktop `
                  --add Microsoft.VisualStudio.Component.Windows11SDK.22621 `
                  --includeRecommended
```

#### Windows Driver Kit (WDK) 11 (Required)
- **Version**: Build 22621 or later
- **Components**:
  - WDK Build Environment
  - WDK Test Infrastructure
  - WDK Documentation
  - Debugging Tools for Windows (WinDbg)
- **Download**: https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk

**Installation:**
```powershell
# Install WDK (requires matching Windows SDK version)
# Download from Microsoft and run installer
wdksetup.exe /features + /ceip off
```

**Post-Install Verification:**
```powershell
# Verify WDK installation
Get-Item "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\inf2cat.exe"
Get-Item "C:\Program Files (x86)\Windows Kits\10\Include\*\km\wdm.h"
```

#### Windows SDK (Required)
- **Version**: 10.0.22621.0 or later (must match WDK version)
- **Components**:
  - Windows SDK for Desktop C++ x64
  - Windows SDK Debugging Tools
  - Windows SDK for UWP Managed Apps (optional)

### 2.2 Debugging & Analysis Tools

#### WinDbg Preview (Required)
- **Source**: Microsoft Store or Windows SDK
- **Version**: Latest (1.2306.x or newer)
- **Purpose**:
  - Kernel debugging (live and crash dumps)
  - Driver analysis
  - Memory leak detection

**Installation:**
```powershell
# Install from Microsoft Store
winget install Microsoft.WinDbg
```

**Configuration:**
```powershell
# Set symbol path (critical for debugging)
setx _NT_SYMBOL_PATH "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols"

# Set source path
setx _NT_SOURCE_PATH "C:\src\YourEDR"
```

#### Driver Verifier (Built-in)
- **Purpose**:
  - Detect driver bugs (memory leaks, buffer overruns)
  - Stress testing
  - I/O verification
- **Usage**:
```powershell
# Enable verifier for your driver
verifier /standard /driver YourEDRFilter.sys

# Check verifier status
verifier /query

# Disable after testing
verifier /reset
```

#### Application Verifier (Optional but Recommended)
- **Download**: Windows SDK
- **Purpose**: User-mode service testing
- **Checks**: Heap corruption, handle leaks, thread issues

#### Performance Analyzer (WPA/WPR)
- **Source**: Windows Performance Toolkit (part of SDK)
- **Purpose**:
  - Performance profiling
  - CPU/memory analysis
  - I/O patterns
- **Files**:
  - wpr.exe (Windows Performance Recorder)
  - wpa.exe (Windows Performance Analyzer)

### 2.3 Build & Packaging Tools

#### MSBuild (Included with Visual Studio)
- **Version**: 17.4 or later
- **Purpose**: Build automation for driver and service

#### NuGet (Package Manager)
- **Version**: 6.0 or later
- **Purpose**: Manage C++ dependencies (JSON libraries, etc.)

#### Inf2Cat (WDK Tool)
- **Purpose**: Create catalog files for driver signing
- **Location**: `$(WindowsSdkDir)\bin\$(WindowsSDKVersion)\x64\inf2cat.exe`

#### SignTool (SDK Tool)
- **Purpose**: Sign drivers and executables
- **Location**: `$(WindowsSdkDir)\bin\$(WindowsSDKVersion)\x64\signtool.exe`

#### WiX Toolset (Optional - for MSI packaging)
- **Version**: 3.11 or later
- **Download**: https://wixtoolset.org/
- **Purpose**: Create Windows Installer packages

**Installation:**
```powershell
winget install WiXToolset.WiX
```

### 2.4 Source Control & Collaboration

#### Git (Required)
- **Version**: 2.40 or later
- **Client Options**:
  - Git for Windows (command-line)
  - GitHub Desktop
  - Visual Studio Git integration

**Configuration:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
git config --global core.autocrlf true
git config --global core.longpaths true
```

#### GitHub / Azure DevOps (Repository Hosting)
- **Purpose**: Source control, CI/CD, issue tracking
- **Integration**: Visual Studio Team Explorer

---

## 3. Libraries & Frameworks

### 3.1 Kernel-Mode Libraries (WDK Provided)

#### Filter Manager (FltMgr.lib)
- **Purpose**: Mini-filter driver framework
- **Header**: `fltKernel.h`
- **Link**: Automatically linked via WDK

#### Windows Filtering Platform (WFP)
- **Libraries**: `fwpkclnt.lib`, `uuid.lib`
- **Headers**: `fwpsk.h`, `fwpmk.h`
- **Purpose**: Network monitoring callouts

#### NT Kernel (ntoskrnl.lib)
- **Purpose**: Core kernel functions
- **Headers**: `ntddk.h`, `wdm.h`, `ntifs.h`

**Example Driver Project Configuration (vcxproj):**
```xml
<ItemDefinitionGroup>
  <ClCompile>
    <AdditionalIncludeDirectories>
      $(DDK_INC_PATH);
      $(SDK_INC_PATH)
    </AdditionalIncludeDirectories>
  </ClCompile>
  <Link>
    <AdditionalDependencies>
      $(DDK_LIB_PATH)\fltMgr.lib;
      $(DDK_LIB_PATH)\ksecdd.lib;
      $(DDK_LIB_PATH)\fwpkclnt.lib;
      %(AdditionalDependencies)
    </AdditionalDependencies>
  </Link>
</ItemDefinitionGroup>
```

### 3.2 User-Mode Libraries

#### JSON Processing

**Option 1: nlohmann/json (Recommended)**
- **Version**: 3.11.2 or later
- **License**: MIT
- **Installation via vcpkg**:
```powershell
vcpkg install nlohmann-json:x64-windows
```
- **Usage**: Header-only, modern C++ interface

**Option 2: RapidJSON**
- **Version**: 1.1.0
- **License**: MIT
- **Installation**:
```powershell
vcpkg install rapidjson:x64-windows
```

**vcpkg Setup:**
```powershell
# Install vcpkg (C++ package manager)
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install

# Install packages
.\vcpkg install nlohmann-json:x64-windows spdlog:x64-windows
```

#### Logging (User-Mode Service)

**spdlog (Recommended)**
- **Version**: 1.12.0 or later
- **Purpose**: Fast C++ logging library
- **Installation**:
```powershell
vcpkg install spdlog:x64-windows
```

#### Compression (Optional - for log compression)

**zlib**
- **Installation**:
```powershell
vcpkg install zlib:x64-windows
```

#### Windows-Specific Libraries (System Provided)

| Library | Purpose | Header | Link |
|---------|---------|--------|------|
| FltLib.lib | Filter Manager user-mode API | FltUser.h | Automatic |
| Advapi32.lib | Registry, services | Windows.h | Automatic |
| Ws2_32.lib | Winsock (if needed) | WinSock2.h | Automatic |
| Kernel32.lib | Core Win32 APIs | Windows.h | Automatic |

---

## 4. Driver Signing Prerequisites

### 4.1 Development & Testing Phase

#### Test Signing Mode (Initial Development)
- **Purpose**: Load unsigned drivers on test machines
- **Enable**:
```powershell
# Enable test signing (requires reboot)
bcdedit /set testsigning on
shutdown /r /t 0
```

#### Self-Signed Certificate (Local Testing)
```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=YourCompany Driver Test" `
    -KeySpec Signature `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(3) `
    -CertStoreLocation "Cert:\CurrentUser\My"

# Export for signing
Export-Certificate -Cert $cert -FilePath "C:\certs\test-driver.cer"

# Install to trusted root (test machine only!)
Import-Certificate -FilePath "C:\certs\test-driver.cer" -CertStoreLocation "Cert:\LocalMachine\Root"
```

#### Signing Driver with Test Certificate
```powershell
# Sign driver file
$certPath = "Cert:\CurrentUser\My\<thumbprint>"
$timestampServer = "http://timestamp.digicert.com"

Set-AuthenticodeSignature -FilePath "YourEDRFilter.sys" `
    -Certificate $certPath `
    -TimestampServer $timestampServer `
    -HashAlgorithm SHA256
```

### 4.2 Production Release Phase

#### EV Code Signing Certificate (Required for Production)
- **Provider**: DigiCert, Sectigo, GlobalSign, etc.
- **Type**: Extended Validation (EV) Code Signing
- **Cost**: $300-$500/year
- **Delivery**: USB token or HSM
- **Timeline**: 1-3 weeks for validation

**Requirements for EV Certificate:**
- Registered business entity (D-U-N-S number)
- Business verification documents
- Identity verification of authorized signer
- Physical address verification

#### Windows Hardware Dev Center Portal
- **URL**: https://partner.microsoft.com/en-us/dashboard/hardware
- **Requirements**:
  - EV Code Signing Certificate registered with portal
  - Company account ($99 annual fee)
- **Purpose**:
  - Driver attestation signing
  - WHQL certification
  - Windows Update distribution

**Driver Submission Process:**
1. Test driver with HLK (Hardware Lab Kit)
2. Generate HLK test logs
3. Create driver submission package (.hlkx)
4. Upload to Hardware Dev Center
5. Microsoft reviews and signs (2-5 business days)
6. Download signed driver

#### Hardware Lab Kit (HLK) - For WHQL
- **Version**: HLK for Windows 11 (version 2306 or later)
- **Components**:
  - HLK Studio (test controller)
  - HLK Client (test target machines)
- **Download**: https://learn.microsoft.com/en-us/windows-hardware/test/hlk/
- **Tests Required**:
  - Filter driver verification
  - Installation tests
  - Stress tests
  - Security tests

**HLK Setup:**
- Controller: Windows Server 2019/2022 (can be VM)
- Clients: Windows 10/11 test machines (physical recommended)
- Network: All machines on same subnet

---

## 5. Runtime Dependencies (Deployment)

### 5.1 Target System Requirements

#### Operating System
- **Minimum**: Windows 10 version 1809 (build 17763)
- **Recommended**: Windows 10 21H2+ or Windows 11
- **Server**: Windows Server 2016+ (full or core)

#### System Services
- **Filter Manager Service** (FltMgr): Built-in, always running
- **Base Filtering Engine** (BFE): Required for WFP, auto-start
- **Windows Management Instrumentation** (WMI): For configuration

#### Kernel Components
- **FltMgr.sys**: Filter Manager driver (inbox)
- **netio.sys**: Network I/O platform (for WFP)
- **FWPM.sys**: WFP management (inbox)

#### Visual C++ Redistributable (for User-Mode Service)
- **Version**: Visual C++ 2022 Redistributable (x64)
- **Download**: https://aka.ms/vs/17/release/vc_redist.x64.exe
- **Installation**:
```powershell
# Silent install
vc_redist.x64.exe /install /quiet /norestart
```

#### .NET Runtime (If Using C# for Service)
- **Version**: .NET 6.0+ Runtime (or .NET 8.0)
- **Download**: https://dotnet.microsoft.com/download/dotnet
- **Installation**:
```powershell
winget install Microsoft.DotNet.Runtime.6
```

### 5.2 File System Requirements
- **Installation Path**: `C:\Program Files\YourEDR\`
- **Log Path**: `C:\ProgramData\YourEDR\Logs\`
- **Config Path**: `C:\ProgramData\YourEDR\Config\`
- **Permissions**:
  - Admins: Full Control
  - SYSTEM: Full Control
  - Users: Read & Execute

### 5.3 Registry Requirements
- **Configuration Key**: `HKLM\SOFTWARE\YourEDR`
- **Service Key**: `HKLM\SYSTEM\CurrentControlSet\Services\YourEDRFilter`
- **Permissions**: Protected (Administrators + SYSTEM only)

---

## 6. Development Environment Setup Checklist

### 6.1 Initial Setup (Step-by-Step)

#### Step 1: Install Visual Studio 2022
```powershell
# Download and install VS2022 with required workloads
# Ensure "Desktop development with C++" is selected
# Install Windows 11 SDK (10.0.22621.0)
```

#### Step 2: Install WDK 11
```powershell
# Download from Microsoft
# https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk
# Install with all components
```

#### Step 3: Install WinDbg Preview
```powershell
winget install Microsoft.WinDbg
```

#### Step 4: Configure Symbol Server
```powershell
# Set environment variables
[System.Environment]::SetEnvironmentVariable(
    "_NT_SYMBOL_PATH",
    "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols",
    [System.EnvironmentVariableTarget]::Machine
)
```

#### Step 5: Install vcpkg & Dependencies
```powershell
# Clone vcpkg
git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
cd C:\vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install

# Install libraries
.\vcpkg install nlohmann-json:x64-windows spdlog:x64-windows
```

#### Step 6: Enable Test Signing (Test Machines Only)
```powershell
bcdedit /set testsigning on
bcdedit /set nointegritychecks on  # Use with caution!
shutdown /r /t 0
```

#### Step 7: Create Test Certificate
```powershell
# Run the self-signed certificate creation script from section 4.1
```

#### Step 8: Setup Hyper-V for Kernel Debugging
```powershell
# Enable Hyper-V feature
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Create VM for testing (PowerShell script)
New-VM -Name "EDR-Test-01" -MemoryStartupBytes 4GB -Generation 2 `
    -NewVHDPath "C:\VMs\EDR-Test-01.vhdx" -NewVHDSizeBytes 60GB

# Configure network debugging
Set-VMComPort -VMName "EDR-Test-01" -Number 1 -Path \\.\pipe\edr-debug

# On VM (after OS install):
bcdedit /debug on
bcdedit /dbgsettings serial debugport:1 baudrate:115200
```

#### Step 9: Clone Repository & Build
```bash
git clone https://github.com/yourcompany/windows-edr.git C:\src\YourEDR
cd C:\src\YourEDR

# Open solution
start YourEDR.sln
```

#### Step 10: Verify Build Environment
```powershell
# Run verification script
.\scripts\verify-environment.ps1
```

### 6.2 Verification Script

```powershell
# verify-environment.ps1
$checks = @{
    "Visual Studio 2022" = "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe"
    "WDK 11" = "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\inf2cat.exe"
    "WinDbg" = "C:\Program Files\WindowsApps\Microsoft.WinDbg_*\DbgX.Shell.exe"
    "vcpkg" = "C:\vcpkg\vcpkg.exe"
}

Write-Host "=== Environment Verification ===" -ForegroundColor Cyan

foreach ($check in $checks.GetEnumerator()) {
    $exists = Test-Path $check.Value
    $status = if ($exists) { "✓ OK" } else { "✗ MISSING" }
    $color = if ($exists) { "Green" } else { "Red" }

    Write-Host "$($check.Key): " -NoNewline
    Write-Host $status -ForegroundColor $color
}

# Check symbol path
$symbolPath = [System.Environment]::GetEnvironmentVariable("_NT_SYMBOL_PATH", "Machine")
if ($symbolPath) {
    Write-Host "_NT_SYMBOL_PATH: ✓ Configured" -ForegroundColor Green
} else {
    Write-Host "_NT_SYMBOL_PATH: ✗ Not configured" -ForegroundColor Red
}

# Check test signing
$testSigning = bcdedit /enum | Select-String "testsigning"
if ($testSigning -match "Yes") {
    Write-Host "Test Signing: ✓ Enabled" -ForegroundColor Green
} else {
    Write-Host "Test Signing: ✗ Disabled" -ForegroundColor Yellow
}
```

---

## 7. Optional Tools & Utilities

### 7.1 Static Analysis
- **PREfast (Built into WDK)**: Code analysis for drivers
- **CodeQL (GitHub)**: Security vulnerability scanning
- **Coverity (Commercial)**: Advanced static analysis

### 7.2 Documentation
- **Doxygen**: Generate API documentation from code
- **Markdown editors**: Typora, VS Code with Markdown extension

### 7.3 Monitoring & Profiling
- **Process Monitor (Sysinternals)**: File/registry/network activity
- **Process Explorer (Sysinternals)**: Process tree and handles
- **DebugView (Sysinternals)**: Capture DbgPrint output

**Installation:**
```powershell
# Install Sysinternals Suite
winget install Microsoft.Sysinternals
```

### 7.4 Network Analysis
- **Wireshark**: Packet capture and analysis
- **Fiddler**: HTTP/HTTPS proxy and debugger (for future cloud integration)

---

## 8. Cost Summary

### 8.1 One-Time Costs

| Item | Cost | Notes |
|------|------|-------|
| Visual Studio Enterprise | $5,999/year | Professional: $499/year, Community: Free |
| EV Code Signing Certificate | $300-500/year | Required for production |
| Hardware Dev Center Account | $99 one-time | Required for driver signing |
| HLK Test Lab Setup | $2,000-5,000 | Physical machines or VMs |

### 8.2 Recurring Costs

| Item | Annual Cost | Notes |
|------|------------|-------|
| EV Certificate Renewal | $300-500 | Annual |
| Visual Studio Subscription | $0-5,999 | Depends on edition |
| Azure DevOps (optional) | $0-1,000+ | Depends on users/features |

### 8.3 Minimum Budget for Startup
- **With Community Edition & Self-Signed Testing**: ~$500 (EV cert + HW Dev Center)
- **With Professional Tools**: ~$2,000-3,000 (VS Pro + EV cert + test hardware)
- **With Enterprise Tools**: ~$8,000-10,000 (VS Enterprise + full lab)

---

## 9. Timeline for Environment Setup

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Initial Setup** | 1-2 days | Install VS, WDK, SDK, tools |
| **Certificate Acquisition** | 1-3 weeks | Apply for EV cert, company verification |
| **Test Lab Setup** | 2-5 days | Configure VMs, network debugging |
| **CI/CD Pipeline** | 3-5 days | Azure Pipelines or GitHub Actions |
| **HLK Testing Setup** | 1 week | Install HLK, configure test infrastructure |
| **Total (Parallel Tasks)** | 2-4 weeks | With EV cert as critical path |

---

## 10. Troubleshooting Common Issues

### Issue 1: WDK Build Errors
**Symptom**: "Cannot find wdm.h" or similar
**Solution**:
```powershell
# Verify WDK installation path
Get-Item "C:\Program Files (x86)\Windows Kits\10\Include\*\km\wdm.h"

# In Visual Studio project, check:
# - Configuration Properties -> General -> Platform Toolset = "WindowsKernelModeDriver10.0"
# - C/C++ -> General -> Additional Include Directories = "$(DDK_INC_PATH)"
```

### Issue 2: Driver Won't Load
**Symptom**: "Windows cannot verify the digital signature for this file"
**Solution**:
```powershell
# Enable test signing
bcdedit /set testsigning on

# Check driver signature
Get-AuthenticodeSignature -FilePath "YourEDRFilter.sys"

# Disable driver signature enforcement (temporary, not recommended)
shutdown /r /o /t 0  # Reboot to advanced options
# Select "Disable driver signature enforcement"
```

### Issue 3: Symbol Loading Failures in WinDbg
**Symptom**: "Unable to load symbols" or "No export kernel32!CreateFileW found"
**Solution**:
```
; In WinDbg command window
.sympath SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols
.reload /f

; Verify symbol loading
lm v m ntoskrnl

; Force symbol download
.reload /f /i /v
```

### Issue 4: vcpkg Integration Not Working
**Solution**:
```powershell
# Re-integrate vcpkg with Visual Studio
cd C:\vcpkg
.\vcpkg integrate remove
.\vcpkg integrate install

# Verify integration
.\vcpkg integrate project
```

---

## 11. Additional Resources

### Documentation
- **WDK Documentation**: https://learn.microsoft.com/en-us/windows-hardware/drivers/
- **Mini-Filter Drivers**: https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts
- **WFP Documentation**: https://learn.microsoft.com/en-us/windows/win32/fwp/windows-filtering-platform-start-page
- **Driver Signing**: https://learn.microsoft.com/en-us/windows-hardware/drivers/install/driver-signing

### Community & Support
- **Windows Driver Developers Forum**: https://community.osr.com/
- **Microsoft Q&A (Drivers)**: https://learn.microsoft.com/en-us/answers/topics/windows-hardware-drivers.html
- **Stack Overflow**: Tag `windows-driver-kit`, `minifilter`

### Training Resources
- **Pluralsight**: "Developing Windows Drivers" courses
- **OSR Online**: Windows driver development training (paid)
- **Microsoft Learn**: Free modules on kernel development

---

## Summary

This document covers all dependencies and prerequisites for Windows EDR development. Key requirements:

1. **Development Machine**: Windows 10/11 with 16+ GB RAM
2. **Core Tools**: Visual Studio 2022, WDK 11, WinDbg
3. **Signing**: EV Code Signing Certificate ($300-500/year)
4. **Testing**: Test machines with enabled test signing
5. **Budget**: $500-10,000 depending on tooling choices

**Next Steps**: After environment setup, proceed to implementation following the technical plan (document 02).
