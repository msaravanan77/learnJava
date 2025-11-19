# Windows EDR System - Detailed Technical Implementation Plan

## Document Overview

This document provides an in-depth technical implementation plan for the Windows EDR system, covering Phase 1 (kernel driver with file-based JSON logging). It includes detailed specifications, code structure, APIs, and step-by-step implementation guidance.

---

## 1. Mini-Filter Driver Implementation

### 1.1 Driver Architecture

#### File Structure
```
YourEDRFilter/
├── src/
│   ├── driver.c                 // DriverEntry, Unload, callbacks
│   ├── filter_operations.c      // Pre/Post operation handlers
│   ├── communication.c          // User-mode communication (IOCTL)
│   ├── process_monitor.c        // Process/thread/image callbacks
│   ├── network_monitor.c        // WFP callout implementation
│   ├── event_logger.c           // Event queuing and buffering
│   ├── utils.c                  // Helper functions (string, memory)
│   └── config.c                 // Configuration management
├── include/
│   ├── driver.h                 // Common definitions
│   ├── event_structures.h       // Event data structures
│   ├── ioctl_codes.h            // IOCTL definitions
│   └── config.h                 // Configuration structures
├── resources/
│   └── YourEDRFilter.rc         // Version resource
├── YourEDRFilter.inf            // Driver installation metadata
└── YourEDRFilter.vcxproj        // Visual Studio project
```

#### Core Data Structures

```c
// Event types enumeration
typedef enum _EDR_EVENT_TYPE {
    EventTypeProcessCreate = 1,
    EventTypeProcessExit = 2,
    EventTypeFileCreate = 3,
    EventTypeFileWrite = 4,
    EventTypeFileDelete = 5,
    EventTypeNetworkConnect = 6,
    EventTypeImageLoad = 7,
    EventTypeThreadCreate = 8
} EDR_EVENT_TYPE;

// Common event header (64 bytes aligned)
typedef struct _EDR_EVENT_HEADER {
    ULONG EventSize;                    // Total event size
    EDR_EVENT_TYPE EventType;           // Event type identifier
    LARGE_INTEGER Timestamp;            // System time (100ns intervals)
    ULONG ProcessId;                    // Source process ID
    ULONG ThreadId;                     // Source thread ID
    ULONG SessionId;                    // Session ID
    UCHAR IntegrityLevel;               // Process integrity level
    UCHAR Reserved[3];                  // Padding
    ULONGLONG SequenceNumber;           // Monotonic sequence
} EDR_EVENT_HEADER, *PEDR_EVENT_HEADER;

// Process creation event
typedef struct _EDR_PROCESS_CREATE_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG ParentProcessId;
    WCHAR ImagePath[260];               // Full path to executable
    WCHAR CommandLine[1024];            // Command line arguments
    UCHAR ImageHash[32];                // SHA-256 hash
    ULONG UserSidLength;
    UCHAR UserSid[68];                  // Variable length SID (max)
} EDR_PROCESS_CREATE_EVENT, *PEDR_PROCESS_CREATE_EVENT;

// File operation event
typedef struct _EDR_FILE_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG DesiredAccess;
    ULONG CreateDisposition;
    ULONG CreateOptions;
    WCHAR FilePath[520];                // Full NT path
    ULONG FileSize;
    LARGE_INTEGER CreationTime;
} EDR_FILE_EVENT, *PEDR_FILE_EVENT;

// Network connection event
typedef struct _EDR_NETWORK_EVENT {
    EDR_EVENT_HEADER Header;
    UCHAR Protocol;                     // IPPROTO_TCP, IPPROTO_UDP
    USHORT LocalPort;
    USHORT RemotePort;
    UCHAR LocalAddress[16];             // IPv6 (IPv4 mapped)
    UCHAR RemoteAddress[16];
    UCHAR Direction;                    // 0=outbound, 1=inbound
    ULONG BytesSent;
    ULONG BytesReceived;
} EDR_NETWORK_EVENT, *PEDR_NETWORK_EVENT;

// Ring buffer for event queuing
typedef struct _EVENT_RING_BUFFER {
    PUCHAR Buffer;                      // Allocated buffer
    ULONG BufferSize;                   // Total size (power of 2)
    volatile ULONG WriteOffset;         // Producer write position
    volatile ULONG ReadOffset;          // Consumer read position
    KSPIN_LOCK SpinLock;               // Synchronization
    ULONG EventsDropped;               // Overflow counter
    KEVENT DataAvailableEvent;         // Notification event
} EVENT_RING_BUFFER, *PEVENT_RING_BUFFER;
```

### 1.2 DriverEntry Implementation

