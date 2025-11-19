/*
 * YourEDR - Event Logger
 * Ring buffer implementation for event queuing
 *
 * Phase 1: Lock-free SPSC ring buffer with 2MB capacity
 */

#include "../include/driver.h"

//
// Initialize ring buffer
//

NTSTATUS
InitializeRingBuffer(
    _Out_ PYOUREDR_RING_BUFFER RingBuffer
)
{
    YOUREDR_LOG_INFO("Initializing ring buffer (Size: %d bytes)", RING_BUFFER_SIZE);

    //
    // Zero out structure
    //

    RtlZeroMemory(RingBuffer, sizeof(YOUREDR_RING_BUFFER));

    //
    // Allocate ring buffer memory from non-paged pool
    // IMPORTANT: Must be non-paged as we may be at DISPATCH_LEVEL
    //

    RingBuffer->Buffer = (PUCHAR)ExAllocatePoolWithTag(
        NonPagedPool,
        RING_BUFFER_SIZE,
        YOUREDR_BUFFER_TAG
    );

    if (RingBuffer->Buffer == NULL) {
        YOUREDR_LOG_ERROR("Failed to allocate ring buffer memory");
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    //
    // Initialize fields
    //

    RingBuffer->Size = RING_BUFFER_SIZE;
    RingBuffer->WriteOffset = 0;
    RingBuffer->ReadOffset = 0;
    RingBuffer->TotalEventsQueued = 0;
    RingBuffer->TotalEventsDropped = 0;

    //
    // Initialize spinlock for synchronization
    //

    KeInitializeSpinLock(&RingBuffer->Lock);

    //
    // Initialize event for signaling data availability
    //

    KeInitializeEvent(
        &RingBuffer->DataAvailableEvent,
        NotificationEvent,
        FALSE
    );

    YOUREDR_LOG_INFO("Ring buffer initialized successfully");
    return STATUS_SUCCESS;
}

//
// Cleanup ring buffer
//

VOID
CleanupRingBuffer(
    _In_ PYOUREDR_RING_BUFFER RingBuffer
)
{
    if (RingBuffer->Buffer != NULL) {
        YOUREDR_LOG_INFO("Cleaning up ring buffer");
        YOUREDR_LOG_INFO("Statistics - Queued: %llu, Dropped: %llu",
            RingBuffer->TotalEventsQueued,
            RingBuffer->TotalEventsDropped);

        ExFreePoolWithTag(RingBuffer->Buffer, YOUREDR_BUFFER_TAG);
        RingBuffer->Buffer = NULL;
    }
}

//
// Queue event to ring buffer
//

NTSTATUS
QueueEvent(
    _In_ PYOUREDR_RING_BUFFER RingBuffer,
    _In_ PVOID EventData,
    _In_ ULONG EventSize
)
{
    KIRQL oldIrql;
    ULONG totalSize;
    ULONG writeOffset;
    ULONG readOffset;
    ULONG availableSpace;
    PRING_BUFFER_ENTRY entry;

    //
    // Validate parameters
    //

    if (RingBuffer == NULL || EventData == NULL || EventSize == 0) {
        return STATUS_INVALID_PARAMETER;
    }

    if (EventSize > EDR_MAX_EVENT_SIZE) {
        YOUREDR_LOG_WARNING("Event too large: %d bytes", EventSize);
        return STATUS_INVALID_PARAMETER;
    }

    //
    // Calculate total size (entry header + event data)
    //

    totalSize = FIELD_OFFSET(RING_BUFFER_ENTRY, EventData) + EventSize;

    //
    // Align to 8-byte boundary
    //

    totalSize = (totalSize + 7) & ~7;

    //
    // Acquire spinlock
    //

    KeAcquireSpinLock(&RingBuffer->Lock, &oldIrql);

    writeOffset = RingBuffer->WriteOffset;
    readOffset = RingBuffer->ReadOffset;

    //
    // Calculate available space
    //

    if (writeOffset >= readOffset) {
        availableSpace = RingBuffer->Size - writeOffset + readOffset;
    } else {
        availableSpace = readOffset - writeOffset;
    }

    //
    // Check if we have enough space
    //

    if (availableSpace < totalSize) {
        RingBuffer->TotalEventsDropped++;
        KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);
        YOUREDR_LOG_DEBUG("Ring buffer full, event dropped");
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    //
    // Handle wrap-around case
    //

    if (writeOffset + totalSize > RingBuffer->Size) {
        //
        // Not enough space at end, wrap to beginning
        // Write a marker entry with Size=0 to indicate wrap
        //

        if (writeOffset < RingBuffer->Size) {
            entry = (PRING_BUFFER_ENTRY)(RingBuffer->Buffer + writeOffset);
            entry->Size = 0;  // Wrap marker
        }

        writeOffset = 0;

        //
        // Check again if we have space at the beginning
        //

        if (readOffset <= totalSize) {
            RingBuffer->TotalEventsDropped++;
            KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);
            YOUREDR_LOG_DEBUG("Ring buffer wrap failed, event dropped");
            return STATUS_INSUFFICIENT_RESOURCES;
        }
    }

    //
    // Write entry to ring buffer
    //

    entry = (PRING_BUFFER_ENTRY)(RingBuffer->Buffer + writeOffset);
    entry->Size = totalSize;

    RtlCopyMemory(entry->EventData, EventData, EventSize);

    //
    // Update write offset
    //

    RingBuffer->WriteOffset = writeOffset + totalSize;
    RingBuffer->TotalEventsQueued++;

    //
    // Signal that data is available
    //

    KeSetEvent(&RingBuffer->DataAvailableEvent, IO_NO_INCREMENT, FALSE);

    //
    // Release spinlock
    //

    KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);

    return STATUS_SUCCESS;
}

