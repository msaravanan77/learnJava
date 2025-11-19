# Windows EDR Project - Complete Directory Structure

## Purpose

This document explains the COMPLETE directory structure of the Windows EDR project, clarifying how all pieces fit together for building, packaging, and distributing the product.

---

## Top-Level Structure

```
WindowsEDR/                                    (Project root)
├── README.md                                  (Project overview and navigation)
├── WindowsEDR.sln                             (Visual Studio solution file)
├── LICENSE                                    (License file)
├── .gitignore                                 (Git ignore rules)
│
├── driver/                                    (Kernel-mode components)
├── service/                                   (User-mode service)
├── common/                                    (Shared code between driver and service)
├── management/                                (PowerShell module and CLI tools)
├── installer/                                 (MSI packaging and installation)
├── tests/                                     (Integration and E2E tests)
├── docs/                                      (All documentation)
├── scripts/                                   (Build, deployment, and utility scripts)
├── config/                                    (Configuration file templates)
├── bin/                                       (Build output - Debug/Release)
├── obj/                                       (Intermediate build files)
└── .github/                                   (CI/CD workflows)
```

---

## Detailed Breakdown

### 1. Driver Directory (`driver/`)

**Purpose**: Contains the kernel-mode mini-filter driver and related test code.

```
driver/
├── YourEDRFilter/                            (Main driver project)
│   ├── src/                                  (Source files)
│   │   ├── driver.c                          (DriverEntry, Unload, initialization)
│   │   ├── filter_operations.c               (Pre/Post operation callbacks)
│   │   ├── communication.c                   (IOCTL handler, port management)
│   │   ├── process_monitor.c                 (Process/thread callbacks)
│   │   ├── network_monitor.c                 (WFP callout implementation)
│   │   ├── event_logger.c                    (Ring buffer, event queuing)
│   │   ├── utils.c                           (String, memory helpers)
│   │   └── config.c                          (Configuration management)
│   │
│   ├── include/                              (Header files)
│   │   ├── driver.h                          (Main driver definitions)
│   │   ├── event_structures.h                (Event data structures)
│   │   ├── ioctl_codes.h                     (IOCTL message definitions)
│   │   ├── config.h                          (Configuration structures)
│   │   └── common.h                          (Common macros and types)
│   │
│   ├── resources/                            (Resources)
│   │   └── YourEDRFilter.rc                  (Version information resource)
│   │
│   ├── YourEDRFilter.vcxproj                 (Visual Studio project file)
│   ├── YourEDRFilter.vcxproj.filters         (VS filters for organization)
│   ├── YourEDRFilter.inf                     (Driver installation metadata)
│   ├── YourEDRFilter.cat                     (Catalog file - generated)
│   │
│   ├── bin/                                  (Build output)
│   │   ├── Debug/
│   │   │   ├── YourEDRFilter.sys             (Debug driver binary)
│   │   │   ├── YourEDRFilter.pdb             (Debug symbols)
│   │   │   └── YourEDRFilter.inf
│   │   └── Release/
│   │       ├── YourEDRFilter.sys             (Release driver binary)
│   │       ├── YourEDRFilter.pdb             (Release symbols)
│   │       └── YourEDRFilter.inf
│   │
│   └── obj/                                  (Intermediate files)
│       ├── Debug/
│       └── Release/
│
└── tests/                                     (Driver-specific tests)
    ├── unit/
    │   ├── test_utils.cpp                    (Unit tests for utils.c)
    │   └── test_config.cpp
    └── kernel_tests.vcxproj                  (Test project)
```

**Build Output**: `driver/YourEDRFilter/bin/{Debug|Release}/YourEDRFilter.sys`

---

### 2. Service Directory (`service/`)

**Purpose**: Contains the user-mode Windows service that communicates with the driver.