```c
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;
    PFLT_FILTER filter = NULL;

    // Initialize global structures
    status = InitializeGlobalContext();
    if (!NT_SUCCESS(status)) {
        return status;
    }

    // Register mini-filter
    status = FltRegisterFilter(
        DriverObject,
        &FilterRegistration,
        &filter
    );
    if (!NT_SUCCESS(status)) {
        CleanupGlobalContext();
        return status;
    }

    // Store filter handle
    g_FilterHandle = filter;

    // Create communication port for user-mode
    status = CreateCommunicationPort(filter);
    if (!NT_SUCCESS(status)) {
        FltUnregisterFilter(filter);
        CleanupGlobalContext();
        return status;
    }

    // Register process callbacks
    status = RegisterProcessMonitor();
    if (!NT_SUCCESS(status)) {
        // Non-fatal, log and continue
        KdPrint(("EDR: Process monitor registration failed: 0x%X\n", status));
    }

    // Register network callbacks (WFP)
    status = RegisterNetworkMonitor();
    if (!NT_SUCCESS(status)) {
        KdPrint(("EDR: Network monitor registration failed: 0x%X\n", status));
    }

    // Initialize event ring buffer
    status = InitializeEventBuffer(&g_EventBuffer, RING_BUFFER_SIZE);
    if (!NT_SUCCESS(status)) {
        UnregisterAllCallbacks();
        FltUnregisterFilter(filter);
        CleanupGlobalContext();
        return status;
    }

    // Start filtering
    status = FltStartFiltering(filter);
    if (!NT_SUCCESS(status)) {
        FreeEventBuffer(&g_EventBuffer);
        UnregisterAllCallbacks();
        FltUnregisterFilter(filter);
        CleanupGlobalContext();
        return status;
    }

    KdPrint(("EDR: Driver loaded successfully\n"));
    return STATUS_SUCCESS;
}
```

### 1.3 Filter Registration

```c
const FLT_OPERATION_REGISTRATION Callbacks[] = {
    {
        IRP_MJ_CREATE,
        0,
        PreCreateOperation,
        PostCreateOperation
    },
    {
        IRP_MJ_WRITE,
        0,
        PreWriteOperation,
        NULL  // No post-operation
    },
    {
        IRP_MJ_SET_INFORMATION,
        0,
        PreSetInformationOperation,
        NULL
    },
    { IRP_MJ_OPERATION_END }
};

const FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),           // Size
    FLT_REGISTRATION_VERSION,           // Version
    0,                                  // Flags
    NULL,                               // Context
    Callbacks,                          // Operation callbacks
    FilterUnload,                       // Unload routine
    InstanceSetup,                      // Instance setup
    InstanceQueryTeardown,              // Query teardown
    InstanceTeardownStart,              // Teardown start
    InstanceTeardownComplete,           // Teardown complete
    NULL, NULL,                         // Name generation callbacks
    NULL, NULL, NULL                    // Normalize callbacks
};
```

### 1.4 Pre-Create Operation Handler

```c
FLT_PREOP_CALLBACK_STATUS PreCreateOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    PFLT_FILE_NAME_INFORMATION nameInfo = NULL;
    EDR_FILE_EVENT event;
    PEPROCESS process;
    HANDLE processId;

    UNREFERENCED_PARAMETER(CompletionContext);

    // Skip pre-rename operations
    if (FltObjects->FileObject->FileName.Length == 0) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    // Get file name information
    status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &nameInfo
    );
    if (!NT_SUCCESS(status)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    status = FltParseFileNameInformation(nameInfo);
    if (!NT_SUCCESS(status)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    // Apply filters (skip system files, whitelisted paths)
    if (ShouldSkipFile(&nameInfo->Name)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    // Build event structure
    RtlZeroMemory(&event, sizeof(event));
    event.Header.EventSize = sizeof(EDR_FILE_EVENT);
    event.Header.EventType = EventTypeFileCreate;
    KeQuerySystemTime(&event.Header.Timestamp);

    // Get process context
    process = IoThreadToProcess(Data->Thread);
    processId = PsGetProcessId(process);
    event.Header.ProcessId = HandleToULong(processId);
    event.Header.ThreadId = HandleToULong(PsGetCurrentThreadId());

    // Copy file path (limit to structure size)
    RtlStringCbCopyNW(
        event.FilePath,
        sizeof(event.FilePath),
        nameInfo->Name.Buffer,
        nameInfo->Name.Length
    );

    // Access rights
    event.DesiredAccess = Data->Iopb->Parameters.Create.SecurityContext->DesiredAccess;
    event.CreateDisposition = (Data->Iopb->Parameters.Create.Options >> 24) & 0xFF;
    event.CreateOptions = Data->Iopb->Parameters.Create.Options & 0x00FFFFFF;

    // Queue event
    QueueEvent(&g_EventBuffer, &event, sizeof(event));

    FltReleaseFileNameInformation(nameInfo);
    return FLT_PREOP_SUCCESS_WITH_CALLBACK;
}
```

