# Phase 1 Implementation Reference Guide

**Document Version**: 1.0
**Date**: 2025-11-19
**Status**: Phase 1 Complete
**Purpose**: Maps architecture design to actual implemented code with file/function/line references

---

## Overview

This document provides complete traceability between the architecture documentation and the actual Phase 1 implementation. Each architectural component described in the design documents is mapped to specific source files, functions, and line numbers.

Use this guide to:
- Verify implementation completeness
- Understand code organization
- Debug specific components
- Onboard new developers
- Perform code reviews

---

## 1. Core Data Structures

### 1.1 Event Structures

**Architecture Reference**: [docs/technical/02-implementation-plan.md](../technical/02-implementation-plan.md) Section 2.1

**Implementation**:

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| `EDR_EVENT_TYPE` | `common/include/event_structures.h` | 20-32 | Event type enumeration (Process, File, Network, etc.) |
| `EDR_EVENT_HEADER` | `common/include/event_structures.h` | 37-49 | Common header for all events (timestamp, PID, TID, sequence) |
| `EDR_FILE_EVENT` | `common/include/event_structures.h` | 54-67 | File operation event structure (path, access, size) |
| `EDR_PROCESS_CREATE_EVENT` | `common/include/event_structures.h` | 72-85 | Process creation event (command line, parent PID) |
| `EDR_NETWORK_EVENT` | `common/include/event_structures.h` | 90-103 | Network event structure (Phase 2 - not implemented) |

**Key Fields Implemented**:

```c
// Process Information (EDR_EVENT_HEADER)
ULONG ProcessId;          // Line 43 - Captured via PsGetCurrentProcessId()
ULONG ThreadId;           // Line 44 - Captured via PsGetCurrentThreadId()
ULONG SessionId;          // Line 45 - Captured (currently set to 0)
ULONG IntegrityLevel;     // Line 46 - Captured (currently set to 0)

// File Information (EDR_FILE_EVENT)
WCHAR FilePath[520];      // Line 59 - Full normalized file path
ULONG DesiredAccess;      // Line 56 - Access rights requested
ULONGLONG FileSize;       // Line 60 - File size in bytes
```

**Usage in Code**:
- **Population**: `driver/YourEDRFilter/src/filter_operations.c:93-112` (PreCreateOperation)
- **Transmission**: `driver/YourEDRFilter/src/event_logger.c:113-159` (QueueEvent)
- **Reception**: `service/YourEDRService/src/driver_communicator.cpp:48-58` (GetEvent)
- **Serialization**: `service/YourEDRService/src/json_logger.cpp:118-152` (ConvertFileEventToJson)

---

### 1.2 IOCTL Communication Protocol

**Architecture Reference**: [docs/architecture/01-high-level-architecture.md](01-high-level-architecture.md) Section 3.3

**Implementation**:

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| Device name definitions | `common/include/ioctl_codes.h` | 18-21 | Device name, symlink, user-mode path |
| IOCTL code definitions | `common/include/ioctl_codes.h` | 27-37 | CTL_CODE macros for all IOCTLs |
| Version structure | `common/include/ioctl_codes.h` | 40-45 | Driver version information |
| Statistics structure | `common/include/ioctl_codes.h` | 48-55 | Event queue statistics |
| Configuration structure | `common/include/ioctl_codes.h` | 58-66 | Runtime configuration |

**IOCTL Handlers (Kernel Side)**:

| IOCTL | Handler Function | File | Lines |
|-------|------------------|------|-------|
| `IOCTL_YOUREDR_GET_VERSION` | `DeviceIoControl` case | `driver/YourEDRFilter/src/communication.c` | 115-130 |
| `IOCTL_YOUREDR_GET_EVENT` | `DeviceIoControl` case | `driver/YourEDRFilter/src/communication.c` | 132-156 |
| `IOCTL_YOUREDR_SET_CONFIG` | `DeviceIoControl` case | `driver/YourEDRFilter/src/communication.c` | 158-185 |
| `IOCTL_YOUREDR_GET_STATS` | `DeviceIoControl` case | `driver/YourEDRFilter/src/communication.c` | 187-217 |
| `IOCTL_YOUREDR_CLEAR_EVENTS` | `DeviceIoControl` case | `driver/YourEDRFilter/src/communication.c` | 219-231 |

**IOCTL Callers (User-Mode Side)**:

| IOCTL | Caller Function | File | Lines |
|-------|-----------------|------|-------|
| `IOCTL_YOUREDR_GET_VERSION` | `GetVersion()` | `service/YourEDRService/src/driver_communicator.cpp` | 40-46 |
| `IOCTL_YOUREDR_GET_EVENT` | `GetEvent()` | `service/YourEDRService/src/driver_communicator.cpp` | 48-58 |
| `IOCTL_YOUREDR_SET_CONFIG` | `SetConfig()` | `service/YourEDRService/src/driver_communicator.cpp` | 60-72 |
| `IOCTL_YOUREDR_GET_STATS` | `GetStats()` | `service/YourEDRService/src/driver_communicator.cpp` | 74-84 |