```
service/
├── YourEDRService/                           (Main service project)
│   ├── src/                                  (Source files)
│   │   ├── main.cpp                          (Service entry point, SCM handlers)
│   │   ├── service_controller.cpp            (Service control logic)
│   │   ├── driver_communicator.cpp           (IOCTL communication with driver)
│   │   ├── event_processor.cpp               (Event deserialization, enrichment)
│   │   ├── json_logger.cpp                   (JSON serialization using nlohmann/json)
│   │   ├── file_rotator.cpp                  (Log rotation and retention)
│   │   ├── config_manager.cpp                (Configuration loading and hot-reload)
│   │   └── health_monitor.cpp                (Watchdog, metrics collection)
│   │
│   ├── include/                              (Header files)
│   │   ├── service.h                         (Service interfaces)
│   │   ├── driver_communicator.h
│   │   ├── event_processor.h
│   │   ├── json_logger.h
│   │   ├── config_manager.h
│   │   └── health_monitor.h
│   │
│   ├── resources/                            (Resources)
│   │   └── YourEDRService.rc                 (Version information)
│   │
│   ├── YourEDRService.vcxproj                (Visual Studio project)
│   ├── YourEDRService.vcxproj.filters
│   ├── YourEDRService.exe.config             (App configuration)
│   ├── packages.config                       (NuGet packages - nlohmann/json, spdlog)
│   │
│   ├── bin/                                  (Build output)
│   │   ├── Debug/
│   │   │   ├── YourEDRService.exe            (Debug service binary)
│   │   │   ├── YourEDRService.pdb
│   │   │   ├── YourEDRService.exe.config
│   │   │   └── *.dll                         (Dependencies: nlohmann, spdlog)
│   │   └── Release/
│   │       ├── YourEDRService.exe            (Release service binary)
│   │       ├── YourEDRService.pdb
│   │       └── *.dll
│   │
│   └── obj/                                  (Intermediate files)
│
└── tests/                                     (Service-specific tests)
    ├── unit/
    │   ├── test_json_logger.cpp
    │   ├── test_file_rotator.cpp
    │   └── test_config_manager.cpp
    ├── mock_driver.cpp                       (Mock driver for testing)
    └── service_tests.vcxproj
```

**Build Output**: `service/YourEDRService/bin/{Debug|Release}/YourEDRService.exe`

---

### 3. Common Directory (`common/`)

**Purpose**: Shared headers and code between driver and service (event structures, IOCTL codes).

```
common/
├── include/
│   ├── event_structures.h                    (SHARED: Event data structures)
│   ├── ioctl_codes.h                         (SHARED: IOCTL message codes)
│   └── common_types.h                        (SHARED: Common types)
│
└── README.md                                  (Usage instructions)
```

**Important**: These headers are symlinked or included in both driver and service projects to ensure consistency.

---

### 4. Management Directory (`management/`)

**Purpose**: PowerShell module and CLI tools for managing the EDR system.

```
management/
├── PowerShell/                               (PowerShell module)
│   ├── YourEDR.psd1                          (Module manifest)
│   ├── YourEDR.psm1                          (Module implementation)
│   ├── Public/
│   │   ├── Get-EDRStatistics.ps1             (Get driver/service stats)
│   │   ├── Set-EDRConfiguration.ps1          (Update configuration)
│   │   ├── Start-EDRService.ps1              (Start service)
│   │   ├── Stop-EDRService.ps1               (Stop service)
│   │   └── Get-EDREvents.ps1                 (Query events)
│   └── Private/
│       └── helpers.ps1                       (Internal helper functions)
│
├── CLI/                                       (C++ CLI tool)
│   ├── src/
│   │   └── cli.cpp                           (Command-line interface)
│   ├── YourEDR-CLI.vcxproj
│   └── bin/
│       ├── Debug/
│       │   └── YourEDR-CLI.exe
│       └── Release/
│           └── YourEDR-CLI.exe
│
└── tests/
    └── management_tests.ps1                  (PowerShell module tests)
```

**Build Output**: `management/CLI/bin/{Debug|Release}/YourEDR-CLI.exe`

---

### 5. Installer Directory (`installer/`)

**Purpose**: MSI packaging using WiX Toolset, including upgrade and update logic.

