/*
 * YourEDR - Communication Layer
 * IOCTL handler for user-mode service communication
 *
 * Phase 1: Device IOCTL interface for event retrieval
 */

#include "../include/driver.h"

//
// Forward declarations
//

DRIVER_DISPATCH DeviceCreateClose;
DRIVER_DISPATCH DeviceIoControl;

NTSTATUS
DeviceCreateClose(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

NTSTATUS
DeviceIoControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

//
// Create communication device
//

NTSTATUS
CreateCommunicationDevice(
    _In_ PDRIVER_OBJECT DriverObject
)
{
    NTSTATUS status;
    UNICODE_STRING deviceName;
    UNICODE_STRING symlinkName;

    YOUREDR_LOG_INFO("Creating communication device");

    //
    // Create device name
    //

    RtlInitUnicodeString(&deviceName, YOUREDR_DEVICE_NAME);
    RtlInitUnicodeString(&symlinkName, YOUREDR_SYMLINK_NAME);

    //
    // Create device object
    //

    status = IoCreateDevice(
        DriverObject,
        0,                              // No device extension
        &deviceName,
        FILE_DEVICE_YOUREDR,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &g_GlobalData.DeviceObject
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("IoCreateDevice failed: 0x%08X", status);
        return status;
    }

    //
    // Create symbolic link for user-mode access
    //

    status = IoCreateSymbolicLink(&symlinkName, &deviceName);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("IoCreateSymbolicLink failed: 0x%08X", status);
        IoDeleteDevice(g_GlobalData.DeviceObject);
        g_GlobalData.DeviceObject = NULL;
        return status;
    }

    //
    // Set device characteristics
    //

    g_GlobalData.DeviceObject->Flags |= DO_BUFFERED_IO;
    g_GlobalData.DeviceObject->Flags &= ~DO_DEVICE_INITIALIZING;

    //
    // Set dispatch routines
    //

    DriverObject->MajorFunction[IRP_MJ_CREATE] = DeviceCreateClose;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = DeviceCreateClose;
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DeviceIoControl;

    YOUREDR_LOG_INFO("Communication device created successfully");
    return STATUS_SUCCESS;
}

//
// Delete communication device
//

VOID
DeleteCommunicationDevice(VOID)
{
    UNICODE_STRING symlinkName;

    if (g_GlobalData.DeviceObject != NULL) {
        YOUREDR_LOG_INFO("Deleting communication device");

        //
        // Delete symbolic link
        //

        RtlInitUnicodeString(&symlinkName, YOUREDR_SYMLINK_NAME);
        IoDeleteSymbolicLink(&symlinkName);

        //
        // Delete device object
        //

        IoDeleteDevice(g_GlobalData.DeviceObject);
        g_GlobalData.DeviceObject = NULL;

        YOUREDR_LOG_INFO("Communication device deleted");
    }
}

//
// Device Create/Close handler
//

NTSTATUS
DeviceCreateClose(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    UNREFERENCED_PARAMETER(DeviceObject);

    YOUREDR_LOG_DEBUG("Device Create/Close request");

    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 0;

    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return STATUS_SUCCESS;
}

//
// Device IOCTL handler
//