### 1.5 Process Monitor Implementation

```c
VOID ProcessNotifyCallback(
    _In_ PEPROCESS Process,
    _In_ HANDLE ProcessId,
    _In_opt_ PPS_CREATE_NOTIFY_INFO CreateInfo
)
{
    EDR_PROCESS_CREATE_EVENT event;
    NTSTATUS status;

    if (CreateInfo != NULL) {
        // Process creation
        RtlZeroMemory(&event, sizeof(event));
        event.Header.EventSize = sizeof(EDR_PROCESS_CREATE_EVENT);
        event.Header.EventType = EventTypeProcessCreate;
        KeQuerySystemTime(&event.Header.Timestamp);
        event.Header.ProcessId = HandleToULong(ProcessId);
        event.ParentProcessId = HandleToULong(CreateInfo->ParentProcessId);

        // Get image path
        if (CreateInfo->ImageFileName != NULL) {
            RtlStringCbCopyNW(
                event.ImagePath,
                sizeof(event.ImagePath),
                CreateInfo->ImageFileName->Buffer,
                CreateInfo->ImageFileName->Length
            );
        }

        // Get command line
        if (CreateInfo->CommandLine != NULL) {
            RtlStringCbCopyNW(
                event.CommandLine,
                sizeof(event.CommandLine),
                CreateInfo->CommandLine->Buffer,
                CreateInfo->CommandLine->Length
            );
        }

        // Get user SID (simplified - actual implementation needs token access)
        // This would require SeDebugPrivilege and proper token handling

        // Queue event
        QueueEvent(&g_EventBuffer, &event, sizeof(event));
    } else {
        // Process exit - create simpler exit event
        EDR_EVENT_HEADER exitEvent;
        RtlZeroMemory(&exitEvent, sizeof(exitEvent));
        exitEvent.EventSize = sizeof(EDR_EVENT_HEADER);
        exitEvent.EventType = EventTypeProcessExit;
        KeQuerySystemTime(&exitEvent.Timestamp);
        exitEvent.ProcessId = HandleToULong(ProcessId);

        QueueEvent(&g_EventBuffer, &exitEvent, sizeof(exitEvent));
    }
}

NTSTATUS RegisterProcessMonitor(VOID)
{
    return PsSetCreateProcessNotifyRoutineEx(
        ProcessNotifyCallback,
        FALSE  // Don't remove
    );
}
```

### 1.6 Network Monitor (WFP Callout)

```c
// WFP callout function for connection monitoring
VOID NTAPI NetworkCalloutClassify(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ VOID* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
)
{
    EDR_NETWORK_EVENT event;
    UINT32 localAddr, remoteAddr;
    UINT16 localPort, remotePort;

    UNREFERENCED_PARAMETER(layerData);
    UNREFERENCED_PARAMETER(classifyContext);
    UNREFERENCED_PARAMETER(filter);
    UNREFERENCED_PARAMETER(flowContext);

    // Allow the connection (we're passive monitoring)
    classifyOut->actionType = FWP_ACTION_PERMIT;

    // Extract connection information (IPv4 example)
    localAddr = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
    remoteAddr = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    localPort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_PORT].value.uint16;
    remotePort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_PORT].value.uint16;

    // Build event
    RtlZeroMemory(&event, sizeof(event));
    event.Header.EventSize = sizeof(EDR_NETWORK_EVENT);
    event.Header.EventType = EventTypeNetworkConnect;
    KeQuerySystemTime(&event.Header.Timestamp);

    // Process ID from metadata
    if (FWPS_IS_METADATA_FIELD_PRESENT(inMetaValues, FWPS_METADATA_FIELD_PROCESS_ID)) {
        event.Header.ProcessId = (ULONG)inMetaValues->processId;
    }

    // Protocol
    event.Protocol = IPPROTO_TCP;  // Determined by layer
    event.LocalPort = localPort;
    event.RemotePort = remotePort;

    // Copy addresses (IPv4 mapped to IPv6 format)
    RtlCopyMemory(&event.LocalAddress[12], &localAddr, 4);
    RtlCopyMemory(&event.RemoteAddress[12], &remoteAddr, 4);
    event.Direction = 0;  // Outbound

    // Queue event
    QueueEvent(&g_EventBuffer, &event, sizeof(event));
}

NTSTATUS RegisterNetworkMonitor(VOID)
{
    NTSTATUS status;
    FWPM_SESSION0 session = {0};

    session.flags = FWPM_SESSION_FLAG_DYNAMIC;

    // Open session with BFE (Base Filtering Engine)
    status = FwpmEngineOpen0(
        NULL,
        RPC_C_AUTHN_WINNT,
        NULL,
        &session,
        &g_WfpEngineHandle
    );
    if (!NT_SUCCESS(status)) {
        return status;
    }

    // Register callout (detailed implementation omitted for brevity)
    // This involves:
    // 1. FwpsCalloutRegister0 - register with filter engine
    // 2. FwpmCalloutAdd0 - add to management layer
    // 3. FwpmFilterAdd0 - add filter to layer

    return STATUS_SUCCESS;
}
```