```
installer/
├── WiX/                                       (WiX source files)
│   ├── Product.wxs                           (Main installer definition)
│   │   // Defines:
│   │   // - Product GUID, version, manufacturer
│   │   // - Install directories
│   │   // - Features (driver, service, management)
│   │   // - Launch conditions
│   │
│   ├── Components.wxs                        (File components)
│   │   // Defines:
│   │   // - Component for driver files
│   │   // - Component for service files
│   │   // - Component for management tools
│   │   // - Component for config files
│   │
│   ├── UI.wxs                                (Custom UI dialogs)
│   │   // Defines:
│   │   // - Welcome dialog
│   │   // - License agreement
│   │   // - Installation progress
│   │   // - Completion dialog
│   │
│   ├── Upgrade.wxs                           (Upgrade logic)
│   │   // Defines:
│   │   // - Upgrade codes
│   │   // - Major upgrade rules
│   │   // - Minor upgrade/patch rules
│   │   // - Downgrade prevention
│   │
│   ├── CustomActions.wxs                     (Custom actions)
│   │   // Defines:
│   │   // - Stop service before uninstall
│   │   // - Unload driver before upgrade
│   │   // - Register filter after install
│   │   // - Clean up logs (optional)
│   │
│   ├── YourEDR.wixproj                       (WiX project file)
│   ├── YourEDR.wxi                           (Include file with variables)
│   └── bin/
│       ├── Debug/
│       │   └── YourEDR_Installer_v1.0.0.msi
│       └── Release/
│           └── YourEDR_Installer_v1.0.0.msi
│
├── config/                                    (Default configuration files)
│   ├── default_config.json                   (Default EDR configuration)
│   │   // Contains:
│   │   // - Log directory path
│   │   // - Rotation settings
│   │   // - Filter rules
│   │   // - Performance tuning
│   │
│   └── filter_rules.json                     (Default filter rules)
│       // Contains:
│       // - Excluded paths
│       // - Excluded processes
│       // - Monitored extensions
│
├── scripts/                                   (Install/uninstall scripts)
│   ├── install.ps1                           (Post-install script)
│   │   // Actions:
│   │   // - Import certificate to Trusted Root
│   │   // - Register filter with FltMgr
│   │   // - Create log directories
│   │   // - Set registry keys
│   │   // - Start service
│   │
│   ├── uninstall.ps1                         (Pre-uninstall script)
│   │   // Actions:
│   │   // - Stop service
│   │   // - Unload driver
│   │   // - Clean up logs (if requested)
│   │   // - Remove registry keys
│   │
│   └── upgrade.ps1                           (Upgrade script)
│       // Actions:
│       // - Detect current version
│       // - Stop service
│       // - Unload old driver
│       // - Install new files
│       // - Load new driver
│       // - Start service
│
├── assets/                                    (Installer assets)
│   ├── banner.bmp                            (Installer banner image)
│   ├── dialog.bmp                            (Installer dialog background)
│   ├── icon.ico                              (Application icon)
│   └── license.rtf                           (License agreement text)
│
└── output/                                    (Final MSI output)
    ├── YourEDR_Installer_v1.0.0.msi          (Installer package)
    ├── YourEDR_Installer_v1.0.0.wixpdb       (Debug symbols for MSI)
    └── logs/
        ├── install.log                       (Installation log)
        └── uninstall.log                     (Uninstallation log)
```

**Final Output**: `installer/output/YourEDR_Installer_v1.0.0.msi`

#### MSI Installation Structure (When Installed)

```
C:\Program Files\YourEDR\                     (Installation directory)
├── YourEDRService.exe
├── YourEDRService.pdb
├── YourEDRService.exe.config
├── nlohmann_json.dll
├── spdlog.dll
├── YourEDR-CLI.exe
└── README.txt

C:\Windows\System32\drivers\                  (Driver location)
├── YourEDRFilter.sys
├── YourEDRFilter.inf
└── YourEDRFilter.cat

C:\Program Files\WindowsPowerShell\Modules\YourEDR\  (PowerShell module)
├── YourEDR.psd1
├── YourEDR.psm1
└── Public/
    └── *.ps1

C:\ProgramData\YourEDR\                       (Data directory)
├── Logs/                                     (Event logs)
│   ├── events_20250119_120000.jsonl
│   └── events_20250119_130000.jsonl
├── Config/                                   (Configuration)
│   ├── config.json
│   └── filter_rules.json
└── Temp/                                     (Temporary files)

HKLM\SOFTWARE\YourEDR\                        (Registry keys)
├── InstallPath                               (REG_SZ: C:\Program Files\YourEDR)
├── Version                                   (REG_SZ: 1.0.0)
├── LogPath                                   (REG_SZ: C:\ProgramData\YourEDR\Logs)
└── DebugLevel                                (REG_DWORD: 2)

HKLM\SYSTEM\CurrentControlSet\Services\       (Service registration)
├── YourEDRFilter\                            (Driver service)
│   ├── Type                                  (REG_DWORD: 2 - FILE_SYSTEM_DRIVER)
│   ├── Start                                 (REG_DWORD: 3 - DEMAND_START)
│   ├── ErrorControl                          (REG_DWORD: 1 - NORMAL)
│   ├── ImagePath                             (System32\drivers\YourEDRFilter.sys)
│   └── Instances\                            (Filter instance configuration)
│       └── YourEDR Instance\
│           ├── Altitude                      (REG_SZ: 325100)
│           └── Flags                         (REG_DWORD: 0)
│
└── YourEDRService\                           (User-mode service)
    ├── Type                                  (REG_DWORD: 16 - WIN32_OWN_PROCESS)
    ├── Start                                 (REG_DWORD: 2 - AUTO_START)
    ├── ErrorControl                          (REG_DWORD: 1 - NORMAL)
    └── ImagePath                             (C:\Program Files\YourEDR\YourEDRService.exe)
```

