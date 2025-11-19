# Windows EDR System - Component Breakdown and Flow Diagrams

## Document Overview

This document provides detailed component breakdowns, sequence diagrams, and data flow specifications for the Windows EDR system. It serves as a technical reference for understanding inter-component communication and event lifecycle.

---

## 1. System Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER MODE (Ring 3)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Management & Control Plane                      │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ PowerShell  │  │   Web API    │  │  Event Viewer  │  │  │
│  │  │   Module    │  │   (Future)   │  │   Integration  │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              YourEDR Service (Main Process)               │  │
│  │                                                            │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │  │
│  │  │ Driver Comm    │  │  Event         │  │  Config    │ │  │
│  │  │ Manager        │→ │  Processor     │→ │  Manager   │ │  │
│  │  └────────────────┘  └────────────────┘  └────────────┘ │  │
│  │           ↓                  ↓                    ↓       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │  │
│  │  │ IOCTL Handler  │  │ JSON Serializer│  │  Registry  │ │  │
│  │  └────────────────┘  └────────────────┘  └────────────┘ │  │
│  │           ↓                  ↓                            │  │
│  │  ┌────────────────┐  ┌────────────────┐                 │  │
│  │  │  Ring Buffer   │  │  File Rotator  │                 │  │
│  │  │   Consumer     │  └────────────────┘                 │  │
│  │  └────────────────┘          ↓                           │  │
│  │                       ┌────────────────┐                 │  │
│  │                       │ JSONL Files    │                 │  │
│  │                       │ (Disk Storage) │                 │  │
│  │                       └────────────────┘                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               ↕                                  │
│                        [IOCTL Channel]                           │
│                        [Shared Memory]                           │
└─────────────────────────────────────────────────────────────────┘
═══════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────┐
│                        KERNEL MODE (Ring 0)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           YourEDRFilter.sys (Mini-Filter Driver)          │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  Filter Mgr  │  │   Process    │  │   Network    │   │  │
│  │  │  Callbacks   │  │   Monitor    │  │   Monitor    │   │  │
│  │  │              │  │              │  │   (WFP)      │   │  │
│  │  │ • PreCreate  │  │ • PsSetCreate│  │ • Callouts   │   │  │
│  │  │ • PostCreate │  │   Process    │  │ • Layer Mgmt │   │  │
│  │  │ • PreWrite   │  │ • ImageLoad  │  │              │   │  │
│  │  │ • PreSetInfo │  │ • ThreadNtfy │  │              │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │         ↓                 ↓                   ↓           │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │        Event Collection & Queuing Layer         │    │  │
│  │  │                                                  │    │  │
│  │  │  • Event normalization                          │    │  │
│  │  │  • Metadata extraction                          │    │  │
│  │  │  • Filtering logic                              │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                         ↓                                 │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │          Ring Buffer (Lock-Free SPSC)           │    │  │
│  │  │                                                  │    │  │
│  │  │  [Write Ptr] ───→ [Events] ───→ [Read Ptr]     │    │  │
│  │  │                                                  │    │  │
│  │  │  • 2MB circular buffer                          │    │  │
│  │  │  • Atomic operations                            │    │  │
│  │  │  • Overflow protection                          │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  │                         ↓                                 │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │        Communication Port (FltMgr)              │    │  │
│  │  │                                                  │    │  │
│  │  │  • IOCTL dispatch                               │    │  │
│  │  │  • Message handlers                             │    │  │
│  │  │  • Client management                            │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               ↕                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Windows Kernel Subsystems                      │  │
│  │                                                            │  │
│  │  • Filter Manager (FltMgr.sys)                            │  │
│  │  • I/O Manager (ntoskrnl.exe)                             │  │
│  │  • Process/Thread Manager                                 │  │
│  │  • Windows Filtering Platform (netio.sys)                 │  │
│  │  • TCP/IP Stack (tcpip.sys)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Event Capture Flow - Detailed Sequence Diagrams

### 2.1 File System Event Flow

