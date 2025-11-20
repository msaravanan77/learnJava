// Unit tests for Ring Buffer implementation
// Framework: GoogleTest
// Build: Requires WDK and GoogleTest

#include <gtest/gtest.h>
#include <windows.h>

// Mock kernel functions for user-mode testing
extern "C" {
    // Mock implementations
    PVOID ExAllocatePoolWithTag(POOL_TYPE PoolType, SIZE_T NumberOfBytes, ULONG Tag) {
        return malloc(NumberOfBytes);
    }

    VOID ExFreePoolWithTag(PVOID P, ULONG Tag) {
        free(P);
    }

    VOID KeInitializeSpinLock(PKSPIN_LOCK SpinLock) {
        *SpinLock = 0;
    }

    VOID KeAcquireSpinLock(PKSPIN_LOCK SpinLock, PKIRQL OldIrql) {
        *OldIrql = 0;
        // In real tests, use proper synchronization
    }

    VOID KeReleaseSpinLock(PKSPIN_LOCK SpinLock, KIRQL NewIrql) {
        // Mock release
    }

    VOID KeInitializeEvent(PRKEVENT Event, EVENT_TYPE Type, BOOLEAN State) {
        // Mock event init
    }

    LONG KeSetEvent(PRKEVENT Event, KPRIORITY Increment, BOOLEAN Wait) {
        return 0;
    }
}

// Include ring buffer implementation (for testing)
// Note: In production, this would link against compiled driver code
#define RING_BUFFER_SIZE (2 * 1024 * 1024)  // 2 MB

typedef struct _YOUREDR_RING_BUFFER {
    PUCHAR Buffer;
    ULONG Size;
    volatile ULONG WriteOffset;
    volatile ULONG ReadOffset;
    KSPIN_LOCK Lock;
    KEVENT DataAvailableEvent;
    ULONGLONG TotalEventsQueued;
    ULONGLONG TotalEventsDropped;
} YOUREDR_RING_BUFFER;

// Test fixture
class RingBufferTest : public ::testing::Test {
protected:
    YOUREDR_RING_BUFFER* ringBuffer;

    void SetUp() override {
        ringBuffer = (YOUREDR_RING_BUFFER*)malloc(sizeof(YOUREDR_RING_BUFFER));
        memset(ringBuffer, 0, sizeof(YOUREDR_RING_BUFFER));

        ringBuffer->Buffer = (PUCHAR)ExAllocatePoolWithTag(NonPagedPool, RING_BUFFER_SIZE, 'RBUF');
        ringBuffer->Size = RING_BUFFER_SIZE;
        ringBuffer->WriteOffset = 0;
        ringBuffer->ReadOffset = 0;
        ringBuffer->TotalEventsQueued = 0;
        ringBuffer->TotalEventsDropped = 0;

        KeInitializeSpinLock(&ringBuffer->Lock);
        KeInitializeEvent(&ringBuffer->DataAvailableEvent, NotificationEvent, FALSE);
    }

    void TearDown() override {
        if (ringBuffer) {
            if (ringBuffer->Buffer) {
                ExFreePoolWithTag(ringBuffer->Buffer, 'RBUF');
            }
            free(ringBuffer);
        }
    }
};

// Test: Initialize ring buffer
TEST_F(RingBufferTest, InitializeSuccess) {
    ASSERT_NE(ringBuffer, nullptr);
    ASSERT_NE(ringBuffer->Buffer, nullptr);
    ASSERT_EQ(ringBuffer->Size, RING_BUFFER_SIZE);
    ASSERT_EQ(ringBuffer->WriteOffset, 0);
    ASSERT_EQ(ringBuffer->ReadOffset, 0);
    ASSERT_EQ(ringBuffer->TotalEventsQueued, 0);
    ASSERT_EQ(ringBuffer->TotalEventsDropped, 0);
}

// Test: Queue single event
TEST_F(RingBufferTest, QueueSingleEvent) {
    // Create test event
    struct TestEvent {
        ULONG EventType;
        ULONG ProcessId;
        CHAR Data[100];
    } testEvent;

    testEvent.EventType = 1;
    testEvent.ProcessId = 1234;
    strcpy_s(testEvent.Data, "Test data");

    ULONG eventSize = sizeof(TestEvent);
    ULONG totalSize = sizeof(ULONG) + eventSize;  // Size header + event

    // Simulate QueueEvent logic
    KIRQL oldIrql;
    KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);

    // Write size
    *(ULONG*)(ringBuffer->Buffer + ringBuffer->WriteOffset) = eventSize;
    ringBuffer->WriteOffset += sizeof(ULONG);

    // Write event
    memcpy(ringBuffer->Buffer + ringBuffer->WriteOffset, &testEvent, eventSize);
    ringBuffer->WriteOffset += eventSize;

    ringBuffer->TotalEventsQueued++;
    KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

    // Verify
    ASSERT_EQ(ringBuffer->WriteOffset, totalSize);
    ASSERT_EQ(ringBuffer->TotalEventsQueued, 1);
    ASSERT_EQ(ringBuffer->TotalEventsDropped, 0);
}

