# Windows EDR System - Getting Started Guide

## Document Purpose

This is your starting point for the Windows EDR project. Read this document first before diving into implementation details.

---

## Quick Navigation

### For Developers Starting Today

**Day 1 Checklist**:
1. ✅ Read this document (you are here)
2. ✅ Read [Caveats & Best Practices](05-caveats-challenges-best-practices.md) ⚠️ CRITICAL
3. ✅ Setup environment: [Dependencies & Prerequisites](04-dependencies-prerequisites.md)
4. ✅ Review [High-Level Architecture](../architecture/01-high-level-architecture.md)
5. ✅ Follow [Development & Testing Guide](06-development-testing-guide.md)

**Day 2-3**: Start implementing based on [Implementation Plan](02-implementation-plan.md)

### Documentation Map

```
docs/
├── architecture/           (High-level design and planning)
│   ├── 01-high-level-architecture.md
│   ├── 02-system-components-detail.md
│   ├── 03-security-architecture.md
│   ├── 04-performance-scalability.md
│   ├── 05-deployment-operations.md
│   └── 06-roadmap-phased-plan.md
│
├── technical/             (Implementation details)
│   ├── 01-getting-started.md (you are here)
│   ├── 02-implementation-plan.md
│   ├── 03-component-flow-diagrams.md
│   ├── 04-dependencies-prerequisites.md
│   ├── 05-caveats-challenges-best-practices.md
│   └── 06-development-testing-guide.md
│
└── diagrams/              (Visual architecture)
    ├── 01-high-level-architecture.svg
    ├── 02-data-flow-architecture.svg
    └── 03-deployment-architecture.svg
```

---

## Project Structure Overview

### Final Directory Structure

```
WindowsEDR/                          (Root project directory)
├── README.md                        (Project overview)
├── WindowsEDR.sln                   (Visual Studio solution)
│
├── driver/                          (Kernel-mode driver)
│   ├── YourEDRFilter/
│   │   ├── src/
│   │   │   ├── driver.c
│   │   │   ├── filter_operations.c
│   │   │   ├── communication.c
│   │   │   ├── process_monitor.c
│   │   │   ├── network_monitor.c
│   │   │   ├── event_logger.c
│   │   │   ├── utils.c
│   │   │   └── config.c
│   │   ├── include/
│   │   │   ├── driver.h
│   │   │   ├── event_structures.h
│   │   │   ├── ioctl_codes.h
│   │   │   └── config.h
│   │   ├── resources/
│   │   │   └── YourEDRFilter.rc
│   │   ├── YourEDRFilter.vcxproj
│   │   ├── YourEDRFilter.inf
│   │   └── YourEDRFilter.cat (generated during signing)
│   │
│   └── tests/                       (Driver test suite)
│       └── driver_tests.cpp
│
├── service/                         (User-mode service)
│   ├── YourEDRService/
│   │   ├── src/
│   │   │   ├── main.cpp
│   │   │   ├── service_controller.cpp
│   │   │   ├── driver_communicator.cpp
│   │   │   ├── event_processor.cpp
│   │   │   ├── json_logger.cpp
│   │   │   ├── file_rotator.cpp
│   │   │   ├── config_manager.cpp
│   │   │   └── health_monitor.cpp
│   │   ├── include/
│   │   │   ├── service.h
│   │   │   ├── event_structures.h (shared with driver)
│   │   │   ├── ioctl_codes.h (shared with driver)
│   │   │   └── config.h
│   │   ├── resources/
│   │   │   └── YourEDRService.rc
│   │   ├── YourEDRService.vcxproj
│   │   └── YourEDRService.exe.config
│   │
│   └── tests/                       (Service test suite)
│       └── service_tests.cpp
│
├── common/                          (Shared headers and utilities)
│   ├── include/
│   │   ├── event_structures.h       (Shared event definitions)
│   │   ├── ioctl_codes.h            (Shared IOCTL codes)
│   │   └── common_types.h
│   └── README.md
│
├── management/                      (PowerShell module and CLI)
│   ├── YourEDR.psd1                 (PowerShell manifest)
│   ├── YourEDR.psm1                 (PowerShell module)
│   ├── YourEDR-CLI/
│   │   ├── src/
│   │   │   └── cli.cpp
│   │   ├── YourEDR-CLI.vcxproj
│   │   └── YourEDR-CLI.exe
│   └── tests/
│       └── management_tests.ps1
│
├── installer/                       (MSI packaging)
│   ├── WiX/
│   │   ├── Product.wxs              (Main installer definition)
│   │   ├── Components.wxs           (File components)
│   │   ├── UI.wxs                   (Custom UI dialogs)
│   │   ├── Upgrade.wxs              (Upgrade logic)
│   │   └── YourEDR.wixproj
│   ├── config/
│   │   ├── default_config.json
│   │   └── filter_rules.json
│   ├── scripts/
│   │   ├── install.ps1              (Post-install script)
│   │   ├── uninstall.ps1            (Pre-uninstall script)
│   │   └── upgrade.ps1              (Upgrade script)
│   └── output/
│       └── YourEDR_Installer_v1.0.msi (generated)
│
├── tests/                           (Integration and E2E tests)
│   ├── integration/
│   │   ├── test_file_monitoring.cpp
│   │   ├── test_process_monitoring.cpp
│   │   └── test_network_monitoring.cpp
│   ├── stress/
│   │   ├── stress_test.ps1
│   │   └── load_generator.cpp
│   └── e2e/
│       └── end_to_end_test.ps1
│
├── docs/                            (Documentation - this folder)
│   ├── architecture/
│   ├── technical/
│   ├── diagrams/
│   └── user-guide/                  (End-user documentation)
│       ├── installation.md
│       ├── configuration.md
│       └── troubleshooting.md
│
├── scripts/                         (Build and utility scripts)
│   ├── build.ps1                    (Build all components)
│   ├── sign.ps1                     (Sign driver and binaries)
│   ├── deploy.ps1                   (Deploy to test VM)
│   ├── verify-environment.ps1       (Environment check)
│   └── create-test-cert.ps1         (Generate test certificate)
│
├── config/                          (Configuration templates)
│   ├── default_config.json
│   └── filter_rules.json
│
└── .github/                         (CI/CD)
    └── workflows/
        ├── build.yml                (Build workflow)
        ├── test.yml                 (Test workflow)
        └── release.yml              (Release workflow)
```

