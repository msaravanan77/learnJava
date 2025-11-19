#ifndef YOUREDR_DRIVER_H
#define YOUREDR_DRIVER_H

#define _KERNEL_MODE
#include <ntddk.h>
#include <fltKernel.h>
#include <ntstrsafe.h>

#include "../../../common/include/event_structures.h"
#include "../../../common/include/ioctl_codes.h"

// Driver version
#define YOUREDR_MAJOR_VERSION   1
#define YOUREDR_MINOR_VERSION   0
#define YOUREDR_PATCH_VERSION   0
#define YOUREDR_BUILD_NUMBER    1

// Ring buffer configuration
#define RING_BUFFER_SIZE        (2 * 1024 * 1024)  // 2 MB
#define MAX_QUEUED_EVENTS       1000

// Filter altitude (FSFilter Activity Monitor range)
#define YOUREDR_ALTITUDE        L"325100"

// Pool tags
#define YOUREDR_POOL_TAG        'rdeY'  // 'Yedr' in little-endian
#define YOUREDR_EVENT_TAG       'evEY'  // 'YEev'
#define YOUREDR_BUFFER_TAG      'fbEY'  // 'YEbf'

//
// Global data structures
//

typedef struct _RING_BUFFER_ENTRY {
    ULONG Size;                         // Size of this entry (including header)
    UCHAR EventData[1];                 // Variable-length event data
} RING_BUFFER_ENTRY, *PRING_BUFFER_ENTRY;

typedef struct _YOUREDR_RING_BUFFER {
    PUCHAR Buffer;                      // Ring buffer memory
    ULONG Size;                         // Total buffer size
    volatile ULONG WriteOffset;         // Producer write position
    volatile ULONG ReadOffset;          // Consumer read position
    KSPIN_LOCK Lock;                    // Spinlock for synchronization
    KEVENT DataAvailableEvent;          // Event signaled when data available
    ULONGLONG TotalEventsQueued;        // Statistics
    ULONGLONG TotalEventsDropped;
} YOUREDR_RING_BUFFER, *PYOUREDR_RING_BUFFER;

typedef struct _YOUREDR_GLOBAL_DATA {
    PFLT_FILTER FilterHandle;           // Filter handle
    PFLT_PORT ServerPort;               // Communication port
    PDEVICE_OBJECT DeviceObject;        // Control device object
    YOUREDR_RING_BUFFER RingBuffer;     // Event ring buffer
    YOUREDR_CONFIG Config;              // Current configuration
    YOUREDR_STATS Stats;                // Statistics
    ULONGLONG SequenceNumber;           // Event sequence number
    KSPIN_LOCK SequenceLock;            // Lock for sequence number
} YOUREDR_GLOBAL_DATA, *PYOUREDR_GLOBAL_DATA;

//
// Global variables (defined in driver.c)
//

extern YOUREDR_GLOBAL_DATA g_GlobalData;

//
// Function declarations from driver.c
//

DRIVER_INITIALIZE DriverEntry;
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
);

NTSTATUS YourEDRUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
);

NTSTATUS YourEDRInstanceSetup(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_SETUP_FLAGS Flags,
    _In_ DEVICE_TYPE VolumeDeviceType,
    _In_ FLT_FILESYSTEM_TYPE VolumeFilesystemType
);

NTSTATUS YourEDRInstanceQueryTeardown(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_QUERY_TEARDOWN_FLAGS Flags
);

//
// Function declarations from filter_operations.c
//

FLT_PREOP_CALLBACK_STATUS PreCreateOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

FLT_PREOP_CALLBACK_STATUS PreWriteOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

FLT_PREOP_CALLBACK_STATUS PreSetInformationOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

//
// Function declarations from communication.c
//

NTSTATUS CreateCommunicationDevice(
    _In_ PDRIVER_OBJECT DriverObject
);

VOID DeleteCommunicationDevice(VOID);

NTSTATUS DeviceIoControlHandler(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

//
// Function declarations from event_logger.c
//

NTSTATUS InitializeRingBuffer(
    _Out_ PYOUREDR_RING_BUFFER RingBuffer
);

VOID CleanupRingBuffer(
    _In_ PYOUREDR_RING_BUFFER RingBuffer
);

NTSTATUS QueueEvent(
    _In_ PYOUREDR_RING_BUFFER RingBuffer,
    _In_ PVOID EventData,
    _In_ ULONG EventSize
);

NTSTATUS DequeueEvent(
    _In_ PYOUREDR_RING_BUFFER RingBuffer,
    _Out_writes_bytes_(BufferSize) PVOID Buffer,
    _In_ ULONG BufferSize,
    _Out_ PULONG BytesReturned
);

ULONGLONG GetNextSequenceNumber(VOID);

VOID GetCurrentTimestamp(
    _Out_ PLARGE_INTEGER Timestamp
);

//
// Function declarations from network_monitor.c
//

NTSTATUS InitializeNetworkMonitoring(
    _In_ PDEVICE_OBJECT DeviceObject
);

VOID CleanupNetworkMonitoring(VOID);

//
// WFP Callout GUIDs (must be unique for each driver)
//

// {8B5E5F01-1234-4567-89AB-0123456789AB}
DEFINE_GUID(
    YOUREDR_CALLOUT_CONNECT_V4_GUID,
    0x8b5e5f01, 0x1234, 0x4567, 0x89, 0xab, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab
);

// {8B5E5F02-1234-4567-89AB-0123456789AB}
DEFINE_GUID(
    YOUREDR_CALLOUT_CONNECT_V6_GUID,
    0x8b5e5f02, 0x1234, 0x4567, 0x89, 0xab, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab
);

// {8B5E5F03-1234-4567-89AB-0123456789AB}
DEFINE_GUID(
    YOUREDR_CALLOUT_ACCEPT_V4_GUID,
    0x8b5e5f03, 0x1234, 0x4567, 0x89, 0xab, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab
);

// {8B5E5F04-1234-4567-89AB-0123456789AB}
DEFINE_GUID(
    YOUREDR_CALLOUT_ACCEPT_V6_GUID,
    0x8b5e5f04, 0x1234, 0x4567, 0x89, 0xab, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab
);

//
// Helper macros
//

#define YOUREDR_ASSERT(x) NT_ASSERT(x)

#define YOUREDR_LOG_ERROR(fmt, ...) \
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, \
        "[YourEDR] ERROR: " fmt "\n", ##__VA_ARGS__)

#define YOUREDR_LOG_WARNING(fmt, ...) \
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_WARNING_LEVEL, \
        "[YourEDR] WARNING: " fmt "\n", ##__VA_ARGS__)

#define YOUREDR_LOG_INFO(fmt, ...) \
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, \
        "[YourEDR] INFO: " fmt "\n", ##__VA_ARGS__)

#ifdef DBG
#define YOUREDR_LOG_DEBUG(fmt, ...) \
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_TRACE_LEVEL, \
        "[YourEDR] DEBUG: " fmt "\n", ##__VA_ARGS__)
#else
#define YOUREDR_LOG_DEBUG(fmt, ...)
#endif

#endif // YOUREDR_DRIVER_H