```
User App          NT Kernel        FltMgr         YourEDRFilter      Ring Buffer      EDR Service
   │                  │               │                  │                │                │
   │ CreateFile()     │               │                  │                │                │
   ├─────────────────>│               │                  │                │                │
   │                  │ IRP_MJ_CREATE │                  │                │                │
   │                  ├──────────────>│                  │                │                │
   │                  │               │ PreCreate()      │                │                │
   │                  │               ├─────────────────>│                │                │
   │                  │               │                  │ Extract:       │                │
   │                  │               │                  │ • FilePath     │                │
   │                  │               │                  │ • ProcessID    │                │
   │                  │               │                  │ • Access Flags │                │
   │                  │               │                  │ • Timestamp    │                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Queue Event    │                │
   │                  │               │                  ├───────────────>│                │
   │                  │               │                  │                │ [Event stored] │
   │                  │               │                  │                │                │
   │                  │               │                  │                │ Signal Event   │
   │                  │               │                  │                ├───────────────>│
   │                  │               │                  │                │                │
   │                  │               │ FLT_PREOP_       │                │                │
   │                  │               │ SUCCESS          │                │                │
   │                  │               │<─────────────────┤                │                │
   │                  │ Continue IRP  │                  │                │                │
   │                  │<──────────────┤                  │                │                │
   │                  │               │                  │                │ IOCTL: GET_    │
   │                  │               │                  │                │ EVENTS         │
   │                  │               │                  │<───────────────┼────────────────┤
   │                  │               │                  │                │                │
   │                  │               │                  │ Read Events    │                │
   │                  │               │                  ├───────────────>│                │
   │                  │               │                  │ [Copy to User] │                │
   │                  │               │                  │<───────────────┤                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Return Events  │                │
   │                  │               │                  ├───────────────────────────────>│
   │                  │               │                  │                │                │
   │ Handle           │               │                  │                │ Parse & Serialize
   │<─────────────────┤               │                  │                │ to JSON        │
   │                  │               │                  │                │                │
   │                  │               │                  │                │ Write to File  │
   │                  │               │                  │                │ (events.jsonl) │
```

### 2.2 Process Creation Event Flow

```
System            NT Kernel        Process CB       YourEDRFilter      Ring Buffer      EDR Service
   │                  │               │                  │                │                │
   │ CreateProcess()  │               │                  │                │                │
   ├─────────────────>│               │                  │                │                │
   │                  │ NtCreateUserProcess             │                │                │
   │                  │ (internal)    │                  │                │                │
   │                  │               │                  │                │                │
   │                  │ Notify        │                  │                │                │
   │                  │ Callbacks     │                  │                │                │
   │                  ├──────────────>│ ProcessNotify()  │                │                │
   │                  │               ├─────────────────>│                │                │
   │                  │               │                  │ Extract:       │                │
   │                  │               │                  │ • PID/PPID     │                │
   │                  │               │                  │ • ImagePath    │                │
   │                  │               │                  │ • CommandLine  │                │
   │                  │               │                  │ • User SID     │                │
   │                  │               │                  │ • Timestamp    │                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Compute Hash   │                │
   │                  │               │                  │ (SHA256)       │                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Queue Event    │                │
   │                  │               │                  ├───────────────>│                │
   │                  │               │                  │                │ [Event stored] │
   │                  │               │                  │                │                │
   │                  │               │                  │                │ Signal Event   │
   │                  │               │                  │                ├───────────────>│
   │                  │               │ Return           │                │                │
   │                  │               │<─────────────────┤                │                │
   │                  │               │                  │                │ Read & Process │
   │                  │               │                  │                │                │
   │ Process Handle   │               │                  │                │ Log to JSON    │
   │<─────────────────┤               │                  │                │                │
```

### 2.3 Network Connection Event Flow