---

## Understanding the Numbering

### Architecture Documents (docs/architecture/)

| Doc | Purpose | Audience |
|-----|---------|----------|
| 01 | High-level architecture overview | All stakeholders |
| 02 | System components deep dive | Developers, Architects |
| 03 | Security architecture | Security team, Architects |
| 04 | Performance and scalability | Performance engineers |
| 05 | Deployment and operations | DevOps, IT operations |
| 06 | Roadmap and phased implementation | Project managers |

### Technical Documents (docs/technical/)

| Doc | Purpose | Audience |
|-----|---------|----------|
| 01 | Getting started guide (this doc) | New developers |
| 02 | Implementation plan with code | Developers |
| 03 | Component flow diagrams | Developers, QA |
| 04 | Dependencies and prerequisites | DevOps, Developers |
| 05 | Caveats and best practices | All developers (CRITICAL) |
| 06 | Development and testing guide | Developers, QA |

---

## Phase 1 Implementation Status

### What's Included in This Repository

✅ **Complete Documentation** (all docs you see)
✅ **Starter Code Templates** (driver skeleton, service skeleton)
✅ **Build System** (Visual Studio projects, solution)
✅ **Test Infrastructure** (unit tests, integration tests)
✅ **MSI Packaging** (WiX installer project)
✅ **Development Tools** (scripts for building, signing, deploying)

### What You Need to Complete

Phase 1 focuses on **file system monitoring**:
- [ ] Implement mini-filter callbacks (PreCreate, PreWrite, PreSetInformation)
- [ ] Implement ring buffer for event queuing
- [ ] Implement IOCTL communication
- [ ] Implement user-mode service event retrieval
- [ ] Implement JSON serialization and file writing
- [ ] Implement log rotation
- [ ] Test and verify all functionality

See [Roadmap](../architecture/06-roadmap-phased-plan.md) for detailed sprint breakdown.

---

## Development Workflow

