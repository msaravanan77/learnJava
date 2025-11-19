#ifndef IOCTL_CODES_H
#define IOCTL_CODES_H

/*
 * YourEDR - IOCTL Communication Codes
 * Shared between kernel driver and user-mode service
 *
 * IMPORTANT: Keep this file synchronized between driver and service projects
 */

#ifdef _KERNEL_MODE
#include <ntddk.h>
#else
#include <windows.h>
#include <winioctl.h>
#endif

// Device name and symbolic link
#define YOUREDR_DEVICE_NAME         L"\\Device\\YourEDRFilter"
#define YOUREDR_SYMLINK_NAME        L"\\DosDevices\\YourEDRFilter"
#define YOUREDR_USER_DEVICE_NAME    L"\\\\.\\YourEDRFilter"

// Device type (custom driver)
#define FILE_DEVICE_YOUREDR         0x8000

// IOCTL function codes (0x800 - 0x8FF for custom drivers)
#define IOCTL_YOUREDR_GET_VERSION \
    CTL_CODE(FILE_DEVICE_YOUREDR, 0x800, METHOD_BUFFERED, FILE_READ_DATA)

#define IOCTL_YOUREDR_GET_EVENT \
    CTL_CODE(FILE_DEVICE_YOUREDR, 0x801, METHOD_BUFFERED, FILE_READ_DATA)

#define IOCTL_YOUREDR_SET_CONFIG \
    CTL_CODE(FILE_DEVICE_YOUREDR, 0x802, METHOD_BUFFERED, FILE_WRITE_DATA)

#define IOCTL_YOUREDR_GET_STATS \
    CTL_CODE(FILE_DEVICE_YOUREDR, 0x803, METHOD_BUFFERED, FILE_READ_DATA)

#define IOCTL_YOUREDR_CLEAR_EVENTS \
    CTL_CODE(FILE_DEVICE_YOUREDR, 0x804, METHOD_BUFFERED, FILE_WRITE_DATA)

// Version structure
typedef struct _YOUREDR_VERSION {
    ULONG MajorVersion;
    ULONG MinorVersion;
    ULONG PatchVersion;
    ULONG BuildNumber;
} YOUREDR_VERSION, *PYOUREDR_VERSION;

// Driver statistics
typedef struct _YOUREDR_STATS {
    ULONGLONG TotalEventsQueued;
    ULONGLONG TotalEventsDropped;
    ULONGLONG TotalEventsRead;
    ULONG CurrentQueuedEvents;
    ULONG RingBufferSize;
    ULONG RingBufferUsedBytes;
} YOUREDR_STATS, *PYOUREDR_STATS;

// Configuration structure (Phase 1 - basic filtering)
typedef struct _YOUREDR_CONFIG {
    BOOLEAN EnableFileMonitoring;
    BOOLEAN EnableProcessMonitoring;
    BOOLEAN EnableNetworkMonitoring;
    ULONG MaxEventsPerSecond;          // Rate limiting
    WCHAR ExcludedPaths[10][260];      // Up to 10 excluded paths
    ULONG ExcludedPathCount;
} YOUREDR_CONFIG, *PYOUREDR_CONFIG;

// Error codes
#define YOUREDR_SUCCESS                 0x00000000
#define YOUREDR_ERROR_NO_EVENTS         0xE0000001
#define YOUREDR_ERROR_BUFFER_TOO_SMALL  0xE0000002
#define YOUREDR_ERROR_INVALID_CONFIG    0xE0000003
#define YOUREDR_ERROR_INTERNAL          0xE0000004

#endif // IOCTL_CODES_H