```
User App          Winsock        TCP/IP Stack     WFP Engine       YourEDRFilter      Ring Buffer
   │                  │               │                  │                │                │
   │ connect()        │               │                  │                │                │
   ├─────────────────>│               │                  │                │                │
   │                  │ WSAConnect()  │                  │                │                │
   │                  ├──────────────>│                  │                │                │
   │                  │               │ TCP SYN          │                │                │
   │                  │               │ (prepare)        │                │                │
   │                  │               │                  │                │                │
   │                  │               │ WFP: ALE_AUTH_   │                │                │
   │                  │               │ CONNECT Layer    │                │                │
   │                  │               ├─────────────────>│                │                │
   │                  │               │                  │ NetworkCallout │                │
   │                  │               │                  │ Classify()     │                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Extract:       │                │
   │                  │               │                  │ • ProcessID    │                │
   │                  │               │                  │ • Local IP:Port│                │
   │                  │               │                  │ • Remote IP:Port│               │
   │                  │               │                  │ • Protocol     │                │
   │                  │               │                  │ • Direction    │                │
   │                  │               │                  │                │                │
   │                  │               │                  │ Queue Event    │                │
   │                  │               │                  ├───────────────>│                │
   │                  │               │                  │                │                │
   │                  │               │ FWP_ACTION_      │                │                │
   │                  │               │ PERMIT           │                │                │
   │                  │               │<─────────────────┤                │                │
   │                  │               │                  │                │                │
   │                  │               │ TCP SYN sent     │                │                │
   │                  │               │ (on wire)        │                │                │
   │                  │               │                  │                │                │
   │ Connection       │               │                  │                │ EDR Service    │
   │ established      │               │                  │                │ reads event    │
   │<─────────────────┴───────────────┘                  │                │                │
```

---

## 3. Communication Channel Details

### 3.1 IOCTL Interface Specification

#### Message Types

| IOCTL Code | Name | Direction | Purpose |
|------------|------|-----------|---------|
| 0x8001 | `MSG_GET_EVENTS` | Service → Driver | Retrieve queued events from ring buffer |
| 0x8002 | `MSG_SET_CONFIG` | Service → Driver | Update filter configuration |
| 0x8003 | `MSG_GET_STATS` | Service → Driver | Query performance statistics |
| 0x8004 | `MSG_REGISTER_CLIENT` | Service → Driver | Register user-mode client |
| 0x8005 | `MSG_HEARTBEAT` | Service → Driver | Keep-alive signal |

#### Request/Response Format

**MSG_GET_EVENTS Request:**
```c
typedef struct _GET_EVENTS_REQUEST {
    ULONG MessageType;      // 0x8001
    ULONG MaxEvents;        // Max events to retrieve
    ULONG TimeoutMs;        // Wait timeout (0 = non-blocking)
} GET_EVENTS_REQUEST;
```

**MSG_GET_EVENTS Response:**
```c
typedef struct _GET_EVENTS_RESPONSE {
    ULONG EventCount;       // Number of events returned
    ULONG TotalSize;        // Total size in bytes
    ULONG EventsDropped;    // Overflow counter
    BYTE Events[1];         // Variable-length event array
} GET_EVENTS_RESPONSE;
```

**MSG_SET_CONFIG Request:**
```c
typedef struct _SET_CONFIG_REQUEST {
    ULONG MessageType;      // 0x8002
    ULONG ConfigSize;       // Size of configuration data
    BYTE ConfigData[1];     // JSON or binary config
} SET_CONFIG_REQUEST;
```

### 3.2 Ring Buffer Protocol

#### Buffer Layout
```
┌──────────────────────────────────────────────────────────┐
│                     Ring Buffer Header                    │
├──────────────────────────────────────────────────────────┤
│  ULONG BufferSize        // Total buffer size (power of 2)│
│  ULONG WriteOffset       // Producer write position       │
│  ULONG ReadOffset        // Consumer read position        │
│  ULONG EventsDropped     // Overflow counter              │
│  KSPIN_LOCK SpinLock     // Synchronization primitive     │
│  KEVENT DataAvailable    // Notification event            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                     Event Data Area                       │
│                    (Circular Buffer)                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  [Event 1: Header + Data][Event 2][Event 3]...           │
│  ↑                                          ↑             │
│  ReadOffset                                 WriteOffset   │
│                                                            │
│  ← Wraps around when WriteOffset >= BufferSize →         │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

#### Producer (Kernel Driver) Algorithm
```
1. Acquire SpinLock
2. Calculate available space:
   if (WriteOffset >= ReadOffset):
       available = BufferSize - (WriteOffset - ReadOffset) - 1
   else:
       available = ReadOffset - WriteOffset - 1