---

### 6. Upgrade/Update Mechanism

#### Version Numbering

```
Major.Minor.Patch.Build
  1  .  0  .  0  . 1234

Major: Breaking changes (1.x.x.x → 2.x.x.x)
Minor: New features (1.0.x.x → 1.1.x.x)
Patch: Bug fixes (1.0.0.x → 1.0.1.x)
Build: Build number (auto-incremented)
```

#### Upgrade Types

**Type 1: Major Upgrade (1.0 → 2.0)**
- Uninstalls old version completely
- Installs new version fresh
- Preserves user data (logs, config)
- Requires reboot

**Type 2: Minor Upgrade (1.0 → 1.1)**
- Replaces changed files only
- Preserves configuration
- May require service restart
- No reboot needed

**Type 3: Patch (1.0.0 → 1.0.1)**
- Replaces specific binaries only
- Hot-patching when possible
- No service restart if possible
- No reboot needed

#### Upgrade Process (WiX Implementation)

```xml
<!-- In Upgrade.wxs -->
<Upgrade Id="YOUR-PRODUCT-UPGRADE-CODE">
  <!-- Detect and remove older versions -->
  <UpgradeVersion
    OnlyDetect="no"
    Property="OLDERVERSIONDETECTED"
    Maximum="$(var.ProductVersion)"
    IncludeMaximum="no"
    MigrateFeatures="yes" />

  <!-- Prevent downgrade -->
  <UpgradeVersion
    OnlyDetect="yes"
    Property="NEWERVERSIONDETECTED"
    Minimum="$(var.ProductVersion)"
    IncludeMinimum="no" />
</Upgrade>

<!-- Install sequence -->
<InstallExecuteSequence>
  <!-- Stop service before upgrade -->
  <Custom Action="StopService" Before="InstallValidate">
    OLDERVERSIONDETECTED
  </Custom>

  <!-- Unload driver before upgrade -->
  <Custom Action="UnloadDriver" After="StopService">
    OLDERVERSIONDETECTED
  </Custom>

  <!-- Remove old version -->
  <RemoveExistingProducts After="InstallInitialize" />

  <!-- Install new files -->
  <InstallFiles />

  <!-- Load new driver -->
  <Custom Action="LoadDriver" After="InstallFiles">
    NOT Installed
  </Custom>

  <!-- Start service -->
  <Custom Action="StartService" After="LoadDriver">
    NOT Installed
  </Custom>
</InstallExecuteSequence>
```

#### Update Mechanism (Future: Auto-Update)

```
Update Server (Phase 4 - Cloud Integration)
│
├── Version Check Endpoint
│   URL: https://api.youredr.com/updates/check
│   Request: { "current_version": "1.0.0", "product_id": "EDR" }
│   Response: { "latest_version": "1.1.0", "download_url": "...", "required": false }
│
├── Download Endpoint
│   URL: https://api.youredr.com/updates/download/1.1.0
│   Response: MSI binary stream (signed)
│
└── Update Process (Service-Side)
    1. Check for updates daily (configurable)
    2. Download MSI to temp directory
    3. Verify signature (EV certificate)
    4. Schedule installation (MSI silent: /quiet /norestart)
    5. Notify user (optional)
    6. Install on next reboot or immediately (based on policy)
```