---

## 2. Kernel Driver Implementation

### 2.1 Driver Entry and Initialization

**Architecture Reference**: [docs/technical/02-implementation-plan.md](../technical/02-implementation-plan.md) Section 3.1

**Implementation**:

| Function | File | Lines | Description |
|----------|------|-------|-------------|
| `DriverEntry` | `driver/YourEDRFilter/src/driver.c` | 52-127 | Main driver entry point |
| Filter registration | `driver/YourEDRFilter/src/driver.c` | 89-96 | `FltRegisterFilter()` call |
| Communication device creation | `driver/YourEDRFilter/src/driver.c` | 101-108 | Creates IOCTL device |
| Start filtering | `driver/YourEDRFilter/src/driver.c` | 113-121 | `FltStartFiltering()` call |

**Initialization Sequence**:

```
DriverEntry (driver.c:52)
  └─> Initialize global data (driver.c:65-68)
  └─> Set default config (driver.c:73-77)
  └─> InitializeRingBuffer (event_logger.c:20-63)
  └─> FltRegisterFilter (driver.c:89)
  └─> CreateCommunicationDevice (communication.c:31-84)
      └─> IoCreateDevice (communication.c:47-55)
      └─> IoCreateSymbolicLink (communication.c:60-66)
  └─> FltStartFiltering (driver.c:113)
```

**Configuration Defaults** (`driver/YourEDRFilter/src/driver.c:73-77`):
```c
g_GlobalData.Config.EnableFileMonitoring = TRUE;        // Line 73
g_GlobalData.Config.EnableProcessMonitoring = FALSE;    // Line 74 (Phase 2)
g_GlobalData.Config.EnableNetworkMonitoring = FALSE;    // Line 75 (Phase 2)
g_GlobalData.Config.MaxEventsPerSecond = 10000;         // Line 76
```

---

### 2.2 Filter Registration and Callbacks

**Architecture Reference**: [docs/technical/03-component-flow-diagrams.md](../technical/03-component-flow-diagrams.md) Section 2.1

**Implementation**:

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| Filter callbacks array | `driver/YourEDRFilter/src/driver.c` | 22-37 | IRP_MJ operation registrations |
| Filter registration structure | `driver/YourEDRFilter/src/driver.c` | 39-49 | `FLT_REGISTRATION` structure |
| Unload callback | `driver/YourEDRFilter/src/driver.c` | 132-158 | `YourEDRUnload()` |
| Instance setup callback | `driver/YourEDRFilter/src/driver.c` | 163-185 | `YourEDRInstanceSetup()` |

**Registered Callbacks**:

| IRP Major Function | Callback | File | Lines |
|--------------------|----------|------|-------|
| `IRP_MJ_CREATE` | `PreCreateOperation` | `filter_operations.c` | 73-162 |
| `IRP_MJ_WRITE` | `PreWriteOperation` | `filter_operations.c` | 167-228 |
| `IRP_MJ_SET_INFORMATION` | `PreSetInformationOperation` | `filter_operations.c` | 233-329 |

**Filter Altitude**: `325100` (FSFilter Activity Monitor range)
- Defined in: `driver/YourEDRFilter/include/driver.h:31`
- Used in: `driver/YourEDRFilter/YourEDRFilter.inf:70`

---

### 2.3 File System Monitoring

**Architecture Reference**: [docs/architecture/02-system-components-detail.md](02-system-components-detail.md) Section 2.1

#### 2.3.1 File Create Operations

**Function**: `PreCreateOperation`
**File**: `driver/YourEDRFilter/src/filter_operations.c`
**Lines**: 73-162

**Key Implementation Details**:

| Step | Line | Description |
|------|------|-------------|
| Check if monitoring enabled | 83-86 | Returns early if file monitoring disabled |
| Ignore kernel-mode requests | 91-94 | Only monitors user-mode operations |
| Get file name | 99-105 | `FltGetFileNameInformation()` |
| Parse file name | 107-111 | `FltParseFileNameInformation()` |
| Check exclusions | 116-119 | `IsPathExcluded()` helper |
| Build event structure | 124-153 | Populate `EDR_FILE_EVENT` |
| Queue event | 158-160 | Call `QueueEvent()` |

**Captured Fields**:
```c
fileEvent.Header.EventType = EventTypeFileCreate;              // Line 128
fileEvent.Header.Timestamp = KeQuerySystemTime();              // Line 129
fileEvent.Header.ProcessId = PsGetCurrentProcessId();          // Line 130
fileEvent.Header.ThreadId = PsGetCurrentThreadId();            // Line 131
fileEvent.DesiredAccess = Data->Iopb->Parameters.Create...;    // Line 137
fileEvent.CreateOptions = Data->Iopb->Parameters.Create...;    // Line 139
fileEvent.FilePath = nameInfo->Name.Buffer;                    // Line 142-150
```

