# Windows EDR System - High-Level Architecture

## Executive Summary

This document outlines the high-level architecture for a production-grade Endpoint Detection and Response (EDR) system built from scratch for Windows platforms. The system leverages kernel-mode mini-filter drivers to capture process and network activity in real-time, with initial implementation focusing on JSON-based file system logging.

## System Overview

### Purpose
Build a robust, enterprise-grade EDR solution that:
- Monitors process creation, termination, and behavior at kernel level
- Captures network activity (connections, DNS queries, data transfers)
- Provides real-time telemetry collection with minimal performance impact
- Exports structured data (JSON) for analysis and alerting
- Scales to cloud-based backend (future phase)

### Design Principles
1. **Security-First**: Operate at Ring 0 with signed drivers, tamper-resistant design
2. **Performance**: Minimal CPU/memory overhead (<5% system resources)
3. **Reliability**: Fault-tolerant with graceful degradation
4. **Observability**: Comprehensive logging and debugging capabilities
5. **Maintainability**: Modular architecture, well-documented codebase
6. **Compliance**: Adheres to Windows Driver Framework (WDF) best practices

## Architecture Layers

### Layer 1: Kernel Components (Ring 0)

#### 1.1 Mini-Filter Driver (File System Monitor)
- **Purpose**: Intercept file system operations (create, read, write, delete, rename)
- **Framework**: Filter Manager (FltMgr.sys)
- **Altitude**: 320000-329999 range (anti-virus/security)
- **Key Operations**:
  - Pre/Post-operation callbacks for IRP_MJ_CREATE, IRP_MJ_WRITE, IRP_MJ_SET_INFORMATION
  - Context tracking for file objects
  - Intelligent filtering (exclude system files, focus on user directories)

#### 1.2 Process Monitor Component
- **Purpose**: Track process lifecycle and behavior
- **Implementation**:
  - PsSetCreateProcessNotifyRoutineEx for process creation/exit
  - PsSetCreateThreadNotifyRoutine for thread activity
  - PsSetLoadImageNotifyRoutine for DLL/driver loading
- **Data Captured**:
  - Process ID, Parent PID, command line, image path
  - User context (SID, token privileges)
  - Integrity level, session ID
  - Timestamp, exit code

#### 1.3 Network Monitor Component
- **Purpose**: Capture network connections and traffic metadata
- **Implementation Options**:
  - **Option A**: Windows Filtering Platform (WFP) Callout Driver
    - Layers: FWPM_LAYER_ALE_AUTH_CONNECT_V{4,6}
    - Captures: TCP/UDP connections, remote endpoints, process association
  - **Option B**: Network Driver Interface Specification (NDIS) Filter
    - Deeper packet inspection capabilities
    - Higher complexity, performance considerations
- **Data Captured**:
  - Source/destination IP:Port
  - Protocol (TCP/UDP/ICMP)
  - Process ID, direction (inbound/outbound)
  - Bytes transferred, connection state

### Layer 2: User-Mode Service (Ring 3)

#### 2.1 Data Collection Service
- **Architecture**: Windows Service (runs as LocalSystem/NT AUTHORITY\SYSTEM)
- **Responsibilities**:
  - Communicate with kernel driver via IOCTL interface
  - Receive telemetry events from ring buffer/shared memory
  - Format data into structured JSON
  - Buffer management and flow control
  - Health monitoring and driver communication

#### 2.2 Storage Manager
- **Phase 1 Implementation**: File System Logger
  - **Format**: JSON Lines (JSONL) - one event per line
  - **Rotation**: Time-based (hourly) and size-based (100MB)
  - **Path**: `C:\ProgramData\YourEDR\Logs\events_YYYYMMDD_HHMMSS.jsonl`
  - **Compression**: Optional gzip for rotated logs
  - **Retention**: Configurable (default: 7 days)

- **Phase 2 (Future)**: Cloud Pipeline
  - In-memory queue (circular buffer)
  - Batch upload with retry logic
  - TLS 1.3 encrypted transport
  - Compression (protobuf/msgpack)

#### 2.3 Configuration Manager
- **Storage**: Registry (HKLM\SOFTWARE\YourEDR) + encrypted config file
- **Settings**:
  - Event filtering rules (processes to monitor, paths to exclude)
  - Log rotation policies
  - Performance tuning (buffer sizes, sampling rates)
  - Feature flags (enable/disable components)

### Layer 3: Management & Control Plane

#### 3.1 Administration Interface
- **CLI Tool**: PowerShell module for configuration
- **Service Control**: Start/stop/restart components
- **Query Interface**: Retrieve driver statistics, event counts
- **Logging**: Diagnostic logs for troubleshooting

#### 3.2 Installation & Updates
- **Installer**: MSI package with driver signing validation
- **Driver Deployment**:
  - Copy to `%SystemRoot%\System32\drivers\`
  - Service creation (sc.exe)
  - Filter registration with FltMgr
- **Update Mechanism**:
  - Staged rollout support
  - Rollback capability
  - Signature verification

## Data Flow

```
[User-Mode Application]
         ↓