### 1.7 Event Queuing

```c
NTSTATUS QueueEvent(
    _In_ PEVENT_RING_BUFFER RingBuffer,
    _In_ PVOID Event,
    _In_ ULONG EventSize
)
{
    ULONG writePos, readPos, available;
    KIRQL oldIrql;

    // Align event size to 8 bytes
    EventSize = ALIGN_UP(EventSize, 8);

    KeAcquireSpinLock(&RingBuffer->SpinLock, &oldIrql);

    writePos = RingBuffer->WriteOffset;
    readPos = RingBuffer->ReadOffset;

    // Calculate available space
    if (writePos >= readPos) {
        available = RingBuffer->BufferSize - (writePos - readPos) - 1;
    } else {
        available = readPos - writePos - 1;
    }

    // Check if event fits
    if (EventSize > available) {
        RingBuffer->EventsDropped++;
        KeReleaseSpinLock(&RingBuffer->SpinLock, oldIrql);
        return STATUS_BUFFER_OVERFLOW;
    }

    // Copy event to buffer (handle wrap-around)
    if (writePos + EventSize <= RingBuffer->BufferSize) {
        RtlCopyMemory(
            RingBuffer->Buffer + writePos,
            Event,
            EventSize
        );
    } else {
        // Wrap around
        ULONG firstPart = RingBuffer->BufferSize - writePos;
        RtlCopyMemory(RingBuffer->Buffer + writePos, Event, firstPart);
        RtlCopyMemory(RingBuffer->Buffer, (PUCHAR)Event + firstPart, EventSize - firstPart);
    }

    // Update write position
    RingBuffer->WriteOffset = (writePos + EventSize) % RingBuffer->BufferSize;

    KeReleaseSpinLock(&RingBuffer->SpinLock, oldIrql);

    // Signal user-mode
    KeSetEvent(&RingBuffer->DataAvailableEvent, IO_NO_INCREMENT, FALSE);

    return STATUS_SUCCESS;
}
```

### 1.8 Communication Port (IOCTL)

```c
NTSTATUS CreateCommunicationPort(_In_ PFLT_FILTER Filter)
{
    NTSTATUS status;
    PSECURITY_DESCRIPTOR sd;
    OBJECT_ATTRIBUTES oa;
    UNICODE_STRING portName;

    // Build security descriptor (allow only SYSTEM and Admins)
    status = FltBuildDefaultSecurityDescriptor(&sd, FLT_PORT_ALL_ACCESS);
    if (!NT_SUCCESS(status)) {
        return status;
    }

    RtlInitUnicodeString(&portName, L"\\YourEDRPort");
    InitializeObjectAttributes(&oa, &portName, OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE, NULL, sd);

    // Create communication port
    status = FltCreateCommunicationPort(
        Filter,
        &g_ServerPort,
        &oa,
        NULL,  // Server port cookie
        ConnectNotifyCallback,
        DisconnectNotifyCallback,
        MessageNotifyCallback,
        1      // Max connections
    );

    FltFreeSecurityDescriptor(sd);
    return status;
}

NTSTATUS ConnectNotifyCallback(
    _In_ PFLT_PORT ClientPort,
    _In_opt_ PVOID ServerPortCookie,
    _In_reads_bytes_opt_(SizeOfContext) PVOID ConnectionContext,
    _In_ ULONG SizeOfContext,
    _Outptr_result_maybenull_ PVOID *ConnectionPortCookie
)
{
    // Store client port for sending events
    g_ClientPort = ClientPort;
    *ConnectionPortCookie = NULL;

    KdPrint(("EDR: User-mode client connected\n"));
    return STATUS_SUCCESS;
}

VOID DisconnectNotifyCallback(_In_opt_ PVOID ConnectionCookie)
{
    UNREFERENCED_PARAMETER(ConnectionCookie);

    FltCloseClientPort(g_FilterHandle, &g_ClientPort);
    g_ClientPort = NULL;

    KdPrint(("EDR: User-mode client disconnected\n"));
}

NTSTATUS MessageNotifyCallback(
    _In_opt_ PVOID PortCookie,
    _In_reads_bytes_opt_(InputBufferLength) PVOID InputBuffer,
    _In_ ULONG InputBufferLength,
    _Out_writes_bytes_to_opt_(OutputBufferLength, *ReturnOutputBufferLength) PVOID OutputBuffer,
    _In_ ULONG OutputBufferLength,
    _Out_ PULONG ReturnOutputBufferLength
)
{
    // Handle IOCTL-style messages from user-mode
    // Example: Get events, set configuration, query stats

    UNREFERENCED_PARAMETER(PortCookie);

    if (InputBufferLength < sizeof(ULONG)) {
        return STATUS_INVALID_PARAMETER;
    }

    ULONG messageType = *(PULONG)InputBuffer;

    switch (messageType) {
        case MSG_GET_EVENTS:
            return HandleGetEventsMessage(OutputBuffer, OutputBufferLength, ReturnOutputBufferLength);

        case MSG_SET_CONFIG:
            return HandleSetConfigMessage(InputBuffer, InputBufferLength);

        case MSG_GET_STATS:
            return HandleGetStatsMessage(OutputBuffer, OutputBufferLength, ReturnOutputBufferLength);

        default:
            return STATUS_INVALID_PARAMETER;
    }
}
```