### 1. Initial Setup (First Time)

```powershell
# Clone repository
git clone https://github.com/msaravanan77/learnJava.git
cd learnJava
git checkout claude/windows-edr-architecture-01QVtrrdUP8JwwftmYmQkMK4

# Verify environment
.\scripts\verify-environment.ps1

# Create test certificate (for development)
.\scripts\create-test-cert.ps1

# Open solution in Visual Studio
start WindowsEDR.sln
```

### 2. Daily Development Cycle

```powershell
# Pull latest changes
git pull origin claude/windows-edr-architecture-01QVtrrdUP8JwwftmYmQkMK4

# Build all components
.\scripts\build.ps1 -Configuration Debug

# Deploy to test VM
.\scripts\deploy.ps1 -TargetVM "EDR-Test-01"

# Run tests
.\scripts\run-tests.ps1

# Make changes, test, commit
git add .
git commit -m "Implement feature X"
git push
```

### 3. Testing Workflow

See [Development & Testing Guide](06-development-testing-guide.md) for:
- How to enable test signing on Windows
- How to load unsigned drivers for testing
- How to use WinDbg for kernel debugging
- How to run stress tests
- How to use Driver Verifier

---

## Building the Project

### Option 1: Visual Studio GUI

1. Open `WindowsEDR.sln`
2. Select configuration: **Debug** or **Release**
3. Build → Build Solution (F7)
4. Output: `bin\Debug\` or `bin\Release\`

### Option 2: Command Line (MSBuild)

```powershell
# Debug build
msbuild WindowsEDR.sln /p:Configuration=Debug /p:Platform=x64

# Release build
msbuild WindowsEDR.sln /p:Configuration=Release /p:Platform=x64

# Build only driver
msbuild driver\YourEDRFilter\YourEDRFilter.vcxproj /p:Configuration=Debug

# Build only service
msbuild service\YourEDRService\YourEDRService.vcxproj /p:Configuration=Debug
```

### Option 3: Automated Script

```powershell
# Build all components
.\scripts\build.ps1

# Build with specific configuration
.\scripts\build.ps1 -Configuration Release -Platform x64

# Clean build
.\scripts\build.ps1 -Clean
```

---

## Installing and Testing (Development Mode)

### Prerequisites

1. **Enable Test Signing** (required for unsigned drivers):
   ```powershell
   bcdedit /set testsigning on
   shutdown /r /t 0  # Reboot
   ```

2. **Install Test Certificate** (one-time):
   ```powershell
   .\scripts\create-test-cert.ps1
   # Follow prompts to install to Trusted Root
   ```

### Install Driver and Service

```powershell
# Install all components
.\scripts\install.ps1

# Or manually:
# 1. Copy driver to System32\drivers
copy driver\YourEDRFilter\bin\Debug\YourEDRFilter.sys C:\Windows\System32\drivers\

# 2. Install driver
rundll32.exe setupapi,InstallHinfSection DefaultInstall 132 driver\YourEDRFilter\YourEDRFilter.inf

# 3. Install service
sc create YourEDRService binPath= "C:\Program Files\YourEDR\YourEDRService.exe" start= auto
sc start YourEDRService

# 4. Verify
fltmc filters        # Should show YourEDRFilter
sc query YourEDRService  # Should show RUNNING
```

### View Logs

```powershell
# Check event logs
Get-EventLog -LogName Application -Source YourEDR -Newest 50

# View JSON logs
Get-Content C:\ProgramData\YourEDR\Logs\events_*.jsonl | ConvertFrom-Json

# Real-time monitoring
Get-Content C:\ProgramData\YourEDR\Logs\events_*.jsonl -Wait
```

---

## Creating MSI Installer

### Prerequisites

- WiX Toolset 3.11+ installed
- All binaries built (driver, service, management tools)
- Binaries signed (test certificate or EV certificate)

### Build MSI

```powershell
# Build installer
msbuild installer\WiX\YourEDR.wixproj /p:Configuration=Release

# Output
# installer\output\YourEDR_Installer_v1.0.msi

# Test install
msiexec /i installer\output\YourEDR_Installer_v1.0.msi /l*v install.log