[System Call (NtCreateFile, NtCreateProcess, socket, etc.)]
         ↓
[NT Kernel (ntoskrnl.exe)]
         ↓
    ┌────┴────┬─────────────┬──────────────┐
    ↓         ↓             ↓              ↓
[FltMgr]  [Process CB]  [WFP/NDIS]  [Image CB]
    ↓         ↓             ↓              ↓
[Mini-Filter Driver] [Process Monitor] [Network Monitor]
    └────┬────┴─────────────┴──────────────┘
         ↓
[Shared Event Queue (Ring Buffer)]
         ↓
[IOCTL Communication Channel]
         ↓
[User-Mode EDR Service]
         ↓
    ┌────┴────┐
    ↓         ↓
[JSON File] [Future: Cloud API]
```

## System Components Interaction

### Event Capture Flow
1. **Kernel Event Occurs**: Process creation, file access, network connection
2. **Driver Callback Triggered**: Registered callback function executes
3. **Data Collection**: Extract relevant metadata from kernel structures
4. **Event Queuing**: Push to lock-free ring buffer (shared memory)
5. **User-Mode Notification**: Signal event to service (IOCTL or event object)
6. **Service Processing**: Dequeue events, enrich with additional context
7. **Serialization**: Convert to JSON with schema validation
8. **Storage**: Append to JSONL file with atomic write operations
9. **Rotation**: Trigger rotation based on size/time policy

### Communication Channels

#### Kernel ↔ User-Mode
- **Method**: DeviceIoControl (IOCTL)
- **Device**: `\\.\YourEDRDevice`
- **IOCTLs**:
  - `IOCTL_EDR_GET_EVENTS`: Retrieve queued events (buffered I/O)
  - `IOCTL_EDR_SET_CONFIG`: Update filter configuration
  - `IOCTL_EDR_GET_STATS`: Query performance counters
  - `IOCTL_EDR_REGISTER_PROCESS`: User-mode registration/heartbeat

#### Shared Memory Architecture
- **Ring Buffer**: Lock-free SPSC (Single Producer, Single Consumer) per component
- **Size**: 2MB default (configurable via registry)
- **Overflow Handling**: Drop oldest events, increment counter
- **Synchronization**: Keyed events (KeSetEvent) for notification

## Security Architecture

### Driver Signing & Trust
- **Requirement**: EV Code Signing Certificate + Microsoft Hardware Dev Center attestation
- **Boot-Start Drivers**: WHQL certification required for clean boot
- **Signature Validation**: Service validates driver signature on installation

### Anti-Tampering Measures
- **Protected Process Light (PPL)**: User-mode service runs as PPL (future)
- **Driver Callbacks**: Early registration (DriverEntry) to prevent bypass
- **Configuration Integrity**: Signed configuration files, registry ACLs
- **Self-Defense**: Monitor attempts to unload driver, terminate service

### Privilege Model
- **Driver**: Runs in kernel mode (Ring 0), highest privilege
- **Service**: LocalSystem account with SeDebugPrivilege, SeLoadDriverPrivilege
- **Admin Interface**: Requires elevation (UAC), validates caller

## Performance Considerations

### Resource Budgets
- **CPU**: <2% average, <5% peak (per-core)
- **Memory**:
  - Kernel: <50MB non-paged pool
  - User-mode: <200MB working set
- **Disk I/O**: <10 MB/s write throughput
- **Network**: N/A (Phase 1), <1 Mbps (Phase 2)

### Optimization Strategies
1. **Event Filtering**:
   - Exclude system processes (PID 0, 4, Registry, smss.exe)
   - Path exclusions (Windows\System32\, Program Files\)
   - Extension whitelist (focus on executables, scripts)

2. **Batching**: Aggregate events before IOCTL transfer (50ms window)

3. **Asynchronous Processing**:
   - Non-blocking driver callbacks (post-operation preferred)
   - Dedicated worker threads in service

4. **Memory Management**:
   - Pool tagging for leak detection
   - Pre-allocated buffers (avoid runtime allocation)

5. **Sampling**: Rate limiting for high-frequency events (configurable)

## Scalability & Reliability

### High-Volume Event Handling
- **Scenario**: 10,000+ events/second (enterprise workstation)
- **Strategy**:
  - Priority queues (critical events vs. verbose)
  - Adaptive sampling during load spikes
  - Back-pressure signaling (kernel → user-mode)

### Fault Tolerance
- **Driver Crash**:
  - Structured Exception Handling (SEH) in all callbacks
  - Bug check avoided (graceful degradation)
  - Automatic service restart on communication loss

- **Service Crash**:
  - Windows Service Recovery (automatic restart)
  - Kernel driver continues queuing (buffer overflow protection)
  - Crash dump generation for RCA

- **Disk Full**:
  - Stop writing, log error event
  - Purge oldest logs (if retention policy allows)
  - Alert mechanism (Event Log, WMI)

## Deployment Architecture

### Target Environments
- **OS Support**: Windows 10/11 (x64), Server 2016/2019/2022
- **Kernel Versions**: Compatible with KMDF 1.25+, WDF 1.31+
- **Deployment Modes**:
  - Standalone (workstations)
  - Managed (Group Policy, SCCM, Intune)

### Installation Package Contents
```
YourEDR_Installer_v1.0.msi
│
├── Drivers/
│   ├── YourEDRFilter.sys        (Mini-filter driver)
│   ├── YourEDRFilter.inf        (Installation metadata)
│   └── YourEDRFilter.cat        (Catalog signature)
│
├── Services/
│   ├── YourEDRService.exe       (User-mode service)
│   └── YourEDRService.exe.config
│
├── Management/
│   ├── YourEDR.psd1             (PowerShell module)
│   ├── YourEDR.psm1
│   └── YourEDR-CLI.exe
│
└── Configuration/
    ├── default_config.json
    └── filter_rules.json
