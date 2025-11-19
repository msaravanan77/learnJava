# Windows EDR System - System Components Deep Dive

## Document Purpose

This document provides detailed specifications for each system component in the Windows EDR architecture. It bridges the gap between high-level architecture (doc 01) and the implementation plan.

## Kernel-Mode Components

### Mini-Filter Driver (YourEDRFilter.sys)

**Purpose**: Intercept and monitor file system operations in real-time.

**Specifications**:
- **Altitude**: 325100 (FSFilter Activity Monitor range)
- **Load Order**: Boot-start (production) or Demand-start (development)
- **Memory Footprint**: <50MB non-paged pool
- **Performance**: <10μs per callback execution

**Capabilities**:
- Pre/Post operation callbacks for IRP_MJ_CREATE, WRITE, SET_INFORMATION
- File name normalization and path resolution
- Context association with file objects
- Metadata extraction (timestamps, access rights, file attributes)

### Process Monitor Component

**Purpose**: Track process lifecycle and behavior.

**Specifications**:
- **Callback Type**: PsSetCreateProcessNotifyRoutineEx
- **Priority**: Normal (0)
- **Context**: Process creation and termination events

**Capabilities**:
- Process ID and parent process ID capture
- Full image path and command line extraction
- User context (SID, token information)
- Process integrity level determination

### Network Monitor Component

**Purpose**: Monitor network connections and traffic metadata.

**Specifications**:
- **Framework**: Windows Filtering Platform (WFP)
- **Layers**: FWPM_LAYER_ALE_AUTH_CONNECT_V4/V6
- **Mode**: Passive monitoring (FWP_ACTION_PERMIT)

**Capabilities**:
- TCP/UDP connection detection
- Source/destination IP and port capture
- Process association (PID)
- Connection direction (inbound/outbound)

## User-Mode Components

### EDR Service (YourEDRService.exe)

**Purpose**: User-mode orchestration and data processing.

**Specifications**:
- **Type**: Windows Service (LocalSystem account)
- **Startup**: Automatic
- **Dependencies**: Filter Manager Service (FltMgr)
- **Memory**: <200MB working set

**Capabilities**:
- IOCTL-based driver communication
- Event deserialization and enrichment
- JSON serialization and file I/O
- Configuration management
- Health monitoring and crash recovery

### Storage Manager

**Purpose**: Persistent event storage with rotation and retention.

**Specifications**:
- **Format**: JSON Lines (JSONL)
- **Location**: C:\ProgramData\YourEDR\Logs\
- **Rotation**: 100MB per file or 1 hour
- **Retention**: 7 days (configurable)

**Capabilities**:
- Atomic file writes
- Size and time-based rotation
- Automatic cleanup of old logs
- Compression support (future)

### Configuration Manager

**Purpose**: Centralized configuration management.

**Specifications**:
- **Storage**: Registry (HKLM\SOFTWARE\YourEDR) + JSON file
- **Format**: JSON schema-validated
- **Hot Reload**: Supported via file watcher

**Capabilities**:
- Path exclusion rules
- Process whitelist
- Performance tuning parameters
- Feature flags (enable/disable monitors)

## Communication Layer

### IOCTL Interface

**Purpose**: Kernel-to-user-mode communication channel.

**Specifications**:
- **Type**: FilterConnectCommunicationPort
- **Port Name**: \\YourEDRPort
- **Security**: SYSTEM and Administrators only
- **Max Connections**: 1 (single service instance)

**Message Types**:
- MSG_GET_EVENTS (0x8001): Retrieve queued events
- MSG_SET_CONFIG (0x8002): Update filter configuration
- MSG_GET_STATS (0x8003): Query performance metrics
- MSG_HEARTBEAT (0x8004): Keep-alive signal

### Ring Buffer

**Purpose**: Lock-free, high-performance event queue.

**Specifications**:
- **Size**: 2MB (configurable)
- **Type**: Single Producer Single Consumer (SPSC)
- **Overflow Policy**: Drop oldest events
- **Latency**: <1μs per write

## Data Structures

All event structures share a common header:

```c
typedef struct _EDR_EVENT_HEADER {
    ULONG EventSize;
    ULONG EventType;
    LARGE_INTEGER Timestamp;
    ULONG ProcessId;
    ULONG ThreadId;
    ULONG SessionId;
} EDR_EVENT_HEADER;
```

Event types extend this header with specific fields.

## Component Interaction Matrix

| Component | Interacts With | Protocol | Frequency |
|-----------|----------------|----------|-----------|
| Mini-Filter | Ring Buffer | Direct memory | Per file I/O |
| Process Monitor | Ring Buffer | Direct memory | Per process event |
| Network Monitor | Ring Buffer | Direct memory | Per connection |
| Ring Buffer | EDR Service | IOCTL | 10-50 Hz |
| EDR Service | Storage Manager | Function call | Per batch |
| EDR Service | Config Manager | Function call | On-demand |

## Performance Budget

| Component | CPU | Memory | Disk I/O |
|-----------|-----|--------|----------|
| Mini-Filter | <1.5% | <30MB | N/A |
| Process Monitor | <0.3% | <5MB | N/A |
| Network Monitor | <0.2% | <15MB | N/A |
| EDR Service | <1% | <200MB | <10MB/s |
| **Total** | **<3%** | **<250MB** | **<10MB/s** |

## Error Handling Strategy

### Kernel Components
- All callbacks use __try/__except
- Invalid pointers checked before dereferencing
- Memory allocation failures handled gracefully
- No bugcheck/BSOD under any circumstance

### User-Mode Components
- Exceptions logged and service continues
- Automatic restart on crash (SCM recovery)
- Graceful degradation if driver unavailable
- Alerts on repeated failures

## Security Model

### Driver Protection
- Signed with EV certificate
- Driver Signature Enforcement (DSE) enabled
- Anti-tampering: monitor driver unload attempts
- Protected configuration (registry ACLs)

### Service Protection
- Runs as LocalSystem (highest privilege)
- Process protection (future: PPL)
- Secure communication (authenticated IOCTL)
- Configuration integrity checks

## Deployment Components

### Installer (MSI)
- Driver files to System32\drivers
- Service executable to Program Files
- Registry configuration
- Automatic service registration
- Filter altitude registration

### Uninstaller
- Service stop and removal
- Driver unload via fltmc
- File cleanup
- Registry key removal
- Log file retention (optional)

## Monitoring and Diagnostics

### Internal Telemetry
- Event capture rate (events/sec)
- Event drop count
- Callback execution time (avg, P95, P99)
- Memory usage (paged/non-paged)
- IOCTL success/failure rate

### External Observability
- Windows Event Log integration
- ETW (Event Tracing for Windows) provider
- Performance counters
- WMI instrumentation

## Scalability Considerations

### Vertical Scaling
- Multi-threaded service processing
- Batch event retrieval from kernel
- Asynchronous file I/O
- Configurable worker thread count

### Horizontal Scaling
- Single agent per machine (no clustering)
- Cloud aggregation (Phase 4)
- Distributed analytics backend

## Summary

This document provides component-level specifications for the Windows EDR system. Each component is designed with clear responsibilities, performance budgets, and interaction protocols. Implementation teams should reference this document when building individual components to ensure consistency with the overall architecture.

**Next Document**: [03 - Security Architecture](03-security-architecture.md)