---

### 7. Tests Directory (`tests/`)

**Purpose**: Integration, end-to-end, and stress tests.

```
tests/
├── integration/                              (Integration tests)
│   ├── test_driver_service_comm.cpp          (Driver ↔ Service communication)
│   ├── test_file_monitoring.cpp              (File operations end-to-end)
│   ├── test_process_monitoring.cpp           (Process tracking end-to-end)
│   ├── test_network_monitoring.cpp           (Network tracking end-to-end)
│   ├── test_log_rotation.cpp                 (Log rotation logic)
│   └── integration_tests.vcxproj
│
├── stress/                                    (Stress and performance tests)
│   ├── stress_test.ps1                       (PowerShell stress test orchestrator)
│   ├── load_generator.cpp                    (Generate high file I/O load)
│   ├── process_spawner.cpp                   (Spawn many processes)
│   ├── network_stress.cpp                    (Generate network connections)
│   └── stress_tests.vcxproj
│
├── e2e/                                       (End-to-end scenarios)
│   ├── scenario_malware_simulation.ps1       (Simulate malware behavior)
│   ├── scenario_normal_workload.ps1          (Simulate normal user activity)
│   └── e2e_test_runner.ps1                   (Run all E2E tests)
│
├── fixtures/                                  (Test data)
│   ├── sample_config.json
│   ├── sample_events.jsonl
│   └── test_binaries/
│       ├── benign.exe
│       └── suspicious.exe
│
└── README.md                                  (Test documentation)
```

---

### 8. Scripts Directory (`scripts/`)

**Purpose**: Build, deployment, and utility automation.

```
scripts/
├── build.ps1                                 (Build all components)
│   Usage: .\build.ps1 [-Configuration Debug|Release] [-Clean]
│   Actions:
│   - Restore NuGet packages
│   - Build driver (MSBuild)
│   - Build service (MSBuild)
│   - Build management tools
│   - Build installer (WiX)
│
├── sign.ps1                                  (Sign binaries)
│   Usage: .\sign.ps1 [-Configuration Debug|Release] [-CertThumbprint <thumbprint>]
│   Actions:
│   - Sign driver (.sys)
│   - Sign service (.exe)
│   - Sign management tools (.exe, .dll)
│   - Create catalog (.cat) for driver
│
├── deploy.ps1                                (Deploy to test VM)
│   Usage: .\deploy.ps1 -TargetVM <VMName> [-Configuration Debug|Release]
│   Actions:
│   - Copy files to VM via PowerShell remoting
│   - Stop old service
│   - Unload old driver
│   - Install new files
│   - Load new driver
│   - Start new service
│
├── run-tests.ps1                             (Run all tests)
│   Usage: .\run-tests.ps1 [-TestType Unit|Integration|Stress|All]
│   Actions:
│   - Run unit tests (VSTest)
│   - Run integration tests
│   - Run stress tests
│   - Generate coverage report
│
├── verify-environment.ps1                    (Verify development environment)
│   Actions:
│   - Check Visual Studio installed
│   - Check WDK installed
│   - Check WinDbg installed
│   - Check vcpkg installed
│   - Check test signing enabled
│   - Check certificate available
│
├── create-test-cert.ps1                      (Generate test certificate)
│   Actions:
│   - Create self-signed certificate
│   - Export to .cer file
│   - Install to Trusted Root
│   - Display thumbprint
│
├── install-local.ps1                         (Install on local machine)
│   Usage: .\install-local.ps1 [-Configuration Debug|Release]
│   Actions:
│   - Copy driver to System32\drivers
│   - Install driver via INF
│   - Install service
│   - Create log directories
│   - Set registry keys
│   - Start service
│
├── uninstall-local.ps1                       (Uninstall from local machine)
│   Actions:
│   - Stop service
│   - Unload driver
│   - Remove files
│   - Clean registry
│   - Clean logs (optional)
│
└── clean.ps1                                 (Clean all build artifacts)
    Actions:
    - Remove bin/ directories
    - Remove obj/ directories
    - Remove NuGet packages
    - Remove MSI output
```

---