```

## Monitoring & Observability

### Telemetry (Internal)
- **Driver Metrics**:
  - Events captured/dropped per component
  - Callback execution time (average, P95, P99)
  - Memory pool usage

- **Service Metrics**:
  - Event processing rate
  - Queue depth, latency
  - File I/O errors
  - Crash/restart count

### Logging
- **Application Logs**: Windows Event Log (custom source)
- **Debug Logs**: ETW (Event Tracing for Windows) provider
- **Crash Dumps**: Mini-dumps (user-mode), kernel memory dumps (driver)

### Health Checks
- **Liveness**: Heartbeat between service and driver (10s interval)
- **Correctness**: Validate JSON schema, event sequence
- **Performance**: Alert on high CPU, memory, or queue depth

## Compliance & Certification

### Windows Hardware Quality Labs (WHQL)
- **Required for**: Boot-start filter drivers (production)
- **Process**: Submit driver package to Hardware Dev Center
- **Testing**: HLK test suite for filter drivers
- **Timeline**: 2-4 weeks for approval

### Security Standards
- **ISO 27001**: Secure development lifecycle
- **Common Criteria**: EAL2+ certification (optional, for government)
- **CIS Benchmarks**: Follow hardening guidelines

## Technology Stack

### Kernel Development
- **Language**: C (C11 standard)
- **Framework**: Windows Driver Framework (WDF/KMDF)
- **Build System**: MSBuild, WDK build tools
- **Testing**: WDK Debugger (WinDbg), Driver Verifier, HLK

### User-Mode Development
- **Language**: C++ (C++17) or C# (.NET 6+)
- **Frameworks**: Windows Services, WMI
- **Serialization**: RapidJSON, nlohmann/json, or System.Text.Json
- **Logging**: spdlog, NLog, or Serilog

### Development Tools
- **IDE**: Visual Studio 2022 Enterprise
- **Version Control**: Git (GitHub/Azure DevOps)
- **CI/CD**: Azure Pipelines, GitHub Actions
- **Static Analysis**: SDL, PREfast, CodeQL

## Future Enhancements (Post-Phase 1)

### Cloud Integration
- **Transport**: HTTPS/2 with certificate pinning
- **Protocol**: gRPC or custom REST API
- **Format**: Protocol Buffers or MessagePack
- **Features**: Bi-directional control (cloud → agent commands)

### Advanced Detection
- **Behavioral Analysis**: Process tree analysis, anomaly detection
- **Threat Intelligence**: IOC matching (file hashes, domains, IPs)
- **Machine Learning**: On-device inference for classification

### Platform Expansion
- **ELAM**: Early Launch Anti-Malware driver integration
- **Kernel Callbacks**: Registry, object manager, image verification
- **ETW Consumer**: Integrate system ETW events (PowerShell, .NET)

## Success Criteria

### Phase 1 Objectives
- [ ] Mini-filter driver successfully captures file operations
- [ ] Process monitor tracks creation/exit for all processes
- [ ] Network monitor logs TCP/UDP connections
- [ ] JSON output validates against schema
- [ ] File rotation works correctly
- [ ] System performance impact <3% CPU
- [ ] Zero kernel crashes in 100-hour stress test
- [ ] Driver passes WHQL static analysis

### Quality Gates
- [ ] Code coverage >80% (user-mode), static analysis clean
- [ ] Driver Verifier enabled testing (no issues)
- [ ] Security review completed (internal + external)
- [ ] Documentation complete (architecture, API, operations)

## Conclusion

This architecture provides a solid foundation for a production-grade Windows EDR system. The phased approach (file-based logging → cloud integration) allows for iterative development and early validation. The modular design ensures components can be developed, tested, and deployed independently while maintaining system cohesion.

**Next Steps**: Review this architecture with stakeholders, proceed to detailed technical specifications, and begin driver framework setup.