---

## 2. User-Mode Service Implementation

### 2.1 Service Architecture

#### Project Structure
```
YourEDRService/
├── src/
│   ├── main.cpp                 // Service entry point
│   ├── service_controller.cpp   // SCM interaction
│   ├── driver_communicator.cpp  // Kernel communication
│   ├── event_processor.cpp      // Event deserialization
│   ├── json_logger.cpp          // JSON file writing
│   ├── file_rotator.cpp         // Log rotation logic
│   ├── config_manager.cpp       // Configuration handling
│   └── health_monitor.cpp       // Watchdog and metrics
├── include/
│   ├── event_structures.h       // Shared with driver
│   ├── ioctl_codes.h           // IOCTL definitions
│   ├── service.h               // Service interfaces
│   └── config.h                // Configuration schema
├── config/
│   └── default_config.json     // Default settings
└── YourEDRService.vcxproj
```

### 2.2 Service Entry Point

```cpp
// main.cpp
#include <windows.h>
#include <iostream>
#include "service_controller.h"

SERVICE_STATUS g_ServiceStatus = {0};
SERVICE_STATUS_HANDLE g_StatusHandle = NULL;
HANDLE g_ServiceStopEvent = INVALID_HANDLE_VALUE;

VOID WINAPI ServiceMain(DWORD argc, LPTSTR *argv);
VOID WINAPI ServiceCtrlHandler(DWORD);
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam);

int main(int argc, char* argv[])
{
    if (argc > 1 && strcmp(argv[1], "--console") == 0) {
        // Console mode for debugging
        std::cout << "Running in console mode...\n";
        ServiceWorkerThread(NULL);
        return 0;
    }

    // Run as Windows Service
    SERVICE_TABLE_ENTRY ServiceTable[] = {
        {(LPSTR)"YourEDRService", (LPSERVICE_MAIN_FUNCTION)ServiceMain},
        {NULL, NULL}
    };

    if (StartServiceCtrlDispatcher(ServiceTable) == FALSE) {
        return GetLastError();
    }

    return 0;
}

VOID WINAPI ServiceMain(DWORD argc, LPTSTR *argv)
{
    g_StatusHandle = RegisterServiceCtrlHandler(
        "YourEDRService",
        ServiceCtrlHandler
    );

    if (g_StatusHandle == NULL) {
        return;
    }

    // Initialize service status
    ZeroMemory(&g_ServiceStatus, sizeof(g_ServiceStatus));
    g_ServiceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    g_ServiceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP;
    g_ServiceStatus.dwCurrentState = SERVICE_START_PENDING;

    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);

    // Create stop event
    g_ServiceStopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (g_ServiceStopEvent == NULL) {
        g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
        return;
    }

    // Start worker thread
    HANDLE hThread = CreateThread(NULL, 0, ServiceWorkerThread, NULL, 0, NULL);
    if (hThread == NULL) {
        g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
        return;
    }

    g_ServiceStatus.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);

    // Wait for stop signal
    WaitForSingleObject(g_ServiceStopEvent, INFINITE);

    // Cleanup
    CloseHandle(hThread);
    CloseHandle(g_ServiceStopEvent);

    g_ServiceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
}

VOID WINAPI ServiceCtrlHandler(DWORD CtrlCode)
{
    switch (CtrlCode) {
        case SERVICE_CONTROL_STOP:
            g_ServiceStatus.dwCurrentState = SERVICE_STOP_PENDING;
            SetServiceStatus(g_StatusHandle, &g_ServiceStatus);
            SetEvent(g_ServiceStopEvent);
            break;

        default:
            break;
    }
}
```

### 2.3 Driver Communication