3. If (EventSize > available):
       Increment EventsDropped
       Release SpinLock
       Return STATUS_BUFFER_OVERFLOW

4. Copy event to buffer:
   if (WriteOffset + EventSize <= BufferSize):
       memcpy(Buffer + WriteOffset, Event, EventSize)
   else:  // Wrap around
       firstPart = BufferSize - WriteOffset
       memcpy(Buffer + WriteOffset, Event, firstPart)
       memcpy(Buffer, Event + firstPart, EventSize - firstPart)

5. Update WriteOffset:
   WriteOffset = (WriteOffset + EventSize) % BufferSize

6. Release SpinLock
7. Signal DataAvailable event
```

#### Consumer (User-Mode Service) Algorithm
```
1. Wait on DataAvailable event (or poll)
2. Send IOCTL_GET_EVENTS to driver
3. Driver acquires SpinLock
4. Calculate readable data:
   if (WriteOffset >= ReadOffset):
       dataSize = WriteOffset - ReadOffset
   else:
       dataSize = (BufferSize - ReadOffset) + WriteOffset

5. Copy events to user-mode buffer:
   if (ReadOffset + dataSize <= BufferSize):
       memcpy(UserBuffer, Buffer + ReadOffset, dataSize)
   else:  // Wrap around
       firstPart = BufferSize - ReadOffset
       memcpy(UserBuffer, Buffer + ReadOffset, firstPart)
       memcpy(UserBuffer + firstPart, Buffer, dataSize - firstPart)

6. Update ReadOffset:
   ReadOffset = (ReadOffset + dataSize) % BufferSize

7. Release SpinLock
8. Return data to user-mode
```

---

## 4. Event Lifecycle State Machine

```
┌─────────────┐
│  Event      │
│  Occurs     │
│  (System)   │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│  Kernel Callback    │
│  Triggered          │
│  • PreCreate        │
│  • ProcessNotify    │
│  • WFP Classify     │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐      ┌──────────────┐
│  Apply Filters      │─────>│  Skip Event  │
│  • Path exclusions  │  No  │  (Return)    │
│  • Process whitelist│      └──────────────┘
└──────┬──────────────┘
       │ Yes
       v
┌─────────────────────┐
│  Extract Metadata   │
│  • PID, TID         │
│  • Paths, IPs       │
│  • Timestamps       │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐      ┌──────────────┐
│  Queue to Ring      │─────>│  Overflow    │
│  Buffer             │  Full │  Drop Event  │
│                     │      │  Increment   │
│                     │      │  Counter     │
└──────┬──────────────┘      └──────────────┘
       │ Success
       v
┌─────────────────────┐
│  Signal User-Mode   │
│  (KeSetEvent)       │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Service Polls      │
│  via IOCTL          │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Dequeue Events     │
│  (Batch Read)       │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Deserialize &      │
│  Enrich Data        │
│  • Resolve PIDs     │
│  • Add context      │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Serialize to JSON  │
│  (Schema validated) │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐      ┌──────────────┐
│  Write to JSONL     │─────>│  Rotate Log  │
│  File               │  Size │  Create New  │
│                     │ Limit │  File        │
└──────┬──────────────┘      └──────────────┘
       │
       v