NTSTATUS
DeviceIoControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    PIO_STACK_LOCATION irpSp;
    ULONG ioControlCode;
    PVOID inputBuffer;
    PVOID outputBuffer;
    ULONG inputBufferLength;
    ULONG outputBufferLength;
    ULONG bytesReturned = 0;

    UNREFERENCED_PARAMETER(DeviceObject);

    irpSp = IoGetCurrentIrpStackLocation(Irp);
    ioControlCode = irpSp->Parameters.DeviceIoControl.IoControlCode;
    inputBufferLength = irpSp->Parameters.DeviceIoControl.InputBufferLength;
    outputBufferLength = irpSp->Parameters.DeviceIoControl.OutputBufferLength;

    //
    // Get system buffer (METHOD_BUFFERED)
    //

    inputBuffer = Irp->AssociatedIrp.SystemBuffer;
    outputBuffer = Irp->AssociatedIrp.SystemBuffer;

    //
    // Process IOCTL request
    //

    switch (ioControlCode) {

    case IOCTL_YOUREDR_GET_VERSION:
    {
        PYOUREDR_VERSION version;

        YOUREDR_LOG_DEBUG("IOCTL_YOUREDR_GET_VERSION");

        if (outputBufferLength < sizeof(YOUREDR_VERSION)) {
            status = STATUS_BUFFER_TOO_SMALL;
            break;
        }

        version = (PYOUREDR_VERSION)outputBuffer;
        version->MajorVersion = YOUREDR_MAJOR_VERSION;
        version->MinorVersion = YOUREDR_MINOR_VERSION;
        version->PatchVersion = YOUREDR_PATCH_VERSION;
        version->BuildNumber = YOUREDR_BUILD_NUMBER;

        bytesReturned = sizeof(YOUREDR_VERSION);
        status = STATUS_SUCCESS;
        break;
    }

    case IOCTL_YOUREDR_GET_EVENT:
    {
        YOUREDR_LOG_DEBUG("IOCTL_YOUREDR_GET_EVENT");

        if (outputBufferLength < sizeof(EDR_EVENT_HEADER)) {
            status = STATUS_BUFFER_TOO_SMALL;
            break;
        }

        //
        // Dequeue event from ring buffer
        //

        status = DequeueEvent(
            &g_GlobalData.RingBuffer,
            outputBuffer,
            outputBufferLength,
            &bytesReturned
        );

        if (status == STATUS_NO_MORE_ENTRIES) {
            // No events available
            bytesReturned = 0;
            status = STATUS_SUCCESS;
        }

        break;
    }

    case IOCTL_YOUREDR_SET_CONFIG:
    {
        PYOUREDR_CONFIG config;

        YOUREDR_LOG_DEBUG("IOCTL_YOUREDR_SET_CONFIG");

        if (inputBufferLength < sizeof(YOUREDR_CONFIG)) {
            status = STATUS_BUFFER_TOO_SMALL;
            break;
        }

        config = (PYOUREDR_CONFIG)inputBuffer;

        //
        // Validate configuration
        //

        if (config->MaxEventsPerSecond > 100000 ||
            config->ExcludedPathCount > 10) {
            status = STATUS_INVALID_PARAMETER;
            break;
        }

        //
        // Update global configuration
        //

        RtlCopyMemory(
            &g_GlobalData.Config,
            config,
            sizeof(YOUREDR_CONFIG)
        );

        YOUREDR_LOG_INFO("Configuration updated");
        status = STATUS_SUCCESS;
        break;
    }

    case IOCTL_YOUREDR_GET_STATS:
    {
        PYOUREDR_STATS stats;

        YOUREDR_LOG_DEBUG("IOCTL_YOUREDR_GET_STATS");

        if (outputBufferLength < sizeof(YOUREDR_STATS)) {
            status = STATUS_BUFFER_TOO_SMALL;
            break;
        }

        stats = (PYOUREDR_STATS)outputBuffer;

        //
        // Collect statistics
        //

        stats->TotalEventsQueued = g_GlobalData.RingBuffer.TotalEventsQueued;
        stats->TotalEventsDropped = g_GlobalData.RingBuffer.TotalEventsDropped;
        stats->TotalEventsRead = 0;  // TODO: Track in service
        stats->RingBufferSize = g_GlobalData.RingBuffer.Size;

        // Calculate current usage
        if (g_GlobalData.RingBuffer.WriteOffset >= g_GlobalData.RingBuffer.ReadOffset) {
            stats->RingBufferUsedBytes =
                g_GlobalData.RingBuffer.WriteOffset - g_GlobalData.RingBuffer.ReadOffset;
        } else {
            stats->RingBufferUsedBytes =
                g_GlobalData.RingBuffer.Size -
                (g_GlobalData.RingBuffer.ReadOffset - g_GlobalData.RingBuffer.WriteOffset);
        }

        stats->CurrentQueuedEvents = 0;  // Approximation needed

        bytesReturned = sizeof(YOUREDR_STATS);
        status = STATUS_SUCCESS;
        break;
    }

    case IOCTL_YOUREDR_CLEAR_EVENTS:
    {
        YOUREDR_LOG_DEBUG("IOCTL_YOUREDR_CLEAR_EVENTS");

        //
        // Reset ring buffer pointers
        //

        g_GlobalData.RingBuffer.WriteOffset = 0;
        g_GlobalData.RingBuffer.ReadOffset = 0;

        YOUREDR_LOG_INFO("Event queue cleared");
        status = STATUS_SUCCESS;
        break;
    }

    default:
        YOUREDR_LOG_WARNING("Unknown IOCTL code: 0x%08X", ioControlCode);
        status = STATUS_INVALID_DEVICE_REQUEST;
        break;
    }

    //
    // Complete IRP
    //

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = bytesReturned;

    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}