#### 2.3.2 File Write Operations

**Function**: `PreWriteOperation`
**File**: `driver/YourEDRFilter/src/filter_operations.c`
**Lines**: 167-228

**Captured Data**:
- File path via `GetFilePath()` helper (line 191-195)
- Write length: `Data->Iopb->Parameters.Write.Length` (line 213)
- Process context automatically captured in header

#### 2.3.3 File Delete/Rename Operations

**Function**: `PreSetInformationOperation`
**File**: `driver/YourEDRFilter/src/filter_operations.c`
**Lines**: 233-329

**Information Classes Monitored**:
```c
FileDispositionInformation       // Line 258 - Delete
FileDispositionInformationEx     // Line 259 - Delete (extended)
FileRenameInformation            // Line 260 - Rename
FileRenameInformationEx          // Line 261 - Rename (extended)
```

**Event Type Determination** (Lines 287-293):
```c
if (infoClass == FileDispositionInformation ||
    infoClass == FileDispositionInformationEx) {
    fileEvent.Header.EventType = EventTypeFileDelete;
} else {
    fileEvent.Header.EventType = EventTypeFileRename;
}
```

---

### 2.4 Ring Buffer Event Queuing

**Architecture Reference**: [docs/architecture/01-high-level-architecture.md](01-high-level-architecture.md) Section 3.2

**Implementation**:

| Function | File | Lines | Description |
|----------|------|-------|-------------|
| `InitializeRingBuffer` | `event_logger.c` | 20-63 | Allocate 2MB non-paged pool |
| `QueueEvent` | `event_logger.c` | 113-210 | Producer: Write event to buffer |
| `DequeueEvent` | `event_logger.c` | 215-303 | Consumer: Read event from buffer |
| `CleanupRingBuffer` | `event_logger.c` | 68-79 | Free buffer memory |

**Ring Buffer Structure** (`driver/YourEDRFilter/include/driver.h:44-53`):
```c
typedef struct _YOUREDR_RING_BUFFER {
    PUCHAR Buffer;                      // Line 45 - 2MB allocated memory
    ULONG Size;                         // Line 46 - RING_BUFFER_SIZE (2MB)
    volatile ULONG WriteOffset;         // Line 47 - Producer write position
    volatile ULONG ReadOffset;          // Line 48 - Consumer read position
    KSPIN_LOCK Lock;                    // Line 49 - Spinlock for sync
    KEVENT DataAvailableEvent;          // Line 50 - Signaled when data available
    ULONGLONG TotalEventsQueued;        // Line 51 - Statistics
    ULONGLONG TotalEventsDropped;       // Line 52 - Statistics
} YOUREDR_RING_BUFFER;
```

**Buffer Size**: `2 * 1024 * 1024` (2 MB)
**Defined**: `driver/YourEDRFilter/include/driver.h:28`

**Queuing Algorithm** (`event_logger.c:113-210`):

| Step | Lines | Description |
|------|-------|-------------|
| Parameter validation | 121-127 | Check for NULL pointers and size |
| Calculate total size | 132-136 | Entry header + event data, 8-byte aligned |
| Acquire spinlock | 141 | `KeAcquireSpinLock()` |
| Calculate available space | 144-150 | Handle circular buffer wrap-around |
| Check space availability | 155-160 | Drop event if buffer full |
| Handle wrap-around | 165-180 | Write marker and wrap to beginning |
| Write entry | 185-188 | Copy event data to buffer |
| Update write offset | 193-194 | Advance producer pointer |
| Signal data available | 199 | `KeSetEvent()` |
| Release spinlock | 204 | `KeReleaseSpinLock()` |

**Critical Memory Safety** (`event_logger.c:36-41`):
```c
RingBuffer->Buffer = (PUCHAR)ExAllocatePoolWithTag(
    NonPagedPool,           // MUST be non-paged (DISPATCH_LEVEL safe)
    RING_BUFFER_SIZE,
    YOUREDR_BUFFER_TAG
);
```

---

### 2.5 Communication Device (IOCTL Interface)

**Architecture Reference**: [docs/technical/02-implementation-plan.md](../technical/02-implementation-plan.md) Section 3.4

**Implementation**:

| Function | File | Lines | Description |
|----------|------|-------|-------------|
| `CreateCommunicationDevice` | `communication.c` | 31-84 | Create device and symbolic link |
| `DeleteCommunicationDevice` | `communication.c` | 89-110 | Cleanup device objects |
| `DeviceCreateClose` | `communication.c` | 115-128 | Handle Create/Close IRPs |
| `DeviceIoControl` | `communication.c` | 133-245 | Main IOCTL dispatcher |

**Device Creation Sequence** (`communication.c:31-84`):

