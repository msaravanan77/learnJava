#ifndef EVENT_STRUCTURES_H
#define EVENT_STRUCTURES_H

/*
 * YourEDR - Event Structures
 * Shared between kernel driver and user-mode service
 *
 * IMPORTANT: Keep this file synchronized between driver and service projects
 */

#ifdef _KERNEL_MODE
#include <ntddk.h>
#include <fltKernel.h>
#else
#include <windows.h>
#endif

// Event type enumeration
typedef enum _EDR_EVENT_TYPE {
    EventTypeNone = 0,
    EventTypeProcessCreate = 1,
    EventTypeProcessExit = 2,
    EventTypeFileCreate = 3,
    EventTypeFileWrite = 4,
    EventTypeFileDelete = 5,
    EventTypeFileRename = 6,
    EventTypeNetworkConnect = 7,
    EventTypeImageLoad = 8,
    EventTypeThreadCreate = 9,
    EventTypeMax = 10
} EDR_EVENT_TYPE;

// Common event header (64 bytes, aligned)
typedef struct _EDR_EVENT_HEADER {
    ULONG EventSize;                    // Total size of event structure
    EDR_EVENT_TYPE EventType;           // Event type identifier
    LARGE_INTEGER Timestamp;            // System time (100ns intervals since 1601)
    ULONG ProcessId;                    // Source process ID
    ULONG ThreadId;                     // Source thread ID
    ULONG SessionId;                    // Session ID
    UCHAR IntegrityLevel;               // Process integrity level (0-4)
    UCHAR Reserved[3];                  // Padding for alignment
    ULONGLONG SequenceNumber;           // Monotonic sequence number
} EDR_EVENT_HEADER, *PEDR_EVENT_HEADER;

// Process creation event (Phase 2)
typedef struct _EDR_PROCESS_CREATE_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG ParentProcessId;
    WCHAR ImagePath[260];               // Full path to executable
    WCHAR CommandLine[1024];            // Command line arguments
    UCHAR ImageHash[32];                // SHA-256 hash (placeholder)
    ULONG UserSidLength;
    UCHAR UserSid[68];                  // Variable length SID (max 68 bytes)
} EDR_PROCESS_CREATE_EVENT, *PEDR_PROCESS_CREATE_EVENT;

// Process exit event (Phase 2)
typedef struct _EDR_PROCESS_EXIT_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG ExitCode;
    ULONG Reserved;
} EDR_PROCESS_EXIT_EVENT, *PEDR_PROCESS_EXIT_EVENT;

// File operation event (Phase 1)
typedef struct _EDR_FILE_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG DesiredAccess;                // FILE_READ_DATA, FILE_WRITE_DATA, etc.
    ULONG CreateDisposition;            // CREATE_NEW, OPEN_EXISTING, etc.
    ULONG CreateOptions;                // FILE_DELETE_ON_CLOSE, etc.
    WCHAR FilePath[520];                // Full NT path (up to 520 chars)
    ULONGLONG FileSize;                 // File size in bytes
    LARGE_INTEGER CreationTime;         // File creation time
    LARGE_INTEGER LastWriteTime;        // File last write time
} EDR_FILE_EVENT, *PEDR_FILE_EVENT;

// Network connection event (Phase 2)
typedef struct _EDR_NETWORK_EVENT {
    EDR_EVENT_HEADER Header;
    UCHAR Protocol;                     // IPPROTO_TCP (6), IPPROTO_UDP (17)
    UCHAR Direction;                    // 0=outbound, 1=inbound
    USHORT LocalPort;
    USHORT RemotePort;
    UCHAR LocalAddress[16];             // IPv6 format (IPv4 mapped)
    UCHAR RemoteAddress[16];            // IPv6 format (IPv4 mapped)
    ULONGLONG BytesSent;
    ULONGLONG BytesReceived;
} EDR_NETWORK_EVENT, *PEDR_NETWORK_EVENT;

// Image load event (Phase 2)
typedef struct _EDR_IMAGE_LOAD_EVENT {
    EDR_EVENT_HEADER Header;
    WCHAR ImagePath[260];
    ULONGLONG ImageBase;
    ULONG ImageSize;
    UCHAR ImageHash[32];                // SHA-256 hash (placeholder)
} EDR_IMAGE_LOAD_EVENT, *PEDR_IMAGE_LOAD_EVENT;

// Thread creation event (Phase 2)
typedef struct _EDR_THREAD_CREATE_EVENT {
    EDR_EVENT_HEADER Header;
    ULONG CreatingProcessId;
    ULONG CreatingThreadId;
    ULONGLONG StartAddress;
} EDR_THREAD_CREATE_EVENT, *PEDR_THREAD_CREATE_EVENT;

// Maximum event size (for buffer allocation)
#define EDR_MAX_EVENT_SIZE sizeof(EDR_PROCESS_CREATE_EVENT)

// Event validation macros
#define EDR_IS_VALID_EVENT_TYPE(type) ((type) > EventTypeNone && (type) < EventTypeMax)
#define EDR_IS_VALID_EVENT_SIZE(size) ((size) >= sizeof(EDR_EVENT_HEADER) && (size) <= EDR_MAX_EVENT_SIZE)

#endif // EVENT_STRUCTURES_H