# Test uninstall
msiexec /x installer\output\YourEDR_Installer_v1.0.msi /l*v uninstall.log
```

See `installer/WiX/README.md` for detailed MSI customization options.

---

## Troubleshooting Common Issues

### Driver Won't Load

**Symptom**: `fltmc load YourEDRFilter` fails with error

**Solutions**:
1. Check test signing is enabled: `bcdedit | findstr testsigning`
2. Verify driver signature: `Get-AuthenticodeSignature YourEDRFilter.sys`
3. Check for conflicting filters: `fltmc filters`
4. Review System Event Log for error details
5. Use Driver Verifier: `verifier /query`

### Service Won't Start

**Symptom**: `sc start YourEDRService` fails

**Solutions**:
1. Check dependencies: `sc qc YourEDRService`
2. Verify driver is loaded: `fltmc filters`
3. Check Event Viewer: Application log, source YourEDR
4. Test manually: Run `YourEDRService.exe` from command line
5. Check file permissions on Program Files directory

### No Events Being Logged

**Symptom**: JSON log files are empty or not created

**Solutions**:
1. Verify service is running: `sc query YourEDRService`
2. Check driver is loaded: `fltmc filters`
3. Test file I/O: Create/modify files, check if captured
4. Review filter configuration: `C:\ProgramData\YourEDR\config\filter_rules.json`
5. Enable debug logging: Set registry key `HKLM\SOFTWARE\YourEDR\DebugLevel = 4`

### Build Errors

**Symptom**: Visual Studio build fails

**Solutions**:
1. Verify WDK installed: Check `C:\Program Files (x86)\Windows Kits\10\`
2. Check SDK version matches: Project properties → SDK version
3. Run environment verification: `.\scripts\verify-environment.ps1`
4. Clean and rebuild: `msbuild WindowsEDR.sln /t:Clean,Build`
5. Check for missing dependencies: Restore NuGet packages

---

## Performance Monitoring

### Real-Time Performance

```powershell
# CPU usage
Get-Counter "\Process(YourEDRService)\% Processor Time"

# Memory usage
Get-Process YourEDRService | Select-Object WorkingSet64, PrivateMemorySize64

# Event rate
# Check internal metrics via PowerShell module
Import-Module YourEDR
Get-EDRStatistics
```

### Driver Verifier (Stability Testing)

```powershell
# Enable for your driver
verifier /standard /driver YourEDRFilter.sys

# Check status
verifier /query

# Disable after testing
verifier /reset
```

---

## Next Steps

### Immediate Actions

1. ✅ Complete environment setup: [Dependencies Guide](04-dependencies-prerequisites.md)
2. ✅ Read critical warnings: [Caveats & Best Practices](05-caveats-challenges-best-practices.md)
3. ✅ Follow testing guide: [Development & Testing](06-development-testing-guide.md)
4. ✅ Review implementation plan: [Implementation Plan](02-implementation-plan.md)

### Start Coding

Begin with Sprint 1 from [Roadmap](../architecture/06-roadmap-phased-plan.md):
- Implement `driver.c` (DriverEntry, filter registration)
- Implement `filter_operations.c` (PreCreate callback)
- Test on VM with Driver Verifier enabled

### Get Help

- **Documentation Issues**: Check [High-Level Architecture](../architecture/01-high-level-architecture.md)
- **Build Issues**: Check [Dependencies Guide](04-dependencies-prerequisites.md)
- **Testing Issues**: Check [Development & Testing Guide](06-development-testing-guide.md)
- **Code Issues**: Check [Implementation Plan](02-implementation-plan.md)

---

## Important Notes

⚠️ **CRITICAL**: Always read [Caveats & Best Practices](05-caveats-challenges-best-practices.md) before writing any kernel code. One mistake can cause system crashes.

⚠️ **TEST SIGNING**: Development requires test signing enabled. Production requires EV certificate and WHQL certification.

⚠️ **DRIVER VERIFIER**: Always test with Driver Verifier enabled. It catches bugs that would otherwise cause crashes in production.

⚠️ **BACKUP**: Use virtual machines or test systems. Kernel bugs can make systems unbootable.

---

**Ready to start? Proceed to [Development & Testing Guide](06-development-testing-guide.md)**
