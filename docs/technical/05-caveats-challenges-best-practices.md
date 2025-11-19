# Windows EDR System - Caveats, Challenges & Best Practices

## Document Overview

This document outlines critical caveats, potential challenges, security considerations, and industry best practices for developing a production-grade Windows EDR system with kernel mini-filter drivers. This is essential reading before implementation.

---

## 1. Critical Caveats & Warnings

### 1.1 Kernel-Mode Development Risks

#### ⚠️ System Stability
**Caveat**: A single bug in kernel code can cause:
- Blue Screen of Death (BSOD)
- Data corruption
- Unrecoverable system hang
- Boot loop requiring safe mode recovery

**Impact**: User systems become unusable, potential data loss, reputation damage

**Mitigation**:
- Extensive testing with Driver Verifier
- Comprehensive error handling (structured exception handling)
- Never call pageable functions at DISPATCH_LEVEL
- Always validate pointers before dereferencing
- Use `__try/__except` blocks for all unsafe operations

```c
// WRONG - Can cause BSOD
VOID UnsafeCallback(PVOID Context) {
    PUSER_DATA data = (PUSER_DATA)Context;
    data->field = 123;  // What if Context is NULL or invalid?
}

// CORRECT - Protected
VOID SafeCallback(PVOID Context) {
    __try {
        if (Context == NULL) {
            return;
        }

        if (!MmIsAddressValid(Context)) {
            KdPrint(("Invalid context pointer\n"));
            return;
        }

        PUSER_DATA data = (PUSER_DATA)Context;
        data->field = 123;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        KdPrint(("Exception in callback: 0x%X\n", GetExceptionCode()));
    }
}
```

#### ⚠️ IRQL (Interrupt Request Level) Violations
**Caveat**: Calling pageable code at high IRQL causes instant BSOD (IRQL_NOT_LESS_OR_EQUAL)

**Rules**:
- DISPATCH_LEVEL (2): Cannot access pageable memory, no waiting
- APC_LEVEL (1): Can wait but limited allocations
- PASSIVE_LEVEL (0): Full access to pageable memory

**Common Mistakes**:
```c
// WRONG - Allocating paged pool at DISPATCH_LEVEL
FLT_PREOP_CALLBACK_STATUS PreOperation(...) {
    // This callback runs at DISPATCH_LEVEL!
    PVOID buffer = ExAllocatePoolWithTag(PagedPool, 1024, 'Tag1');  // BSOD!
}

// CORRECT - Use non-paged pool
FLT_PREOP_CALLBACK_STATUS PreOperation(...) {
    PVOID buffer = ExAllocatePoolWithTag(NonPagedPool, 1024, 'Tag1');  // OK
}
```

#### ⚠️ Memory Leaks
**Caveat**: Kernel memory leaks are catastrophic - no automatic cleanup

**Consequences**:
- System gradually exhausts non-paged pool
- Other drivers fail to allocate memory
- System becomes unstable after hours/days of uptime

**Best Practices**:
- Use pool tagging for all allocations: `ExAllocatePoolWithTag(..., 'rdfE')`
- Track allocations in debug builds with counters
- Run Driver Verifier with pool tracking enabled
- Use `!poolused` and `!poolfind` in WinDbg to detect leaks

```powershell
# Enable Driver Verifier with pool tracking
verifier /flags 0x1 /driver YourEDRFilter.sys

# In WinDbg, check for leaks
!poolused 2 'rdfE'
```

### 1.2 Performance Impact Caveats

#### ⚠️ File System Bottlenecks
**Caveat**: File system filters are in the hot path of ALL I/O operations

**Impact**:
- 1ms delay per file operation = 10-50% system slowdown
- Users experience "slow computer" symptoms
- Complaints, uninstallations, negative reviews

**Critical Rules**:
- **Never do synchronous I/O in pre-operation callbacks**
- **Never wait on locks in callbacks** (use spinlocks, not mutexes)
- **Never call user-mode from kernel callbacks** (use work queues)
- **Filter aggressively** - only monitor what's necessary