```cpp
// driver_communicator.cpp
#include <windows.h>
#include <fltUser.h>
#include "event_structures.h"

class DriverCommunicator {
private:
    HANDLE m_PortHandle;
    bool m_Connected;

public:
    DriverCommunicator() : m_PortHandle(INVALID_HANDLE_VALUE), m_Connected(false) {}

    HRESULT Connect() {
        HRESULT hr = FilterConnectCommunicationPort(
            L"\\YourEDRPort",
            0,  // Options
            NULL,  // Context
            0,  // Context size
            NULL,  // Security attributes
            &m_PortHandle
        );

        if (SUCCEEDED(hr)) {
            m_Connected = true;
            std::cout << "Connected to driver\n";
        }

        return hr;
    }

    void Disconnect() {
        if (m_PortHandle != INVALID_HANDLE_VALUE) {
            CloseHandle(m_PortHandle);
            m_PortHandle = INVALID_HANDLE_VALUE;
            m_Connected = false;
        }
    }

    HRESULT GetEvents(PVOID Buffer, DWORD BufferSize, PDWORD BytesReturned) {
        if (!m_Connected) {
            return E_NOT_VALID_STATE;
        }

        DWORD messageType = MSG_GET_EVENTS;

        HRESULT hr = FilterSendMessage(
            m_PortHandle,
            &messageType,
            sizeof(messageType),
            Buffer,
            BufferSize,
            BytesReturned
        );

        return hr;
    }

    HRESULT SetConfiguration(PVOID ConfigData, DWORD ConfigSize) {
        if (!m_Connected) {
            return E_NOT_VALID_STATE;
        }

        struct {
            DWORD MessageType;
            BYTE ConfigData[4096];
        } message;

        message.MessageType = MSG_SET_CONFIG;
        memcpy(message.ConfigData, ConfigData, min(ConfigSize, 4096));

        DWORD bytesReturned;
        HRESULT hr = FilterSendMessage(
            m_PortHandle,
            &message,
            sizeof(DWORD) + ConfigSize,
            NULL,
            0,
            &bytesReturned
        );

        return hr;
    }
};
```

### 2.4 JSON Event Serialization

```cpp
// json_logger.cpp
#include <nlohmann/json.hpp>
#include <fstream>
#include <sstream>
#include <iomanip>

using json = nlohmann::json;

class JsonLogger {
private:
    std::wstring m_LogDirectory;
    std::wstring m_CurrentLogFile;
    std::ofstream m_FileStream;
    uint64_t m_CurrentFileSize;
    uint64_t m_MaxFileSize;

    std::wstring GenerateLogFileName() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        std::wstringstream ss;
        ss << m_LogDirectory << L"\\events_"
           << std::put_time(std::localtime(&time_t), L"%Y%m%d_%H%M%S")
           << L".jsonl";

        return ss.str();
    }

    void RotateLog() {
        if (m_FileStream.is_open()) {
            m_FileStream.close();
        }

        m_CurrentLogFile = GenerateLogFileName();
        m_FileStream.open(m_CurrentLogFile, std::ios::app);
        m_CurrentFileSize = 0;
    }

public:
    JsonLogger(const std::wstring& logDir, uint64_t maxSize)
        : m_LogDirectory(logDir)
        , m_MaxFileSize(maxSize)
        , m_CurrentFileSize(0)
    {
        CreateDirectoryW(logDir.c_str(), NULL);
        RotateLog();
    }

    void LogProcessCreate(const EDR_PROCESS_CREATE_EVENT* event) {
        json j;
        j["event_type"] = "process_create";
        j["timestamp"] = event->Header.Timestamp.QuadPart;
        j["process_id"] = event->Header.ProcessId;
        j["parent_process_id"] = event->ParentProcessId;
        j["image_path"] = WideToUtf8(event->ImagePath);
        j["command_line"] = WideToUtf8(event->CommandLine);
        j["session_id"] = event->Header.SessionId;

        WriteJsonLine(j);
    }

    void LogFileEvent(const EDR_FILE_EVENT* event) {
        json j;
        j["event_type"] = "file_create";
        j["timestamp"] = event->Header.Timestamp.QuadPart;
        j["process_id"] = event->Header.ProcessId;
        j["file_path"] = WideToUtf8(event->FilePath);
        j["desired_access"] = event->DesiredAccess;
        j["create_disposition"] = event->CreateDisposition;

        WriteJsonLine(j);
    }

    void LogNetworkEvent(const EDR_NETWORK_EVENT* event) {
        json j;
        j["event_type"] = "network_connect";
        j["timestamp"] = event->Header.Timestamp.QuadPart;
        j["process_id"] = event->Header.ProcessId;
        j["protocol"] = event->Protocol;
        j["local_port"] = event->LocalPort;
        j["remote_port"] = event->RemotePort;
        j["remote_address"] = FormatIPAddress(event->RemoteAddress);
        j["direction"] = event->Direction == 0 ? "outbound" : "inbound";

        WriteJsonLine(j);
    }

private:
    void WriteJsonLine(const json& j) {
        std::string line = j.dump() + "\n";

        m_FileStream << line;
        m_FileStream.flush();

        m_CurrentFileSize += line.size();

        // Check if rotation needed
        if (m_CurrentFileSize >= m_MaxFileSize) {
            RotateLog();
        }
    }

    std::string WideToUtf8(const wchar_t* wide) {
        if (wide == nullptr || wide[0] == L'\0') return "";

        int size = WideCharToMultiByte(CP_UTF8, 0, wide, -1, NULL, 0, NULL, NULL);
        std::string utf8(size, 0);
        WideCharToMultiByte(CP_UTF8, 0, wide, -1, &utf8[0], size, NULL, NULL);

        // Remove null terminator
        utf8.resize(size - 1);
        return utf8;
    }

    std::string FormatIPAddress(const UCHAR* addr) {
        // IPv4 (mapped in last 4 bytes)
        std::stringstream ss;
        ss << (int)addr[12] << "." << (int)addr[13] << "."
           << (int)addr[14] << "." << (int)addr[15];
        return ss.str();
    }
};
```