┌─────────────────────┐
│  Event Persisted    │
│  (Disk Storage)     │
└─────────────────────┘
```

---

## 5. Thread Architecture

### 5.1 Kernel Driver Threads

| Thread | Type | Purpose | Priority |
|--------|------|---------|----------|
| DriverEntry | System | Initialization, callback registration | PASSIVE_LEVEL |
| I/O Callbacks | System | Handle IRP_MJ_* operations | DISPATCH_LEVEL |
| Process Callbacks | System | Process/thread/image notifications | PASSIVE_LEVEL |
| WFP Callouts | System | Network event classification | DISPATCH_LEVEL |
| IOCTL Handler | System | Handle user-mode messages | PASSIVE_LEVEL |

**Notes:**
- No dedicated driver threads (all callbacks are synchronous)
- Must complete quickly to avoid system hangs
- Use DPCs for deferred work if needed

### 5.2 User-Mode Service Threads

| Thread | Count | Purpose | Priority |
|--------|-------|---------|----------|
| Main Service | 1 | Service control, initialization | Normal |
| Event Processor | 2-4 | Read from driver, parse events | Above Normal |
| JSON Writer | 1 | Serialize and write to disk | Normal |
| File Rotator | 1 | Background log rotation | Below Normal |
| Health Monitor | 1 | Watchdog, metrics collection | Normal |
| Config Watcher | 1 | Monitor registry/file changes | Normal |

**Synchronization:**
- Lock-free queues between Event Processor and JSON Writer
- Thread pool for parallel event processing (optional)
- Async I/O for file writes (overlapped I/O)

---

## 6. Error Handling Flow

```
┌──────────────────┐
│  Operation       │
│  (Any Component) │
└────────┬─────────┘
         │
         v
    ┌────────┐
    │Success?│
    └───┬────┘
        │
   ┌────┴────┐
   │ Yes     │ No
   v         v
┌────────┐  ┌──────────────────┐
│Continue│  │  Error Severity? │
└────────┘  └────┬─────────────┘
                 │
         ┌───────┼────────┐
         │       │        │
         v       v        v
    ┌────────┐ ┌───────┐ ┌────────┐
    │Critical│ │Warning│ │ Info   │
    └───┬────┘ └───┬───┘ └───┬────┘
        │          │         │
        │          v         v
        │      ┌────────┐ ┌────────┐
        │      │  Log   │ │  Log   │
        │      │ Event  │ │ Debug  │
        │      └────────┘ └────────┘
        │
        v
    ┌──────────────────┐
    │  Critical Path:  │
    │                  │
    │  1. Log error    │
    │  2. Attempt      │
    │     recovery     │
    │  3. Notify admin │
    │  4. Graceful     │
    │     degradation  │
    └────────┬─────────┘
             │
             v
    ┌─────────────────┐
    │ Recovery Action:│
    ├─────────────────┤
    │ • Driver crash  │──> Structured exception, avoid bugcheck
    │ • Service crash │──> Auto-restart via SCM
    │ • Disk full     │──> Stop writing, purge old logs
    │ • Buffer full   │──> Drop events, increment counter
    │ • Config error  │──> Use defaults, log warning
    └─────────────────┘
```

---

## 7. Performance Optimization Points

### 7.1 Hot Path Optimizations

| Component | Optimization | Impact |
|-----------|--------------|--------|
| File Filter | Skip system volumes, whitelist paths | 60% reduction in events |
| Process Monitor | Exclude system processes (PID 0, 4, Registry) | 40% reduction |
| Network Monitor | Layer-specific callouts (avoid duplicate) | 30% reduction |
| Ring Buffer | Lock-free SPSC, power-of-2 size | 5x throughput |
| IOCTL | Batch event retrieval (100 events/call) | 10x reduction in syscalls |
| JSON Serialization | Pre-allocated buffers, string pooling | 2x faster |

### 7.2 Memory Optimization

```
Kernel Memory Budget:
┌─────────────────────────────────────┐
│ Component                  Size     │
├─────────────────────────────────────┤
│ Ring Buffer                2 MB     │
│ Driver Context             1 MB     │
│ WFP Callout Tables         512 KB   │
│ Filter Context Pool        1 MB     │
│ String Buffers             512 KB   │
├─────────────────────────────────────┤
│ Total Non-Paged Pool      ~5 MB     │
└─────────────────────────────────────┘

User-Mode Memory Budget:
┌─────────────────────────────────────┐
│ Component                  Size     │
├─────────────────────────────────────┤
│ Event Processing Queue     10 MB    │
│ JSON Serialization Buffers 5 MB     │
│ File Write Buffers         5 MB     │
│ Configuration Cache        1 MB     │
│ Thread Stacks (6x1MB)      6 MB     │
├─────────────────────────────────────┤
│ Total Working Set          ~27 MB   │
└─────────────────────────────────────┘
```

---

## 8. Component Interfaces (API Summary)

### 8.1 Kernel Driver Exports

```c
// Filter Manager Registration
NTSTATUS DriverEntry(PDRIVER_OBJECT, PUNICODE_STRING);
NTSTATUS FilterUnload(FLT_FILTER_UNLOAD_FLAGS);