**Example - What NOT to do**:
```c
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(...) {
    // WRONG: Synchronous network call to check reputation
    NTSTATUS status = HttpCheckFileReputation(fileHash);  // Takes 100ms+!

    // WRONG: Wait on mutex
    KeWaitForMutexObject(&g_ConfigMutex, ...);  // Blocks I/O!

    // WRONG: Complex hash computation
    SHA256_Hash(fileData, fileSize, hashOutput);  // Too slow for hot path!
}

// CORRECT: Defer expensive work
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(...) {
    // Queue work item for background processing
    EDR_WORK_ITEM* workItem = AllocateWorkItem();
    workItem->FilePath = DuplicateString(&nameInfo->Name);
    ExQueueWorkItem(&workItem->WorkItem, DelayedWorkQueue);

    return FLT_PREOP_SUCCESS_NO_CALLBACK;  // Let I/O proceed immediately
}
```

#### ⚠️ CPU Usage - Process Callbacks
**Caveat**: Process creation notifications can fire 100+ times per second on busy systems

**Impact**: Consuming >5% CPU is unacceptable for security products

**Optimization Strategies**:
- Skip system processes (PID 0, 4, Registry)
- Skip known-good publishers (Microsoft-signed binaries)
- Use quick filters before expensive operations
- Batch events to amortize overhead

```c
VOID ProcessNotifyCallback(PEPROCESS Process, HANDLE ProcessId, PPS_CREATE_NOTIFY_INFO CreateInfo) {
    // FAST PATH: Skip system processes immediately
    ULONG pid = HandleToULong(ProcessId);
    if (pid <= 4) return;

    // FAST PATH: Skip if no image path
    if (CreateInfo == NULL || CreateInfo->ImageFileName == NULL) return;

    // FAST PATH: Skip Windows directory (80% of processes)
    if (IsWindowsSystemPath(CreateInfo->ImageFileName)) return;

    // SLOW PATH: Only now do expensive work
    QueueEvent(...);
}
```

#### ⚠️ Network Monitoring - WFP Performance
**Caveat**: Every TCP connection goes through WFP callout

**Concerns**:
- Web browsers create 50+ connections per page load
- Enterprise apps: 1000+ connections/minute
- Callout must complete in <100 microseconds