### 9. Config Directory (`config/`)

**Purpose**: Configuration file templates.

```
config/
├── default_config.json                       (Default configuration)
│   {
│     "version": "1.0",
│     "logging": {
│       "directory": "C:\\ProgramData\\YourEDR\\Logs",
│       "max_file_size_mb": 100,
│       "retention_days": 7,
│       "compression_enabled": false
│     },
│     "filtering": {
│       "excluded_processes": ["System", "Registry", "smss.exe"],
│       "excluded_paths": ["C:\\Windows\\System32\\", "C:\\Windows\\SysWOW64\\"],
│       "monitored_extensions": [".exe", ".dll", ".sys", ".ps1", ".bat"]
│     },
│     "performance": {
│       "ring_buffer_size_mb": 2,
│       "event_batch_size": 100,
│       "sampling_rate_percent": 100
│     },
│     "features": {
│       "process_monitoring": true,
│       "file_monitoring": true,
│       "network_monitoring": true
│     }
│   }
│
└── filter_rules.json                         (Filter rules)
    {
      "exclude_paths": [
        "C:\\Windows\\System32\\",
        "C:\\Windows\\SysWOW64\\",
        "C:\\Program Files\\WindowsApps\\"
      ],
      "exclude_processes": [
        "System",
        "Registry",
        "smss.exe",
        "csrss.exe",
        "wininit.exe"
      ],
      "monitored_extensions": [
        ".exe", ".dll", ".sys",
        ".ps1", ".bat", ".cmd",
        ".vbs", ".js", ".jar"
      ]
    }
```

---

## Build Output Summary

After a full build, the output structure is:

```
bin/
├── Debug/                                    (Debug builds)
│   ├── driver/
│   │   ├── YourEDRFilter.sys
│   │   ├── YourEDRFilter.pdb
│   │   ├── YourEDRFilter.inf
│   │   └── YourEDRFilter.cat
│   ├── service/
│   │   ├── YourEDRService.exe
│   │   ├── YourEDRService.pdb
│   │   └── *.dll
│   ├── management/
│   │   ├── YourEDR-CLI.exe
│   │   └── YourEDR-CLI.pdb
│   └── tests/
│       ├── unit_tests.exe
│       └── integration_tests.exe
│
└── Release/                                  (Release builds)
    ├── driver/
    │   ├── YourEDRFilter.sys                 (Signed with EV certificate)
    │   ├── YourEDRFilter.inf
    │   └── YourEDRFilter.cat
    ├── service/
    │   ├── YourEDRService.exe                (Signed)
    │   └── *.dll
    ├── management/
    │   └── YourEDR-CLI.exe                   (Signed)
    └── installer/
        └── YourEDR_Installer_v1.0.0.msi      (Signed MSI)
```

---

## Distribution Package Structure

The final distribution package (MSI installer contains):

```
YourEDR_Installer_v1.0.0.msi
│
└── Embedded Files:
    ├── YourEDRFilter.sys                     (Driver)
    ├── YourEDRFilter.inf
    ├── YourEDRFilter.cat
    ├── YourEDRService.exe                    (Service)
    ├── YourEDRService.exe.config
    ├── nlohmann_json.dll
    ├── spdlog.dll
    ├── YourEDR-CLI.exe                       (Management tool)
    ├── YourEDR.psd1                          (PowerShell module)
    ├── YourEDR.psm1
    ├── default_config.json                   (Default configuration)
    ├── filter_rules.json
    ├── license.rtf                           (License agreement)
    └── README.txt                            (User documentation)
```

---

## Summary

This document explained:

1. ✅ **Complete directory structure** from root to every file
2. ✅ **Purpose of each directory** and subdirectory
3. ✅ **Build output locations** (where compiled files go)
4. ✅ **MSI packaging structure** (how installer is organized)
5. ✅ **Installation structure** (where files are placed on target system)
6. ✅ **Upgrade/update mechanism** (how updates work)
7. ✅ **Distribution package** (final MSI contents)

**Next**: See individual component READMEs for detailed instructions:
- `driver/README.md` - Driver development
- `service/README.md` - Service development
- `installer/WiX/README.md` - MSI customization
- `scripts/README.md` - Script usage

**Questions?** Check `docs/technical/01-getting-started.md` for navigation guide.