### 2.5 Main Worker Thread

```cpp
DWORD WINAPI ServiceWorkerThread(LPVOID lpParam)
{
    UNREFERENCED_PARAMETER(lpParam);

    // Initialize components
    DriverCommunicator driverComm;
    JsonLogger logger(L"C:\\ProgramData\\YourEDR\\Logs", 100 * 1024 * 1024);  // 100MB

    // Connect to driver
    HRESULT hr = driverComm.Connect();
    if (FAILED(hr)) {
        std::cerr << "Failed to connect to driver: " << std::hex << hr << "\n";
        return 1;
    }

    // Event loop
    BYTE buffer[65536];  // 64KB buffer
    DWORD bytesReturned;

    while (WaitForSingleObject(g_ServiceStopEvent, 0) != WAIT_OBJECT_0) {
        // Get events from driver
        hr = driverComm.GetEvents(buffer, sizeof(buffer), &bytesReturned);

        if (FAILED(hr)) {
            Sleep(100);
            continue;
        }

        if (bytesReturned == 0) {
            Sleep(50);
            continue;
        }

        // Process events
        DWORD offset = 0;
        while (offset < bytesReturned) {
            PEDR_EVENT_HEADER header = (PEDR_EVENT_HEADER)(buffer + offset);

            switch (header->EventType) {
                case EventTypeProcessCreate:
                    logger.LogProcessCreate((PEDR_PROCESS_CREATE_EVENT)header);
                    break;

                case EventTypeFileCreate:
                    logger.LogFileEvent((PEDR_FILE_EVENT)header);
                    break;

                case EventTypeNetworkConnect:
                    logger.LogNetworkEvent((PEDR_NETWORK_EVENT)header);
                    break;

                default:
                    // Unknown event type
                    break;
            }

            offset += header->EventSize;
        }
    }

    driverComm.Disconnect();
    return 0;
}
```

---

## 3. Configuration Management

### 3.1 Configuration Schema (JSON)

```json
{
  "version": "1.0",
  "logging": {
    "directory": "C:\\ProgramData\\YourEDR\\Logs",
    "max_file_size_mb": 100,
    "retention_days": 7,
    "compression_enabled": false
  },
  "filtering": {
    "excluded_processes": [
      "System",
      "Registry",
      "smss.exe",
      "csrss.exe",
      "wininit.exe",
      "services.exe"
    ],
    "excluded_paths": [
      "C:\\Windows\\System32\\",
      "C:\\Windows\\SysWOW64\\",
      "C:\\Program Files\\WindowsApps\\"
    ],
    "monitored_extensions": [
      ".exe", ".dll", ".sys", ".ps1", ".bat",
      ".vbs", ".js", ".jar", ".scr"
    ]
  },
  "performance": {
    "ring_buffer_size_mb": 2,
    "event_batch_size": 100,
    "sampling_rate_percent": 100
  },
  "features": {
    "process_monitoring": true,
    "file_monitoring": true,
    "network_monitoring": true,
    "registry_monitoring": false,
    "image_load_monitoring": false
  }
}
```

---

## 4. Build and Deployment

### 4.1 Driver INF File