// Operation Callbacks
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(...);
FLT_PREOP_CALLBACK_STATUS PreWriteOperation(...);
FLT_POSTOP_CALLBACK_STATUS PostCreateOperation(...);

// Process/Thread Callbacks
VOID ProcessNotifyCallback(PEPROCESS, HANDLE, PPS_CREATE_NOTIFY_INFO);
VOID ThreadNotifyCallback(HANDLE, HANDLE, BOOLEAN);
VOID ImageLoadNotifyCallback(PUNICODE_STRING, HANDLE, PIMAGE_INFO);

// Network Callbacks
VOID NTAPI NetworkCalloutClassify(const FWPS_INCOMING_VALUES0*, ...);

// Communication
NTSTATUS ConnectNotifyCallback(PFLT_PORT, PVOID, PVOID, ULONG, PVOID*);
NTSTATUS MessageNotifyCallback(PVOID, PVOID, ULONG, PVOID, ULONG, PULONG);
VOID DisconnectNotifyCallback(PVOID);

// Event Queue
NTSTATUS QueueEvent(PEVENT_RING_BUFFER, PVOID, ULONG);
NTSTATUS DequeueEvents(PEVENT_RING_BUFFER, PVOID, ULONG, PULONG);
```

### 8.2 User-Mode Service Interfaces

```cpp
class IDriverCommunicator {
public:
    virtual HRESULT Connect() = 0;
    virtual HRESULT Disconnect() = 0;
    virtual HRESULT GetEvents(PVOID Buffer, DWORD Size, PDWORD BytesReturned) = 0;
    virtual HRESULT SetConfiguration(PVOID Config, DWORD Size) = 0;
    virtual HRESULT GetStatistics(PerfStats* Stats) = 0;
};

class IEventProcessor {
public:
    virtual void ProcessEvent(const EDR_EVENT_HEADER* Event) = 0;
    virtual void SetCallback(EventCallback Callback) = 0;
};

class IJsonLogger {
public:
    virtual void LogEvent(const json& Event) = 0;
    virtual void Rotate() = 0;
    virtual void SetMaxFileSize(uint64_t Size) = 0;
};

class IConfigManager {
public:
    virtual bool LoadConfiguration(const std::wstring& Path) = 0;
    virtual bool SaveConfiguration(const std::wstring& Path) = 0;
    virtual ConfigValue GetValue(const std::string& Key) = 0;
    virtual void SetValue(const std::string& Key, const ConfigValue& Value) = 0;
};
```

---

## 9. Data Flow Summary

### 9.1 Latency Budget

| Stage | Target Latency | Max Latency |
|-------|---------------|-------------|
| Kernel callback execution | <10 μs | <100 μs |
| Ring buffer write | <1 μs | <10 μs |
| IOCTL roundtrip | <100 μs | <1 ms |
| Event deserialization | <50 μs | <500 μs |
| JSON serialization | <100 μs | <1 ms |
| File write (buffered) | <1 ms | <10 ms |
| **End-to-end (event → disk)** | **<2 ms** | **<20 ms** |

### 9.2 Throughput Requirements

| Metric | Normal Load | Peak Load | Stress Test |
|--------|-------------|-----------|-------------|
| Events/second | 1,000 | 5,000 | 10,000+ |
| File operations/second | 100 | 500 | 1,000 |
| Network connections/second | 50 | 200 | 500 |
| Process creations/second | 10 | 50 | 100 |
| JSON write throughput | 1 MB/s | 5 MB/s | 10 MB/s |

---

## Summary

This document provides comprehensive component breakdowns and flow diagrams for all major system interactions. The architecture is designed for:

1. **Low Latency**: Sub-millisecond event capture and queuing
2. **High Throughput**: 10,000+ events/second sustained
3. **Reliability**: Graceful degradation under overload
4. **Maintainability**: Clear component boundaries and interfaces

Use these diagrams for implementation reference, code reviews, and architectural discussions with stakeholders.