// Test: Queue and dequeue event
TEST_F(RingBufferTest, QueueAndDequeueEvent) {
    struct TestEvent {
        ULONG EventType;
        ULONG ProcessId;
    } testEvent, readEvent;

    testEvent.EventType = 5;
    testEvent.ProcessId = 9999;

    ULONG eventSize = sizeof(TestEvent);

    // Queue event
    KIRQL oldIrql;
    KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);
    *(ULONG*)(ringBuffer->Buffer + ringBuffer->WriteOffset) = eventSize;
    ringBuffer->WriteOffset += sizeof(ULONG);
    memcpy(ringBuffer->Buffer + ringBuffer->WriteOffset, &testEvent, eventSize);
    ringBuffer->WriteOffset += eventSize;
    ringBuffer->TotalEventsQueued++;
    KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

    // Dequeue event
    KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);
    ULONG size = *(ULONG*)(ringBuffer->Buffer + ringBuffer->ReadOffset);
    ringBuffer->ReadOffset += sizeof(ULONG);
    memcpy(&readEvent, ringBuffer->Buffer + ringBuffer->ReadOffset, size);
    ringBuffer->ReadOffset += size;
    KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

    // Verify
    ASSERT_EQ(readEvent.EventType, 5);
    ASSERT_EQ(readEvent.ProcessId, 9999);
    ASSERT_EQ(ringBuffer->ReadOffset, ringBuffer->WriteOffset);
}

// Test: Buffer wrap-around
TEST_F(RingBufferTest, BufferWrapAround) {
    // Fill buffer almost to the end
    ringBuffer->WriteOffset = RING_BUFFER_SIZE - 100;
    ringBuffer->ReadOffset = RING_BUFFER_SIZE - 100;

    // Try to write event larger than remaining space
    ULONG eventSize = 200;
    ULONG totalSize = sizeof(ULONG) + eventSize;

    KIRQL oldIrql;
    KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);

    // Check if we need to wrap
    if (ringBuffer->WriteOffset + totalSize > RING_BUFFER_SIZE) {
        // Write wrap marker (size = 0)
        *(ULONG*)(ringBuffer->Buffer + ringBuffer->WriteOffset) = 0;
        ringBuffer->WriteOffset = 0;  // Wrap to beginning
    }

    KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

    // Verify wrapped to beginning
    ASSERT_EQ(ringBuffer->WriteOffset, 0);
}

// Test: Buffer full scenario
TEST_F(RingBufferTest, BufferFullDrop) {
    // Simulate buffer full by setting write offset close to read offset
    ringBuffer->ReadOffset = 1000;
    ringBuffer->WriteOffset = RING_BUFFER_SIZE - 500;

    ULONG eventSize = 1000;
    ULONG totalSize = sizeof(ULONG) + eventSize;

    // Calculate available space
    KIRQL oldIrql;
    KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);

    ULONG availableSpace;
    if (ringBuffer->WriteOffset >= ringBuffer->ReadOffset) {
        availableSpace = RING_BUFFER_SIZE - ringBuffer->WriteOffset + ringBuffer->ReadOffset;
    } else {
        availableSpace = ringBuffer->ReadOffset - ringBuffer->WriteOffset;
    }

    BOOL dropped = FALSE;
    if (totalSize > availableSpace) {
        ringBuffer->TotalEventsDropped++;
        dropped = TRUE;
    }

    KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

    // Verify event was dropped
    ASSERT_TRUE(dropped);
    ASSERT_EQ(ringBuffer->TotalEventsDropped, 1);
}

// Test: Multiple events queue/dequeue
TEST_F(RingBufferTest, MultipleEvents) {
    const int NUM_EVENTS = 100;

    struct TestEvent {
        ULONG SequenceNumber;
    } testEvent;

    // Queue multiple events
    for (int i = 0; i < NUM_EVENTS; i++) {
        testEvent.SequenceNumber = i;
        ULONG eventSize = sizeof(TestEvent);

        KIRQL oldIrql;
        KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);
        *(ULONG*)(ringBuffer->Buffer + ringBuffer->WriteOffset) = eventSize;
        ringBuffer->WriteOffset += sizeof(ULONG);
        memcpy(ringBuffer->Buffer + ringBuffer->WriteOffset, &testEvent, eventSize);
        ringBuffer->WriteOffset += eventSize;
        ringBuffer->TotalEventsQueued++;
        KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);
    }

    ASSERT_EQ(ringBuffer->TotalEventsQueued, NUM_EVENTS);

    // Dequeue and verify
    for (int i = 0; i < NUM_EVENTS; i++) {
        TestEvent readEvent;
        KIRQL oldIrql;
        KeAcquireSpinLock(&ringBuffer->Lock, &oldIrql);
        ULONG size = *(ULONG*)(ringBuffer->Buffer + ringBuffer->ReadOffset);
        ringBuffer->ReadOffset += sizeof(ULONG);
        memcpy(&readEvent, ringBuffer->Buffer + ringBuffer->ReadOffset, size);
        ringBuffer->ReadOffset += size;
        KeReleaseSpinLock(&ringBuffer->Lock, oldIrql);

        ASSERT_EQ(readEvent.SequenceNumber, i);
    }

    // Buffer should be empty
    ASSERT_EQ(ringBuffer->ReadOffset, ringBuffer->WriteOffset);
}

// Main function
int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