//
// Dequeue event from ring buffer
//

NTSTATUS
DequeueEvent(
    _In_ PYOUREDR_RING_BUFFER RingBuffer,
    _Out_writes_bytes_(BufferSize) PVOID Buffer,
    _In_ ULONG BufferSize,
    _Out_ PULONG BytesReturned
)
{
    KIRQL oldIrql;
    ULONG writeOffset;
    ULONG readOffset;
    PRING_BUFFER_ENTRY entry;
    ULONG eventSize;

    //
    // Validate parameters
    //

    if (RingBuffer == NULL || Buffer == NULL || BytesReturned == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    *BytesReturned = 0;

    //
    // Acquire spinlock
    //

    KeAcquireSpinLock(&RingBuffer->Lock, &oldIrql);

    writeOffset = RingBuffer->WriteOffset;
    readOffset = RingBuffer->ReadOffset;

    //
    // Check if buffer is empty
    //

    if (readOffset == writeOffset) {
        KeClearEvent(&RingBuffer->DataAvailableEvent);
        KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);
        return STATUS_NO_MORE_ENTRIES;
    }

    //
    // Get entry at read offset
    //

    entry = (PRING_BUFFER_ENTRY)(RingBuffer->Buffer + readOffset);

    //
    // Check for wrap marker (Size=0)
    //

    if (entry->Size == 0) {
        //
        // Wrap to beginning
        //

        readOffset = 0;
        RingBuffer->ReadOffset = 0;

        //
        // Check again if buffer is empty after wrap
        //

        if (readOffset == writeOffset) {
            KeClearEvent(&RingBuffer->DataAvailableEvent);
            KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);
            return STATUS_NO_MORE_ENTRIES;
        }

        entry = (PRING_BUFFER_ENTRY)(RingBuffer->Buffer + readOffset);
    }

    //
    // Calculate event data size (exclude entry header)
    //

    eventSize = entry->Size - FIELD_OFFSET(RING_BUFFER_ENTRY, EventData);

    //
    // Check if caller's buffer is large enough
    //

    if (BufferSize < eventSize) {
        KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);
        return STATUS_BUFFER_TOO_SMALL;
    }

    //
    // Copy event data to caller's buffer
    //

    RtlCopyMemory(Buffer, entry->EventData, eventSize);
    *BytesReturned = eventSize;

    //
    // Update read offset
    //

    RingBuffer->ReadOffset = readOffset + entry->Size;

    //
    // Release spinlock
    //

    KeReleaseSpinLock(&RingBuffer->Lock, oldIrql);

    return STATUS_SUCCESS;
}

//
// Get next sequence number
//

ULONGLONG
GetNextSequenceNumber(VOID)
{
    KIRQL oldIrql;
    ULONGLONG sequenceNumber;

    KeAcquireSpinLock(&g_GlobalData.SequenceLock, &oldIrql);
    sequenceNumber = ++g_GlobalData.SequenceNumber;
    KeReleaseSpinLock(&g_GlobalData.SequenceLock, oldIrql);

    return sequenceNumber;
}

//
// Get current timestamp
//

VOID
GetCurrentTimestamp(
    _Out_ PLARGE_INTEGER Timestamp
)
{
    KeQuerySystemTime(Timestamp);
}