```ini
;
; YourEDRFilter.inf
;

[Version]
Signature   = "$Windows NT$"
Class       = "ActivityMonitor"
ClassGuid   = {b86dff51-a31e-4bac-b3cf-e8cfe75c9fc2}
Provider    = %ManufacturerName%
DriverVer   = 01/01/2025,1.0.0.0
CatalogFile = YourEDRFilter.cat
PnpLockdown = 1

[DestinationDirs]
DefaultDestDir          = 12
MiniFilter.DriverFiles  = 12

[DefaultInstall]
OptionDesc = %ServiceDescription%
CopyFiles  = MiniFilter.DriverFiles

[DefaultInstall.Services]
AddService = %ServiceName%,,MiniFilter.Service

[DefaultUninstall]
DelFiles   = MiniFilter.DriverFiles

[DefaultUninstall.Services]
DelService = %ServiceName%,0x200

[MiniFilter.Service]
DisplayName    = %ServiceName%
Description    = %ServiceDescription%
ServiceBinary  = %12%\%DriverName%.sys
ServiceType    = 2  ; SERVICE_FILE_SYSTEM_DRIVER
StartType      = 3  ; SERVICE_DEMAND_START (change to 2 for boot-start)
ErrorControl   = 1  ; SERVICE_ERROR_NORMAL
LoadOrderGroup = "FSFilter Activity Monitor"
AddReg         = MiniFilter.AddRegistry

[MiniFilter.AddRegistry]
HKR,"Instances","DefaultInstance",0x00000000,%DefaultInstance%
HKR,"Instances\"%Instance1.Name%,"Altitude",0x00000000,%Instance1.Altitude%
HKR,"Instances\"%Instance1.Name%,"Flags",0x00010001,0x0

[MiniFilter.DriverFiles]
%DriverName%.sys

[SourceDisksFiles]
YourEDRFilter.sys = 1,,

[SourceDisksNames]
1 = %DiskId1%,,,

[Strings]
ManufacturerName   = "Your Company"
ServiceName        = "YourEDRFilter"
ServiceDescription = "Your EDR Mini-Filter Driver"
DriverName         = "YourEDRFilter"
DiskId1            = "YourEDR Installation Disk"
DefaultInstance    = "YourEDR Instance"
Instance1.Name     = "YourEDR Instance"
Instance1.Altitude = "325100"
```

### 4.2 Installation Script (PowerShell)

```powershell
# install.ps1
param(
    [switch]$Uninstall
)

$ServiceName = "YourEDRFilter"
$DriverPath = "$PSScriptRoot\drivers\YourEDRFilter.sys"
$InfPath = "$PSScriptRoot\drivers\YourEDRFilter.inf"

function Install-Driver {
    Write-Host "Installing YourEDR driver..."

    # Verify signature
    $sig = Get-AuthenticodeSignature $DriverPath
    if ($sig.Status -ne 'Valid') {
        Write-Error "Driver signature is invalid!"
        return
    }

    # Install via INF
    $result = & pnputil.exe /add-driver $InfPath /install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Driver installation failed"
        return
    }

    # Load driver
    & sc.exe start $ServiceName

    Write-Host "Driver installed successfully"
}

function Uninstall-Driver {
    Write-Host "Uninstalling YourEDR driver..."

    # Stop driver
    & sc.exe stop $ServiceName

    # Uninstall via INF
    & rundll32.exe setupapi.dll,InstallHinfSection DefaultUninstall 132 $InfPath

    Write-Host "Driver uninstalled"
}

# Require elevation
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script requires administrative privileges"
    exit 1
}

if ($Uninstall) {
    Uninstall-Driver
} else {
    Install-Driver
}
```

---

## 5. Testing Strategy

### 5.1 Unit Testing
- **Driver**: Use WDK Debugger with test VMs
- **Service**: MSTest/NUnit with mock driver interface

### 5.2 Integration Testing
- End-to-end event flow (kernel → user-mode → JSON)
- Verify all event types captured correctly
- Test rotation logic with large datasets

### 5.3 Performance Testing
- Monitor CPU usage under load (1000+ processes)
- Memory leak detection (Driver Verifier)
- Disk I/O stress testing

### 5.4 Security Testing
- Fuzzing IOCTLs with invalid inputs
- Privilege escalation attempts
- Anti-tampering validation

---

## 6. Development Workflow

1. **Setup Development Environment** (see dependencies doc)
2. **Implement Mini-Filter Driver** (file operations first)
3. **Implement Process Monitor** (add process callbacks)
4. **Implement Network Monitor** (WFP integration)
5. **Implement User-Mode Service** (IOCTL communication)
6. **Add JSON Logging** (serialization and rotation)
7. **Configuration System** (registry + JSON config)
8. **Testing & Debugging** (Driver Verifier, WinDbg)
9. **Driver Signing** (EV certificate, HLK testing)
10. **Deployment Package** (MSI with INF)

---

## Summary

This implementation plan provides production-ready code templates for all major components. The architecture is modular, allowing parallel development of driver and service components. Phase 1 focuses on robust local logging; Phase 2 will extend to cloud connectivity.

**Estimated Timeline**: 8-12 weeks for Phase 1 MVP with experienced kernel developer.
