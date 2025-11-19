/*
 * YourEDR - Mini-Filter Driver
 * Main driver entry point and initialization
 *
 * Phase 1: File system monitoring with JSON logging
 */

#include "../include/driver.h"

//
// Global data
//

YOUREDR_GLOBAL_DATA g_GlobalData = {0};

//
// Filter registration structure
//

CONST FLT_OPERATION_REGISTRATION Callbacks[] = {
    {
        IRP_MJ_CREATE,
        0,
        PreCreateOperation,
        NULL
    },
    {
        IRP_MJ_WRITE,
        0,
        PreWriteOperation,
        NULL
    },
    {
        IRP_MJ_SET_INFORMATION,
        0,
        PreSetInformationOperation,
        NULL
    },
    { IRP_MJ_OPERATION_END }
};

CONST FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),           // Size
    FLT_REGISTRATION_VERSION,           // Version
    0,                                  // Flags
    NULL,                               // Context
    Callbacks,                          // Operation callbacks
    YourEDRUnload,                      // FilterUnload
    YourEDRInstanceSetup,               // InstanceSetup
    YourEDRInstanceQueryTeardown,       // InstanceQueryTeardown
    NULL,                               // InstanceTeardownStart
    NULL,                               // InstanceTeardownComplete
    NULL,                               // GenerateFileName
    NULL,                               // NormalizeNameComponent
    NULL,                               // NormalizeContextCleanup
    NULL,                               // TransactionNotification
    NULL,                               // NormalizeNameComponentEx
    NULL                                // SectionNotification
};

//
// Driver Entry Point
//

NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;

    UNREFERENCED_PARAMETER(RegistryPath);

    YOUREDR_LOG_INFO("YourEDR Driver Loading - Version %d.%d.%d Build %d",
        YOUREDR_MAJOR_VERSION,
        YOUREDR_MINOR_VERSION,
        YOUREDR_PATCH_VERSION,
        YOUREDR_BUILD_NUMBER);

    //
    // Initialize global data structure
    //

    RtlZeroMemory(&g_GlobalData, sizeof(YOUREDR_GLOBAL_DATA));
    KeInitializeSpinLock(&g_GlobalData.SequenceLock);
    g_GlobalData.SequenceNumber = 0;

    //
    // Initialize default configuration
    //

    g_GlobalData.Config.EnableFileMonitoring = TRUE;
    g_GlobalData.Config.EnableProcessMonitoring = FALSE;  // Future Phase
    g_GlobalData.Config.EnableNetworkMonitoring = TRUE;   // Phase 2 - NOW ENABLED
    g_GlobalData.Config.MaxEventsPerSecond = 10000;
    g_GlobalData.Config.ExcludedPathCount = 0;

    //
    // Initialize ring buffer for event queuing
    //

    status = InitializeRingBuffer(&g_GlobalData.RingBuffer);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("Failed to initialize ring buffer: 0x%08X", status);
        return status;
    }

    //
    // Register with Filter Manager
    //

    status = FltRegisterFilter(
        DriverObject,
        &FilterRegistration,
        &g_GlobalData.FilterHandle
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FltRegisterFilter failed: 0x%08X", status);
        CleanupRingBuffer(&g_GlobalData.RingBuffer);
        return status;
    }

    //
    // Create communication device for IOCTL interface
    //

    status = CreateCommunicationDevice(DriverObject);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("Failed to create communication device: 0x%08X", status);
        FltUnregisterFilter(g_GlobalData.FilterHandle);
        CleanupRingBuffer(&g_GlobalData.RingBuffer);
        return status;
    }

    //
    // Initialize network monitoring (WFP) - Phase 2
    //

    if (g_GlobalData.Config.EnableNetworkMonitoring) {
        status = InitializeNetworkMonitoring(g_GlobalData.DeviceObject);
        if (!NT_SUCCESS(status)) {
            YOUREDR_LOG_WARNING("Failed to initialize network monitoring: 0x%08X (continuing without network monitoring)", status);
            g_GlobalData.Config.EnableNetworkMonitoring = FALSE;
            // Don't fail driver load if WFP fails, just disable network monitoring
        }
    }

    //
    // Start filtering I/O
    //

    status = FltStartFiltering(g_GlobalData.FilterHandle);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FltStartFiltering failed: 0x%08X", status);
        DeleteCommunicationDevice();
        FltUnregisterFilter(g_GlobalData.FilterHandle);
        CleanupRingBuffer(&g_GlobalData.RingBuffer);
        return status;
    }

    YOUREDR_LOG_INFO("YourEDR Driver Loaded Successfully");
    return STATUS_SUCCESS;
}

//
// Filter Unload
//

NTSTATUS
YourEDRUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
)
{
    UNREFERENCED_PARAMETER(Flags);

    YOUREDR_LOG_INFO("YourEDR Driver Unloading");

    //
    // Cleanup network monitoring (WFP) - Phase 2
    //

    CleanupNetworkMonitoring();

    //
    // Delete communication device
    //

    DeleteCommunicationDevice();

    //
    // Unregister filter
    //

    if (g_GlobalData.FilterHandle != NULL) {
        FltUnregisterFilter(g_GlobalData.FilterHandle);
        g_GlobalData.FilterHandle = NULL;
    }

    //
    // Cleanup ring buffer
    //

    CleanupRingBuffer(&g_GlobalData.RingBuffer);

    YOUREDR_LOG_INFO("YourEDR Driver Unloaded Successfully");
    return STATUS_SUCCESS;
}

//
// Instance Setup
//

NTSTATUS
YourEDRInstanceSetup(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_SETUP_FLAGS Flags,
    _In_ DEVICE_TYPE VolumeDeviceType,
    _In_ FLT_FILESYSTEM_TYPE VolumeFilesystemType
)
{
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);
    UNREFERENCED_PARAMETER(VolumeDeviceType);

    //
    // Attach to NTFS and ReFS volumes only (Phase 1)
    //

    if (VolumeFilesystemType == FLT_FSTYPE_NTFS ||
        VolumeFilesystemType == FLT_FSTYPE_REFS) {

        YOUREDR_LOG_DEBUG("Attaching to volume (FS Type: %d)", VolumeFilesystemType);
        return STATUS_SUCCESS;
    }

    //
    // Don't attach to other file systems
    //

    return STATUS_FLT_DO_NOT_ATTACH;
}

//
// Instance Query Teardown
//

NTSTATUS
YourEDRInstanceQueryTeardown(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_QUERY_TEARDOWN_FLAGS Flags
)
{
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);

    YOUREDR_LOG_DEBUG("Instance teardown requested");
    return STATUS_SUCCESS;
}