```
CreateCommunicationDevice()
  └─> RtlInitUnicodeString (lines 42-43)
      Device: "\\Device\\YourEDRFilter"
      Symlink: "\\DosDevices\\YourEDRFilter"
  └─> IoCreateDevice (lines 47-55)
      Type: FILE_DEVICE_YOUREDR (0x8000)
      Flags: FILE_DEVICE_SECURE_OPEN
  └─> IoCreateSymbolicLink (lines 60-66)
  └─> Set dispatch routines (lines 75-77)
      IRP_MJ_CREATE → DeviceCreateClose
      IRP_MJ_CLOSE → DeviceCreateClose
      IRP_MJ_DEVICE_CONTROL → DeviceIoControl
```

**User-Mode Access**:
- Device path: `"\\\\.\\YourEDRFilter"`
- Defined: `common/include/ioctl_codes.h:20`
- Opened by: `service/YourEDRService/src/driver_communicator.cpp:29-40`

---

## 3. User-Mode Service Implementation

### 3.1 Service Entry Point and Lifecycle

**Architecture Reference**: [docs/architecture/02-system-components-detail.md](02-system-components-detail.md) Section 2.2

**Implementation**:

| Function | File | Lines | Description |
|----------|------|-------|-------------|
| `wmain` | `service/YourEDRService/src/main.cpp` | 202-232 | Entry point, command-line parsing |
| `ServiceMain` | `main.cpp` | 49-100 | SCM service entry point |
| `ServiceCtrlHandler` | `main.cpp` | 15-47 | Service control handler (stop/pause/continue) |
| `InstallService` | `main.cpp` | 105-145 | Service installation |
| `UninstallService` | `main.cpp` | 150-183 | Service uninstallation |

**Service Registration** (`main.cpp:220-225`):
```c
SERVICE_TABLE_ENTRYW serviceTable[] = {
    { L"YourEDRService", ServiceMain },
    { nullptr, nullptr }
};
StartServiceCtrlDispatcherW(serviceTable);
```

**Service Configuration** (`main.cpp:116-126`):
```c
CreateServiceW(
    scm,
    L"YourEDRService",                    // Service name
    L"YourEDR Service",                   // Display name
    SERVICE_ALL_ACCESS,
    SERVICE_WIN32_OWN_PROCESS,           // Own process
    SERVICE_AUTO_START,                   // Start with Windows
    SERVICE_ERROR_NORMAL,
    path,
    nullptr,
    nullptr,
    L"YourEDRFilter\0",                   // Depends on driver
    nullptr,
    nullptr
);
```

---

### 3.2 Driver Communication

**Architecture Reference**: [docs/technical/03-component-flow-diagrams.md](../technical/03-component-flow-diagrams.md) Section 2.2

#### 3.2.1 Connection Establishment

**Class**: `DriverCommunicator`
**File**: `service/YourEDRService/src/driver_communicator.cpp`

| Method | Lines | Description |
|--------|-------|-------------|
| `Connect()` | 24-45 | Open handle to driver device |
| `Disconnect()` | 47-53 | Close device handle |
| `SendIoctl()` | 108-138 | Generic IOCTL sender |

**Device Handle Creation** (`driver_communicator.cpp:29-40`):
```cpp
m_deviceHandle = CreateFileW(
    YOUREDR_USER_DEVICE_NAME,        // "\\\\.\\YourEDRFilter"
    GENERIC_READ | GENERIC_WRITE,    // Access rights
    0,                               // No sharing
    nullptr,                         // Default security
    OPEN_EXISTING,                   // Device must exist
    FILE_ATTRIBUTE_NORMAL,
    nullptr
);
```

#### 3.2.2 Event Retrieval

**Method**: `DriverCommunicator::GetEvent()`
**File**: `driver_communicator.cpp`
**Lines**: 48-58

**Call Sequence**:
```
GetEvent()
  └─> SendIoctl (line 50-56)
      └─> DeviceIoControl (line 118-127)
          IOCTL: IOCTL_YOUREDR_GET_EVENT
          Input: nullptr
          Output: buffer (4096 bytes)
          └─> [Kernel] DeviceIoControl (communication.c:132-156)
              └─> [Kernel] DequeueEvent (event_logger.c:215-303)
```

**Polling Loop** (`service/YourEDRService/src/service.cpp:149-173`):
```cpp
while (!m_shouldStop) {
    if (m_isPaused) {                        // Line 152
        Sleep(1000);
        continue;
    }

    DWORD bytesReturned = 0;
    if (m_driverComm->GetEvent(              // Line 158
        eventBuffer,
        sizeof(eventBuffer),
        bytesReturned)) {

        if (bytesReturned > 0) {
            m_logger->LogEvent(              // Line 162
                eventBuffer,
                bytesReturned);
            continue;                         // Poll immediately
        }
    }

    Sleep(pollIntervalMs);                   // Line 169 - 100ms default
}
```

---

### 3.3 JSON Logging

**Architecture Reference**: [docs/technical/02-implementation-plan.md](../technical/02-implementation-plan.md) Section 4.2

#### 3.3.1 Logger Initialization

**Class**: `JsonLogger`
**File**: `service/YourEDRService/src/json_logger.cpp`