**Best Practices**:
- Use `FWP_ACTION_PERMIT` (never block unless necessary)
- Avoid per-packet inspection (use connection-level only)
- Cache process information (don't query PID→Name every time)
- Use flow context to track connection state

### 1.3 Security & Anti-Tampering Caveats

#### ⚠️ Driver Unload Attacks
**Caveat**: Admin-level attackers can unload your driver

**Techniques**:
```powershell
# Attacker commands
fltmc unload YourEDRFilter     # Unload filter
sc stop YourEDRService         # Stop service
taskkill /F /IM YourEDRService.exe
```

**Mitigation Strategies**:
1. **Prevent Unload** (Partial):
```c
// In DriverEntry, make unload harder
DriverObject->DriverUnload = NULL;  // Prevent graceful unload

// Or implement unload callback that logs/alerts
NTSTATUS FilterUnload(FLT_FILTER_UNLOAD_FLAGS Flags) {
    // Log critical alert: driver unload attempted
    LogSecurityEvent(EVENT_DRIVER_UNLOAD_ATTEMPT);

    // In production, may want to resist unload
    if (Flags & FLTFL_FILTER_UNLOAD_MANDATORY) {
        // System is shutting down, allow
        return STATUS_SUCCESS;
    }

    // Resist non-mandatory unload
    return STATUS_FLT_DO_NOT_DETACH;
}
```

2. **Monitor for Tampering**:
- Service self-monitoring (heartbeat)
- Driver self-integrity checks (verify loaded driver hash)
- Object Manager callbacks to detect driver object manipulation

3. **Protected Process Light (PPL)** (Advanced):
- Run service as PPL (requires ELAM driver)
- Prevents even admin-level termination
- Requires Microsoft signing and certification

#### ⚠️ Bypass via Alternate Data Streams (ADS)
**Caveat**: File mini-filters may miss ADS accesses

**Example**:
```
file.txt       <- Monitored
file.txt:hidden <- May be missed if not handled
```

**Solution**: Check for `:` in file paths, handle `$DATA` stream explicitly

#### ⚠️ Time-of-Check to Time-of-Use (TOCTOU) Races
**Caveat**: File attributes can change between pre-operation and post-operation

**Scenario**:
1. PreCreate: Check file path → `C:\safe\file.exe`
2. Attacker: Rename during I/O
3. PostCreate: File opened → actually `C:\malware\file.exe`

**Mitigation**: Use file object tracking, not paths

---

## 2. Major Technical Challenges

### 2.1 Challenge: Reliable Event Ordering

**Problem**: Events from different sources (file, process, network) arrive out-of-order

**Example**:
```
Time 0: Process foo.exe created (PID 1234)
Time 1: foo.exe creates file C:\temp\data.txt
Time 2: foo.exe makes network connection to 1.2.3.4

Possible arrival order:
  Network event (PID 1234) arrives BEFORE process creation event!
  → Service doesn't know what PID 1234 is yet
```

**Solutions**:
1. **Process Cache**: Maintain PID→Name cache, pre-populate with existing processes
2. **Event Sequencing**: Add global sequence numbers, reorder in user-mode
3. **Delayed Processing**: Buffer events for 100ms, sort by timestamp
4. **Lazy Resolution**: Store PID, resolve to name later during analysis

### 2.2 Challenge: High-Frequency Event Filtering

**Problem**: Need to decide in <1 microsecond whether to capture event

**Requirements**:
- Path whitelisting: `C:\Windows\System32\*` → skip
- Process whitelisting: `svchost.exe` → skip
- Extension filtering: `*.txt` → skip

**Naive Approach** (Slow):
```c
BOOLEAN ShouldSkipFile(PUNICODE_STRING Path) {
    // String comparison on every I/O = too slow!
    if (wcsstr(Path->Buffer, L"\\Windows\\System32\\")) return TRUE;
    if (wcsstr(Path->Buffer, L"\\Program Files\\")) return TRUE;
    // ... more comparisons
}
```

**Optimized Approach**:
```c
// Use prefix tree (trie) for path matching
typedef struct _PATH_TRIE_NODE {
    WCHAR Character;
    BOOLEAN IsTerminal;  // End of exclusion path
    struct _PATH_TRIE_NODE* Children[256];
} PATH_TRIE_NODE;

// Pre-build at driver load, O(n) lookup
BOOLEAN IsExcludedPath(PUNICODE_STRING Path) {
    PATH_TRIE_NODE* node = &g_RootNode;
    for (USHORT i = 0; i < Path->Length / sizeof(WCHAR); i++) {
        WCHAR c = Path->Buffer[i];
        node = node->Children[c % 256];
        if (node == NULL) return FALSE;
        if (node->IsTerminal) return TRUE;
    }
    return FALSE;
}
```

### 2.3 Challenge: Memory Management Under Stress

**Problem**: Non-paged pool is limited (typically 200-500 MB)

**Scenarios**:
- Burst of 10,000 events/second → 20 MB/second allocation
- Ring buffer fills → events dropped
- Memory pressure → system instability

**Best Practices**:
1. **Pre-Allocate**: Reserve buffers at driver load
```c
// Allocate pool at startup
PVOID g_PreAllocatedBuffers[100];
for (int i = 0; i < 100; i++) {
    g_PreAllocatedBuffers[i] = ExAllocatePoolWithTag(NonPagedPool, 4096, 'fubE');
}

// Use lock-free stack for fast allocation
PVOID AllocateEventBuffer() {
    return PopFromLockFreeStack(&g_BufferStack);
}
```

2. **Lookaside Lists**: Use Windows kernel allocator optimizations
```c
NPAGED_LOOKASIDE_LIST g_EventLookasideList;

// Initialize in DriverEntry
ExInitializeNPagedLookasideList(
    &g_EventLookasideList,
    NULL, NULL,
    0,
    sizeof(EDR_FILE_EVENT),
    'evfE',
    0
);

// Fast allocation
PEDR_FILE_EVENT AllocateEvent() {
    return (PEDR_FILE_EVENT)ExAllocateFromNPagedLookasideList(&g_EventLookasideList);
}
```

3. **Adaptive Sampling**: Drop low-priority events under memory pressure
```c
if (g_MemoryPressureLevel > 80) {
    // Drop verbose file read events, keep only creates/writes
    if (eventType == EventTypeFileRead) {
        InterlockedIncrement(&g_EventsDroppedDueToPressure);
        return STATUS_SUCCESS;  // Don't queue
    }
}
```

### 2.4 Challenge: Debugging Kernel Crashes

**Problem**: Kernel debugger setup is complex, crashes are hard to reproduce

**Best Practices**:

#### Local Kernel Debugging (Hyper-V)
```powershell
# On host machine
bcdedit /set hypervisorlaunchtype auto
bcdedit /dbgsettings serial debugport:1 baudrate:115200

# Create named pipe for debugging
# In Hyper-V VM settings → COM1 → Named Pipe: \\.\pipe\edr-debug

# Launch WinDbg
windbgx -k com:pipe,port=\\.\pipe\edr-debug,resets=0
```

#### Live Kernel Debugging (Network - Best for Production)
```powershell
# On target machine
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.1.100 port:50000 key:1.2.3.4

# On debugger machine
windbgx -k net:port=50000,key=1.2.3.4
```

#### Analyzing Crash Dumps
```
# In WinDbg after loading crash dump
!analyze -v        # Automatic analysis
kv                 # Stack trace
!process 0 0       # All processes
!drivers           # Loaded drivers
!poolused 2        # Pool usage by tag

# Driver-specific commands
!fltkd.filters     # List filter drivers
!fltkd.filter <address>  # Your filter details
```

#### Essential Debugging Macros
```c
// Debug print with function name and line number
#define EDR_DBG_PRINT(fmt, ...) \
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, \
               "[EDR] %s:%d - " fmt "\n", __FUNCTION__, __LINE__, __VA_ARGS__)

// Assert that doesn't crash in production
#define EDR_ASSERT(expr) \
    if (!(expr)) { \
        EDR_DBG_PRINT("ASSERTION FAILED: %s", #expr); \
        if (KdDebuggerEnabled) { \
            DbgBreakPoint(); \
        } \
    }
```

### 2.5 Challenge: Driver Signing & Distribution

**Problem**: Microsoft's signing process is slow and strict

**Timeline**:
- EV certificate acquisition: 1-3 weeks
- Hardware Dev Center account setup: 2-3 days
- First driver submission: 2-5 business days
- WHQL certification: 1-2 weeks

**Challenges**:
1. **Static Analysis Failures**: Microsoft runs SDV (Static Driver Verifier)
   - Common issues: Missing annotations, buffer overflows
   - Solution: Run SDV locally before submission

2. **Test Failures**: HLK tests must pass 100%
   - Common issues: IOCTL validation, PnP behavior
   - Solution: Run HLK locally, fix all issues first

3. **Attestation vs. WHQL**:
   - **Attestation** (Fast): Sign without full testing, limited distribution
   - **WHQL** (Slow): Full certification, Windows Update eligible
   - Recommendation: Use attestation for early testing, WHQL for production

**Submission Checklist**:
```
[ ] Driver passes Static Driver Verifier (SDV) with no errors
[ ] Driver passes Driver Verifier on multiple test systems (48+ hours)
[ ] All HLK tests passed and logs generated
[ ] INF file follows best practices (no hardcoded paths)
[ ] No test/debug code in release binary
[ ] Code signing with EV certificate
[ ] Catalog file (.cat) generated with Inf2Cat
[ ] Driver submission package (.hlkx) created
[ ] Hardware Dev Center portal account configured
```

---

## 3. Best Practices for Production EDR

### 3.1 Code Quality & Safety

#### Rule 1: Fail Safe, Never Fail Open
```c
// WRONG: Block on error
if (!IsFileSafe(filePath)) {
    return STATUS_ACCESS_DENIED;  // System breaks if your code fails!
}

// CORRECT: Allow on error (security reduced, but system works)
BOOLEAN isSafe = TRUE;  // Default to safe
NTSTATUS status = IsFileSafe(filePath, &isSafe);
if (NT_SUCCESS(status) && !isSafe) {
    return STATUS_ACCESS_DENIED;
}
return STATUS_SUCCESS;  // Error? Let it through with warning
```

#### Rule 2: Validate All Input
```c
NTSTATUS HandleIoctlMessage(PVOID InputBuffer, ULONG InputLength, ...) {
    // ALWAYS validate size first
    if (InputLength < sizeof(MESSAGE_HEADER)) {
        return STATUS_INVALID_PARAMETER;
    }

    PMESSAGE_HEADER header = (PMESSAGE_HEADER)InputBuffer;

    // Validate magic number (detect corruption)
    if (header->Magic != EXPECTED_MAGIC) {
        return STATUS_INVALID_PARAMETER;
    }

    // Validate message type range
    if (header->MessageType < MSG_MIN || header->MessageType > MSG_MAX) {
        return STATUS_INVALID_PARAMETER;
    }

    // Validate variable-length fields
    if (header->DataOffset + header->DataSize > InputLength) {
        return STATUS_BUFFER_TOO_SMALL;
    }

    // Now safe to process
    ProcessMessage(header);
}
```

#### Rule 3: Use SAL Annotations (Source Annotation Language)
```c
// Annotate function parameters for static analysis
NTSTATUS CopyUserString(
    _In_ PUNICODE_STRING Source,           // Must not be NULL
    _Out_ PUNICODE_STRING Destination,     // Output parameter
    _In_ POOL_TYPE PoolType                // Input parameter
)
{
    _Analysis_assume_(Source != NULL);
    _Analysis_assume_(Source->Buffer != NULL);

    // Allocate destination buffer
    Destination->Length = 0;
    Destination->MaximumLength = Source->Length;
    Destination->Buffer = ExAllocatePoolWithTag(
        PoolType,
        Source->Length,
        'rtsE'
    );

    if (Destination->Buffer == NULL) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    // Copy string
    RtlCopyMemory(Destination->Buffer, Source->Buffer, Source->Length);
    Destination->Length = Source->Length;

    return STATUS_SUCCESS;
}
```

### 3.2 Performance Best Practices

#### Benchmark-Driven Optimization
```c
// Measure callback performance
LARGE_INTEGER startTime, endTime;
KeQuerySystemTime(&startTime);

// Your code here
ProcessEvent(...);

KeQuerySystemTime(&endTime);
LONGLONG elapsedMicroseconds = (endTime.QuadPart - startTime.QuadPart) / 10;

// Collect statistics
InterlockedIncrement(&g_CallbackCount);
InterlockedAdd64(&g_TotalExecutionTime, elapsedMicroseconds);

// Alert if callback is too slow
if (elapsedMicroseconds > 100) {  // >100 microseconds
    KdPrint(("WARNING: Slow callback: %lld us\n", elapsedMicroseconds));
}
```

#### Telemetry for Optimization
```c
typedef struct _PERFORMANCE_COUNTERS {
    ULONG64 TotalEvents;
    ULONG64 EventsDropped;
    ULONG64 FastPathHits;         // Events filtered quickly
    ULONG64 SlowPathHits;         // Events requiring full processing
    ULONG64 AverageCallbackTime;  // Microseconds
    ULONG64 MaxCallbackTime;
    ULONG64 MemoryUsageBytes;
} PERFORMANCE_COUNTERS;

// Expose via IOCTL for monitoring
NTSTATUS GetPerformanceCounters(PPERFORMANCE_COUNTERS Counters) {
    Counters->TotalEvents = InterlockedRead64(&g_Stats.TotalEvents);
    Counters->EventsDropped = InterlockedRead64(&g_Stats.EventsDropped);
    // ... populate other fields
    return STATUS_SUCCESS;
}
```

### 3.3 Operational Best Practices

#### Graceful Degradation Strategy
```
Priority 1 (Critical): Process monitoring
  → If fails: Log error, continue with other monitors

Priority 2 (Important): File monitoring
  → If fails: Disable file monitoring, keep process/network

Priority 3 (Useful): Network monitoring
  → If fails: Disable network monitoring, keep others

Priority 4 (Optional): Registry monitoring (future)
  → If fails: Disable, no impact on core functionality
```

#### Logging Strategy (ETW - Event Tracing for Windows)
```c
// Register ETW provider in DriverEntry
#include <evntprov.h>

REGHANDLE g_EtwRegHandle = 0;

NTSTATUS RegisterEtwProvider() {
    NTSTATUS status = EventRegister(
        &EDR_ETW_PROVIDER_GUID,
        NULL,  // Callback
        NULL,  // Context
        &g_EtwRegHandle
    );
    return status;
}

// Log events via ETW (visible in Event Viewer and tracers)
VOID LogEtwEvent(UCHAR Level, PCWSTR Message) {
    if (g_EtwRegHandle != 0) {
        EventWriteString(g_EtwRegHandle, Level, 0, Message);
    }
}

// Usage
LogEtwEvent(TRACE_LEVEL_ERROR, L"Failed to allocate event buffer");
```

#### Configuration Management
```c
// Store config in registry, validate on load
#define CONFIG_KEY L"\\Registry\\Machine\\SOFTWARE\\YourEDR"

NTSTATUS LoadConfiguration() {
    OBJECT_ATTRIBUTES oa;
    UNICODE_STRING keyPath;
    HANDLE keyHandle;

    RtlInitUnicodeString(&keyPath, CONFIG_KEY);
    InitializeObjectAttributes(&oa, &keyPath, OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE, NULL, NULL);

    NTSTATUS status = ZwOpenKey(&keyHandle, KEY_READ, &oa);
    if (!NT_SUCCESS(status)) {
        // Config not found, use defaults
        UseDefaultConfiguration();
        return STATUS_SUCCESS;
    }

    // Read values
    ReadRegistryValue(keyHandle, L"EnableFileMonitoring", &g_Config.EnableFileMonitoring);
    ReadRegistryValue(keyHandle, L"RingBufferSizeMB", &g_Config.RingBufferSize);

    ZwClose(keyHandle);
    return STATUS_SUCCESS;
}
```

### 3.4 Security Best Practices

#### Principle of Least Privilege
```c
// Don't require more privileges than necessary
// Example: User-mode service doesn't need SeDebugPrivilege for basic operation

// Only elevate when needed
NTSTATUS EnableDebugPrivilege() {
    HANDLE tokenHandle;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &tokenHandle)) {
        return STATUS_UNSUCCESSFUL;
    }

    TOKEN_PRIVILEGES tp;
    tp.PrivilegeCount = 1;
    LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid);
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    AdjustTokenPrivileges(tokenHandle, FALSE, &tp, sizeof(tp), NULL, NULL);
    CloseHandle(tokenHandle);

    return GetLastError() == ERROR_SUCCESS ? STATUS_SUCCESS : STATUS_UNSUCCESSFUL;
}
```

#### Input Validation (Defense in Depth)
```c
// Validate in BOTH kernel and user-mode
// Example: File path validation

// Kernel: Validate length and characters
BOOLEAN IsValidFilePath(PUNICODE_STRING Path) {
    if (Path == NULL || Path->Buffer == NULL) return FALSE;
    if (Path->Length == 0 || Path->Length > 32767) return FALSE;  // Max path

    // Check for invalid characters (examples, not exhaustive)
    for (USHORT i = 0; i < Path->Length / sizeof(WCHAR); i++) {
        WCHAR c = Path->Buffer[i];
        if (c < 32 || c == L'<' || c == L'>' || c == L'|') {
            return FALSE;  // Invalid character
        }
    }

    return TRUE;
}

// User-mode: Additional validation (filesystem checks)
bool IsPathSafe(const std::wstring& path) {
    // Check if path is absolute
    if (path.length() < 3 || path[1] != L':') return false;

    // Resolve to canonical form (prevent ../ tricks)
    wchar_t canonical[MAX_PATH];
    if (!PathCanonicalizeW(canonical, path.c_str())) return false;

    // Check against whitelist
    if (wcsncmp(canonical, L"C:\\Program Files\\", 17) == 0) {
        // Protected path, need admin approval
        return false;
    }

    return true;
}
```

#### Secure Coding Checklist
```
[ ] All allocations have corresponding frees (no leaks)
[ ] All error paths release resources (use RAII pattern)
[ ] No hardcoded credentials or secrets
[ ] All IOCTL handlers validate input size
[ ] No unbounded loops or recursion
[ ] All string operations use safe functions (RtlStringCb*, not strcpy)
[ ] No use-after-free vulnerabilities
[ ] All shared data protected by appropriate synchronization
[ ] No trust in user-mode input (validate everything)
[ ] Secrets (if any) stored encrypted, not plaintext
```

---

## 4. Common Pitfalls & How to Avoid

### Pitfall 1: Forgetting to Release Context
```c
// WRONG
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(...) {
    PFLT_FILE_NAME_INFORMATION nameInfo;
    FltGetFileNameInformation(Data, ..., &nameInfo);

    if (someCondition) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;  // LEAKED nameInfo!
    }

    FltReleaseFileNameInformation(nameInfo);
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// CORRECT
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(...) {
    PFLT_FILE_NAME_INFORMATION nameInfo = NULL;
    NTSTATUS status = FltGetFileNameInformation(Data, ..., &nameInfo);

    if (!NT_SUCCESS(status)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    // ... use nameInfo ...

    // ALWAYS release before ALL return paths
    if (nameInfo != NULL) {
        FltReleaseFileNameInformation(nameInfo);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}
```

### Pitfall 2: Not Handling Volume Mount/Dismount
```c
// Implement instance callbacks
NTSTATUS InstanceSetup(
    PCFLT_RELATED_OBJECTS FltObjects,
    FLT_INSTANCE_SETUP_FLAGS Flags,
    DEVICE_TYPE VolumeDeviceType,
    FLT_FILESYSTEM_TYPE VolumeFilesystemType
)
{
    // Only attach to local disks, not network or removable
    if (VolumeDeviceType != FILE_DEVICE_DISK_FILE_SYSTEM) {
        return STATUS_FLT_DO_NOT_ATTACH;
    }

    // Skip attaching to non-NTFS (optional, depends on requirements)
    if (VolumeFilesystemType != FLT_FSTYPE_NTFS) {
        return STATUS_FLT_DO_NOT_ATTACH;
    }

    KdPrint(("EDR: Attached to volume\n"));
    return STATUS_SUCCESS;
}
```

### Pitfall 3: Assuming Process ID Uniqueness
```c
// WRONG: PIDs can be reused!
HANDLE g_SuspiciousProcessPID = (HANDLE)1234;

if (CurrentProcessId == g_SuspiciousProcessPID) {
    // This might be a DIFFERENT process now!
    TerminateProcess(...);  // Killed innocent process!
}

// CORRECT: Use process object, not PID
PEPROCESS g_SuspiciousProcess = NULL;

// When marking suspicious, reference the object
ObReferenceObject(Process);
g_SuspiciousProcess = Process;

// When checking
if (CurrentProcess == g_SuspiciousProcess) {
    // Same object, guaranteed same process
    TerminateProcess(...);
}

// When done, dereference
ObDereferenceObject(g_SuspiciousProcess);
```

---

## 5. Testing & Quality Assurance Best Practices

### 5.1 Testing Levels

| Level | Tool/Method | Coverage | Duration |
|-------|-------------|----------|----------|
| **Unit** | WDK test framework | Individual functions | Minutes |
| **Integration** | Custom test app | Driver ↔ Service communication | Hours |
| **System** | Manual scenarios | Full EDR functionality | Days |
| **Stress** | Driver Verifier + load generators | Stability, leaks, performance | 48+ hours |
| **Security** | Fuzzing, penetration testing | Attack resistance | Weeks |

### 5.2 Stress Testing Script
```powershell
# stress-test.ps1
param(
    [int]$DurationHours = 48
)

Write-Host "Starting $DurationHours hour stress test..."

# Enable Driver Verifier
verifier /standard /driver YourEDRFilter.sys

# Start file I/O stress
Start-Job {
    while ($true) {
        Get-ChildItem -Recurse C:\Windows\System32 -ErrorAction SilentlyContinue | Out-Null
        Start-Sleep -Seconds 1
    }
}

# Start process stress
Start-Job {
    while ($true) {
        Start-Process cmd.exe -ArgumentList "/c exit" -NoNewWindow -Wait
        Start-Sleep -Milliseconds 100
    }
}

# Start network stress
Start-Job {
    while ($true) {
        Test-NetConnection -ComputerName google.com -Port 80 -InformationLevel Quiet
        Start-Sleep -Seconds 2
    }
}

# Monitor for crashes
$endTime = (Get-Date).AddHours($DurationHours)
while ((Get-Date) -lt $endTime) {
    # Check for crash dumps
    $dumps = Get-ChildItem C:\Windows\Minidump -ErrorAction SilentlyContinue
    if ($dumps) {
        Write-Host "CRASH DETECTED! Stopping test."
        Stop-Job *
        exit 1
    }

    # Check CPU usage
    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    Write-Host "CPU: $cpu%, Memory: $((Get-Process YourEDRService).WorkingSet64 / 1MB) MB"

    Start-Sleep -Seconds 60
}

Write-Host "Stress test completed successfully!"
Stop-Job *
verifier /reset
```

---

## 6. Deployment & Rollout Best Practices

### 6.1 Phased Rollout Strategy

```
Phase 1: Internal Testing (1-2 weeks)
  - Deploy to 10 developer machines
  - Monitor closely, fix critical bugs
  - Success criteria: No BSODs, <3% CPU usage

Phase 2: Alpha Testing (2-4 weeks)
  - Deploy to 100 internal employees
  - Collect telemetry, identify edge cases
  - Success criteria: <0.1% crash rate, no data corruption

Phase 3: Beta Testing (4-8 weeks)
  - Deploy to 1,000 friendly customers
  - Offer support, gather feedback
  - Success criteria: Positive feedback, <0.01% crash rate

Phase 4: General Availability
  - Gradual rollout: 1% → 10% → 50% → 100%
  - Monitor support tickets, crash reports
  - Rollback plan ready if issues detected
```

### 6.2 Rollback Plan
```powershell
# rollback-driver.ps1
Write-Host "Rolling back to previous driver version..."

# Stop service
Stop-Service YourEDRService -Force

# Unload driver
fltmc unload YourEDRFilter

# Restore previous driver
Copy-Item C:\Backup\YourEDRFilter.sys C:\Windows\System32\drivers\ -Force

# Restart service
Start-Service YourEDRService

Write-Host "Rollback complete. Please reboot if issues persist."
```

---

## 7. Summary of Critical Best Practices

### Top 10 Rules for EDR Driver Development

1. **Never Block I/O** - Use post-operation callbacks or work queues for expensive operations
2. **Validate Everything** - Never trust pointers, sizes, or user input
3. **Handle All Errors** - Every allocation, every function call, every I/O
4. **Test with Driver Verifier** - Always, for at least 48 hours
5. **Monitor Performance** - <2% CPU average, <100 microseconds per callback
6. **Protect Against Unload** - Log attempts, consider PPL for production
7. **Use ETW for Logging** - Better than DbgPrint, production-safe
8. **Fail Safe** - If your code fails, let the system continue (don't block)
9. **Sign Everything** - Even test builds (prevents signing bypass attacks)
10. **Plan for Rollback** - Always have a way to disable/uninstall remotely

### Key Takeaways

- **Kernel development is high-risk**: One mistake = system crash
- **Performance is critical**: Users will uninstall slow security products
- **Security is paramount**: Attackers will try to bypass/disable your EDR
- **Testing is non-negotiable**: 48+ hour stress tests, Driver Verifier mandatory
- **Signing is complex**: Start EV cert process early (3-week lead time)

This document should be reviewed by all team members before starting implementation. Good luck building a robust, production-grade EDR system!