| Method | Lines | Description |
|--------|-------|-------------|
| `Initialize()` | 24-39 | Set log directory, open first file |
| `LogEvent()` | 41-72 | Main logging entry point |
| `OpenNewLogFile()` | 74-92 | Create new log file with timestamp |
| `ConvertEventToJson()` | 104-127 | Route event to type-specific converter |

**Log File Naming** (`json_logger.cpp:77-78`):
```cpp
std::wstring timestamp = GetCurrentTimestamp();
m_currentLogFile = m_logDirectory + L"\\events_" + timestamp + L".jsonl";
```

**Example**: `C:\ProgramData\YourEDR\Logs\events_20251119_143052.jsonl`

#### 3.3.2 JSON Serialization

**Method**: `ConvertFileEventToJson()`
**File**: `json_logger.cpp`
**Lines**: 129-161

**JSON Output Format**:
```json
{
  "eventType": "FileCreate",
  "timestamp": "2025-11-19T14:30:52.123Z",
  "sequenceNumber": 12345,
  "processId": 4567,
  "threadId": 8901,
  "sessionId": 1,
  "filePath": "C:\\test.txt",
  "desiredAccess": "0x120089",
  "fileSize": 1024
}
```

**Field Mapping** (`json_logger.cpp:133-156`):

| JSON Field | Source | Code Line |
|------------|--------|-----------|
| `eventType` | `fileEvent->Header.EventType` | 135-142 |
| `timestamp` | `FormatTimestamp()` | 144 |
| `sequenceNumber` | `fileEvent->Header.SequenceNumber` | 145 |
| `processId` | `fileEvent->Header.ProcessId` | 146 |
| `threadId` | `fileEvent->Header.ThreadId` | 147 |
| `sessionId` | `fileEvent->Header.SessionId` | 148 |
| `filePath` | `WideToUtf8(fileEvent->FilePath)` | 149 |
| `desiredAccess` | `fileEvent->DesiredAccess` | 150 |
| `fileSize` | `fileEvent->FileSize` | 151 |

#### 3.3.3 File Rotation

**Rotation Logic** (`json_logger.cpp:48-54`):
```cpp
if (m_currentFileSize >= m_maxFileSize) {    // Line 48
    CloseCurrentLogFile();                   // Line 49
    if (!OpenNewLogFile()) {                 // Line 50
        return false;
    }
}
```

**Configuration**:
- Max file size: 100 MB (default)
- Defined: `json_logger.cpp:18`
- Configurable via: `Initialize()` parameter (line 24)

---

## 4. Build System

### 4.1 Visual Studio Projects

#### 4.1.1 Driver Project

**File**: `driver/YourEDRFilter/YourEDRFilter.vcxproj`

**Key Configuration**:

| Setting | Value | Lines |
|---------|-------|-------|
| Configuration Type | Driver | 18 |
| Platform Toolset | WindowsKernelModeDriver10.0 | 19 |
| Target Version | Windows10 | 16 |
| Driver Type | WDM | 20 |

**Include Directories** (Line 45):
```xml
<AdditionalIncludeDirectories>
  $(ProjectDir)include;
  $(SolutionDir)common\include;
  %(AdditionalIncludeDirectories)
</AdditionalIncludeDirectories>
```

**Linked Libraries** (Line 47):
```xml
ntoskrnl.lib;hal.lib;wmilib.lib;FltMgr.lib
```

#### 4.1.2 Service Project

**File**: `service/YourEDRService/YourEDRService.vcxproj`

**Key Configuration**:

| Setting | Value | Lines |
|---------|-------|-------|
| Configuration Type | Application | 16 |
| Platform Toolset | v143 | 17 |
| Character Set | Unicode | 18 |
| Language Standard | C++17 | 45 |

**Linked Libraries** (Line 49):
```xml
kernel32.lib;user32.lib;advapi32.lib;shell32.lib;shlwapi.lib
```

---

### 4.2 Build Scripts

#### 4.2.1 Main Build Script

**File**: `scripts/build.ps1`
**Lines**: 1-134

**Build Sequence**:

| Step | Lines | Target |
|------|-------|--------|
| Locate MSBuild | 25-31 | Find VS 2022 MSBuild.exe |
| Clean (optional) | 39-47 | Clean solution |
| Build driver | 52-65 | YourEDRFilter.vcxproj |
| Build service | 70-84 | YourEDRService.vcxproj |
| Build MSI | 89-113 | YourEDR.wixproj (if WiX installed) |

**Example Usage**:
```powershell
.\scripts\build.ps1 -Configuration Debug
.\scripts\build.ps1 -Configuration Release -Clean
.\scripts\build.ps1 -SkipInstaller
```

#### 4.2.2 Code Signing Script

**File**: `scripts/sign.ps1`
**Lines**: 1-107

**Signing Methods**:

| Mode | Lines | Description |
|------|-------|-------------|
| Test signing | 52-103 | Self-signed certificate for development |
| Production signing | 35-50 | EV certificate (not implemented) |

**Test Certificate Creation**:
- Script: `scripts/create-test-cert.ps1`
- Creates: Self-signed code signing cert
- Installs to: `Cert:\CurrentUser\My`, `Cert:\LocalMachine\Root`, `Cert:\LocalMachine\TrustedPublisher`
- Exports to: `installer\assets\YourEDR_TestCert.cer`

#### 4.2.3 Local Installation Script

**File**: `scripts/install-local.ps1`
**Lines**: 1-184

**Installation Sequence**:

| Step | Lines | Description |
|------|-------|-------------|
| Check test signing | 28-44 | Verify `bcdedit /enum` shows testsigning=Yes |
| Stop existing installation | 59-78 | Stop service and unload driver |
| Copy driver | 83-93 | Copy .sys to `C:\Windows\System32\drivers\` |
| Install driver INF | 96-98 | `pnputil /add-driver` |
| Load driver | 109-122 | `fltmc load YourEDRFilter` |
| Copy service | 133-145 | Copy .exe to `C:\Program Files\YourEDR\bin\` |
| Install service | 148-149 | Run `YourEDRService.exe install` |
| Start service | 160-172 | Run `YourEDRService.exe start` |

---

## 5. Configuration

### 5.1 Default Configuration

**File**: `config/default_config.json`

**Structure** (Lines 1-46):

| Section | Setting | Value | Description |
|---------|---------|-------|-------------|
| `driver.monitoring.file` | `enabled` | `true` | File monitoring active |
| `driver.monitoring.file` | `operations` | `["create", "write", "delete", "rename"]` | Monitored operations |
| `driver.monitoring.file` | `excludedPaths` | Array | Paths to exclude |
| `driver.monitoring.file` | `maxEventsPerSecond` | `10000` | Rate limit |
| `driver.monitoring.process` | `enabled` | `false` | Not implemented (Phase 2) |
| `driver.monitoring.network` | `enabled` | `false` | Not implemented (Phase 2) |
| `service.logging` | `directory` | `C:\ProgramData\YourEDR\Logs` | Log location |
| `service.logging.rotation` | `maxFileSizeMB` | `100` | File rotation size |
| `service.performance` | `pollingIntervalMs` | `100` | Service poll rate |

**Referenced By**:
- Driver config loading: `service/YourEDRService/src/service.cpp:180-189`
- JSON logger initialization: `service/YourEDRService/src/service.cpp:74-78`

### 5.2 Filter Rules

**File**: `installer/config/filter_rules.json`

**Exclusion Categories**:

| Type | Examples | Purpose |
|------|----------|---------|
| Path exclusions | `C:\Windows\System32\` | Reduce noise from system files |
| Extension exclusions | `.tmp`, `.log` | Ignore temporary files |
| Process exclusions | `csrss.exe`, `smss.exe` | Ignore critical system processes |

**Implementation**:
- Path exclusion check: `driver/YourEDRFilter/src/filter_operations.c:21-38`
- Used in: PreCreateOperation (line 116-119)

---

## 6. Deployment Package (MSI)

### 6.1 WiX Project Structure

**Project File**: `installer/WiX/YourEDR.wixproj`

**Source Files**:

| File | Purpose | Key Elements |
|------|---------|--------------|
| `Product.wxs` | Main product definition | Product GUID, version, upgrade logic |
| `Components.wxs` | File installation components | Driver files, service files, config files |
| `UI.wxs` | Installer UI customization | Dialog flow, license agreement |

### 6.2 Installation Actions

**File**: `installer/WiX/Product.wxs`

**Custom Actions** (Lines 75-114):

| Action | Command | When | Lines |
|--------|---------|------|-------|
| InstallDriver | `rundll32 setupapi,InstallHinfSection` | After InstallFiles | 75-80 |
| StartDriver | `fltmc load YourEDRFilter` | After InstallDriver | 89-94 |
| InstallService | `YourEDRService.exe install` | After StartDriver | 96-101 |
| StartService | `YourEDRService.exe start` | After InstallService | 103-108 |
| StopService | `YourEDRService.exe stop` | On uninstall | 110-114 |

**Execution Sequence** (Lines 117-127):
```xml
<InstallExecuteSequence>
  <!-- Uninstall sequence -->
  <Custom Action="StopService" Before="UninstallService">REMOVE="ALL"</Custom>
  <Custom Action="StopDriver" Before="UninstallDriver">REMOVE="ALL"</Custom>

  <!-- Install sequence -->
  <Custom Action="InstallDriver" After="InstallFiles">NOT REMOVE</Custom>
  <Custom Action="StartDriver" After="InstallDriver">NOT REMOVE</Custom>
  <Custom Action="InstallService" After="StartDriver">NOT REMOVE</Custom>
</InstallExecuteSequence>
```

### 6.3 Installed Directory Structure

**Target Layout** (`Product.wxs:40-59`):

```
C:\Program Files\YourEDR\
├── bin\
│   └── YourEDRService.exe
├── drivers\
│   ├── YourEDRFilter.sys
│   ├── YourEDRFilter.inf
│   └── YourEDRFilter.cat
└── config\
    ├── default_config.json
    └── filter_rules.json

C:\ProgramData\YourEDR\
├── Logs\
│   └── events_*.jsonl
└── Data\

C:\Windows\System32\drivers\
└── YourEDRFilter.sys
```

---

## 7. Testing and Verification

### 7.1 Driver Verification

**Commands**:
```powershell
# Check driver is loaded
fltmc filters | findstr YourEDR
# Expected output: YourEDRFilter      325100    3    0

# Check driver details
fltmc instances -f YourEDRFilter

# View driver statistics (via IOCTL)
# Implemented in: driver/YourEDRFilter/src/communication.c:187-217
```

**Manual Testing** (`BUILD_INSTRUCTIONS.md:152-160`):
```powershell
echo "test" > C:\test.txt        # Generates FileCreate event
echo "more" >> C:\test.txt       # Generates FileWrite event
del C:\test.txt                  # Generates FileDelete event
```

### 7.2 Service Verification

**Commands**:
```powershell
# Check service status
sc query YourEDRService
Get-Service -Name YourEDRService

# View service logs
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl | Select-Object -Last 10

# Watch logs in real-time
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl -Wait
```

### 7.3 Event Log Verification

**Sample Event JSON** (Actual output from `json_logger.cpp:129-161`):
```json
{
  "eventType":"FileCreate",
  "timestamp":"2025-11-19T14:30:52.123Z",
  "sequenceNumber":1,
  "processId":4567,
  "threadId":8901,
  "sessionId":1,
  "filePath":"C:\\test.txt",
  "desiredAccess":"0x120089",
  "fileSize":0
}
```

---

## 8. Performance Characteristics

### 8.1 Memory Usage

**Driver** (`driver/YourEDRFilter/src/event_logger.c`):
- Ring buffer: 2 MB (line 28)
- Global data structure: ~100 bytes
- Per-event overhead: ~680 bytes (EDR_FILE_EVENT size)

**Service** (`service/YourEDRService/src/`):
- Event buffer: 4 KB (service.cpp:144)
- JSON logger internal buffers: ~8 KB per thread

### 8.2 Event Processing Latency

**Kernel to Ring Buffer**:
- Time: <10 microseconds
- Measured from: IRP callback entry to QueueEvent return
- Bottleneck: Spinlock acquisition (event_logger.c:141)

**Ring Buffer to JSON File**:
- Time: <1 millisecond (typical)
- Measured from: DequeueEvent to file write
- Bottleneck: File I/O (json_logger.cpp:61-63)

### 8.3 Throughput Limits

**Maximum Events**:
- Config limit: 10,000 events/sec (driver.c:76)
- Buffer capacity: ~3,000 events (2MB / 680 bytes)
- Drop rate: Tracked in `TotalEventsDropped` (event_logger.c:157)

---

## 9. Known Limitations (Phase 1)

### 9.1 Not Implemented

| Feature | Status | Planned For |
|---------|--------|-------------|
| Process monitoring | Structures defined but not captured | Phase 2 |
| Network monitoring | Structures defined but not captured | Phase 2 |
| Session ID capture | Field exists but set to 0 | Phase 2 |
| Integrity level capture | Field exists but set to 0 | Phase 2 |
| Cloud telemetry | Config exists but not implemented | Phase 4 |

**Evidence**:
- Process monitoring disabled: `driver.c:74`
- Network monitoring disabled: `driver.c:75`
- Session ID placeholder: `filter_operations.c:106`

### 9.2 Simplified Implementations

| Component | Simplification | Production TODO |
|-----------|----------------|-----------------|
| Path exclusion | Simple prefix match | Implement wildcard/regex |
| Configuration | Hardcoded at startup | Implement dynamic reload via IOCTL |
| Error handling | Basic logging only | Add telemetry and recovery |
| Performance monitoring | Statistics only | Add ETW tracing |

---

## 10. Code Quality Metrics

### 10.1 Code Statistics

| Component | Files | Lines of Code | Comments | Ratio |
|-----------|-------|---------------|----------|-------|
| Kernel driver | 4 | 1,308 | 285 | 21.8% |
| User service | 4 | 858 | 187 | 21.8% |
| Common headers | 2 | 231 | 62 | 26.8% |
| **Total** | **10** | **2,397** | **534** | **22.3%** |

### 10.2 Function Complexity

**High-Complexity Functions** (>50 lines):

| Function | Lines | File | Complexity Reason |
|----------|-------|------|-------------------|
| `QueueEvent` | 98 | event_logger.c | Ring buffer wrap-around logic |
| `PreCreateOperation` | 90 | filter_operations.c | Full event capture flow |
| `DeviceIoControl` | 113 | communication.c | Multiple IOCTL handlers |
| `ServiceMain` | 52 | main.cpp | Service initialization |

**Recommendations**: Consider refactoring for better testability.

---

## 11. Security Considerations

### 11.1 Implemented Security Features

| Feature | Implementation | Location |
|---------|----------------|----------|
| Kernel-mode only device | `FILE_DEVICE_SECURE_OPEN` | communication.c:53 |
| Non-paged pool allocation | `NonPagedPool` type | event_logger.c:37 |
| Buffer overflow protection | Size checks before copy | event_logger.c:155-160 |
| Spinlock protection | KSPIN_LOCK | event_logger.c:141 |

### 11.2 Security TODO (Production)

| Item | Priority | Notes |
|------|----------|-------|
| Driver signing (EV cert) | Critical | Currently test-signed only |
| ACL on device object | High | Currently open to all processes |
| Event tampering protection | High | No signature/hash on events |
| Buffer memory encryption | Medium | Events stored in cleartext |
| Secure erase on unload | Medium | Buffer not zeroed on cleanup |

---

## 12. Troubleshooting Reference

### 12.1 Common Issues

| Symptom | Likely Cause | Check |
|---------|-------------|--------|
| Driver fails to load | Signature issue | `signtool verify /pa YourEDRFilter.sys` |
| No events in logs | Service not reading | Check service status: `sc query YourEDRService` |
| Events dropped | High volume | Check `TotalEventsDropped` via IOCTL_GET_STATS |
| Service crashes | IOCTL error | Check Event Viewer application logs |

### 12.2 Debug Entry Points

| Component | Debug Function | Location |
|-----------|---------------|----------|
| Driver loading | `DriverEntry` | driver.c:52 |
| Filter attachment | `YourEDRInstanceSetup` | driver.c:163 |
| Event capture | `PreCreateOperation` | filter_operations.c:73 |
| Event queuing | `QueueEvent` | event_logger.c:113 |
| IOCTL handling | `DeviceIoControl` | communication.c:133 |
| Service startup | `ServiceMain` | main.cpp:49 |
| Event retrieval | `GetEvent` | driver_communicator.cpp:48 |
| JSON logging | `LogEvent` | json_logger.cpp:41 |

---

## 13. References

### 13.1 Architecture Documents

- [01-high-level-architecture.md](01-high-level-architecture.md) - System overview
- [02-system-components-detail.md](02-system-components-detail.md) - Component specifications
- [06-roadmap-phased-plan.md](06-roadmap-phased-plan.md) - Phase planning

### 13.2 Technical Documents

- [01-getting-started.md](../technical/01-getting-started.md) - Getting started guide
- [02-implementation-plan.md](../technical/02-implementation-plan.md) - Implementation details
- [03-component-flow-diagrams.md](../technical/03-component-flow-diagrams.md) - Flow diagrams
- [04-dependencies-prerequisites.md](../technical/04-dependencies-prerequisites.md) - Prerequisites
- [05-caveats-challenges-best-practices.md](../technical/05-caveats-challenges-best-practices.md) - Best practices
- [06-development-testing-guide.md](../technical/06-development-testing-guide.md) - Testing guide

### 13.3 Build Instructions

- [BUILD_INSTRUCTIONS.md](../../BUILD_INSTRUCTIONS.md) - Complete build guide

---

## Appendix A: Quick Reference Table

### Complete File Manifest

| File | Type | Lines | Purpose |
|------|------|-------|---------|
| `driver/YourEDRFilter/src/driver.c` | C | 195 | Driver entry, registration, lifecycle |
| `driver/YourEDRFilter/src/filter_operations.c` | C | 329 | File operation callbacks |
| `driver/YourEDRFilter/src/communication.c` | C | 245 | IOCTL device and handlers |
| `driver/YourEDRFilter/src/event_logger.c` | C | 308 | Ring buffer implementation |
| `driver/YourEDRFilter/include/driver.h` | C Header | 138 | Driver declarations and structures |
| `common/include/event_structures.h` | C Header | 123 | Event type definitions |
| `common/include/ioctl_codes.h` | C Header | 108 | IOCTL communication protocol |
| `service/YourEDRService/src/main.cpp` | C++ | 232 | Service entry point |
| `service/YourEDRService/src/service.cpp` | C++ | 173 | Service lifecycle management |
| `service/YourEDRService/src/driver_communicator.cpp` | C++ | 138 | IOCTL client |
| `service/YourEDRService/src/json_logger.cpp` | C++ | 230 | JSON serialization and file I/O |
| `service/YourEDRService/include/service.h` | C++ Header | 58 | Service class declarations |
| `service/YourEDRService/include/driver_communicator.h` | C++ Header | 42 | Communicator class |
| `service/YourEDRService/include/json_logger.h` | C++ Header | 46 | Logger class |

---

**Document End**

**Last Updated**: 2025-11-19
**Maintainer**: Development Team
**Next Review**: After Phase 2 Implementation
