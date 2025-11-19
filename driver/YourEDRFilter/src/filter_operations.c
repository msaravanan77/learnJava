/*
 * YourEDR - Filter Operation Callbacks
 * Handles file system operations (IRP_MJ_CREATE, IRP_MJ_WRITE, etc.)
 *
 * Phase 1: File create/write/delete/rename monitoring
 */

#include "../include/driver.h"

//
// Helper function to check if path should be excluded
//

BOOLEAN
IsPathExcluded(
    _In_ PCUNICODE_STRING FilePath
)
{
    ULONG i;
    UNICODE_STRING excludedPath;

    for (i = 0; i < g_GlobalData.Config.ExcludedPathCount; i++) {
        RtlInitUnicodeString(&excludedPath, g_GlobalData.Config.ExcludedPaths[i]);

        // Simple prefix match (case-insensitive)
        if (RtlPrefixUnicodeString(&excludedPath, FilePath, TRUE)) {
            return TRUE;
        }
    }

    return FALSE;
}

//
// Helper function to get file path from callback data
//

NTSTATUS
GetFilePath(
    _In_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Out_writes_(MaxLength) PWCHAR FilePathBuffer,
    _In_ ULONG MaxLength
)
{
    NTSTATUS status;
    PFLT_FILE_NAME_INFORMATION nameInfo = NULL;

    //
    // Get file name information
    //

    status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &nameInfo
    );

    if (!NT_SUCCESS(status)) {
        return status;
    }

    //
    // Parse the name
    //

    status = FltParseFileNameInformation(nameInfo);
    if (!NT_SUCCESS(status)) {
        FltReleaseFileNameInformation(nameInfo);
        return status;
    }

    //
    // Copy to buffer (truncate if necessary)
    //

    if (nameInfo->Name.Length > 0) {
        ULONG copyLength = min(
            nameInfo->Name.Length / sizeof(WCHAR),
            MaxLength - 1
        );

        RtlCopyMemory(
            FilePathBuffer,
            nameInfo->Name.Buffer,
            copyLength * sizeof(WCHAR)
        );

        FilePathBuffer[copyLength] = L'\0';
    } else {
        FilePathBuffer[0] = L'\0';
        status = STATUS_UNSUCCESSFUL;
    }

    FltReleaseFileNameInformation(nameInfo);
    return status;
}

//
// IRP_MJ_CREATE callback (file open/create operations)
//

FLT_PREOP_CALLBACK_STATUS
PreCreateOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    EDR_FILE_EVENT fileEvent;
    PFLT_FILE_NAME_INFORMATION nameInfo = NULL;

    UNREFERENCED_PARAMETER(CompletionContext);

    //
    // Only process if file monitoring is enabled
    //

    if (!g_GlobalData.Config.EnableFileMonitoring) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Ignore kernel-mode requests
    //

    if (Data->RequestorMode == KernelMode) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Get file path
    //

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

    //
    // Check if path should be excluded
    //

    if (IsPathExcluded(&nameInfo->Name)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Build file event structure
    //

    RtlZeroMemory(&fileEvent, sizeof(EDR_FILE_EVENT));

    // Fill header
    fileEvent.Header.EventSize = sizeof(EDR_FILE_EVENT);
    fileEvent.Header.EventType = EventTypeFileCreate;
    GetCurrentTimestamp(&fileEvent.Header.Timestamp);
    fileEvent.Header.ProcessId = HandleToUlong(PsGetCurrentProcessId());
    fileEvent.Header.ThreadId = HandleToUlong(PsGetCurrentThreadId());
    fileEvent.Header.SessionId = 0;  // TODO: Get actual session ID
    fileEvent.Header.IntegrityLevel = 0;  // TODO: Get integrity level
    fileEvent.Header.SequenceNumber = GetNextSequenceNumber();

    // Fill file-specific data
    fileEvent.DesiredAccess = Data->Iopb->Parameters.Create.SecurityContext->DesiredAccess;
    fileEvent.CreateDisposition = (Data->Iopb->Parameters.Create.Options >> 24) & 0xFF;
    fileEvent.CreateOptions = Data->Iopb->Parameters.Create.Options & 0x00FFFFFF;

    // Copy file path (truncate if necessary)
    {
        ULONG copyLength = min(
            nameInfo->Name.Length / sizeof(WCHAR),
            519  // Max 519 chars + null terminator
        );

        RtlCopyMemory(
            fileEvent.FilePath,
            nameInfo->Name.Buffer,
            copyLength * sizeof(WCHAR)
        );

        fileEvent.FilePath[copyLength] = L'\0';
    }

    fileEvent.FileSize = 0;  // Unknown at create time
    fileEvent.CreationTime.QuadPart = 0;
    fileEvent.LastWriteTime.QuadPart = 0;

    FltReleaseFileNameInformation(nameInfo);

    //
    // Queue event to ring buffer
    //

    status = QueueEvent(
        &g_GlobalData.RingBuffer,
        &fileEvent,
        sizeof(EDR_FILE_EVENT)
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_DEBUG("Failed to queue file create event: 0x%08X", status);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

//
// IRP_MJ_WRITE callback (file write operations)
//

FLT_PREOP_CALLBACK_STATUS
PreWriteOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    EDR_FILE_EVENT fileEvent;
    WCHAR filePathBuffer[520];

    UNREFERENCED_PARAMETER(CompletionContext);

    //
    // Only process if file monitoring is enabled
    //

    if (!g_GlobalData.Config.EnableFileMonitoring) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Ignore kernel-mode requests
    //

    if (Data->RequestorMode == KernelMode) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Get file path
    //

    status = GetFilePath(Data, FltObjects, filePathBuffer, 520);
    if (!NT_SUCCESS(status)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Build file event structure
    //

    RtlZeroMemory(&fileEvent, sizeof(EDR_FILE_EVENT));

    // Fill header
    fileEvent.Header.EventSize = sizeof(EDR_FILE_EVENT);
    fileEvent.Header.EventType = EventTypeFileWrite;
    GetCurrentTimestamp(&fileEvent.Header.Timestamp);
    fileEvent.Header.ProcessId = HandleToUlong(PsGetCurrentProcessId());
    fileEvent.Header.ThreadId = HandleToUlong(PsGetCurrentThreadId());
    fileEvent.Header.SessionId = 0;
    fileEvent.Header.IntegrityLevel = 0;
    fileEvent.Header.SequenceNumber = GetNextSequenceNumber();

    // Fill file-specific data
    RtlStringCchCopyW(fileEvent.FilePath, 520, filePathBuffer);
    fileEvent.DesiredAccess = FILE_WRITE_DATA;
    fileEvent.FileSize = Data->Iopb->Parameters.Write.Length;

    //
    // Queue event to ring buffer
    //

    status = QueueEvent(
        &g_GlobalData.RingBuffer,
        &fileEvent,
        sizeof(EDR_FILE_EVENT)
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_DEBUG("Failed to queue file write event: 0x%08X", status);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

//
// IRP_MJ_SET_INFORMATION callback (file delete/rename operations)
//

FLT_PREOP_CALLBACK_STATUS
PreSetInformationOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    EDR_FILE_EVENT fileEvent;
    WCHAR filePathBuffer[520];
    FILE_INFORMATION_CLASS infoClass;

    UNREFERENCED_PARAMETER(CompletionContext);

    //
    // Only process if file monitoring is enabled
    //

    if (!g_GlobalData.Config.EnableFileMonitoring) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Ignore kernel-mode requests
    //

    if (Data->RequestorMode == KernelMode) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Get information class
    //

    infoClass = Data->Iopb->Parameters.SetFileInformation.FileInformationClass;

    //
    // We're interested in delete and rename operations only
    //

    if (infoClass != FileDispositionInformation &&
        infoClass != FileDispositionInformationEx &&
        infoClass != FileRenameInformation &&
        infoClass != FileRenameInformationEx) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Get file path
    //

    status = GetFilePath(Data, FltObjects, filePathBuffer, 520);
    if (!NT_SUCCESS(status)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    //
    // Build file event structure
    //

    RtlZeroMemory(&fileEvent, sizeof(EDR_FILE_EVENT));

    // Fill header
    fileEvent.Header.EventSize = sizeof(EDR_FILE_EVENT);

    if (infoClass == FileDispositionInformation ||
        infoClass == FileDispositionInformationEx) {
        fileEvent.Header.EventType = EventTypeFileDelete;
    } else {
        fileEvent.Header.EventType = EventTypeFileRename;
    }

    GetCurrentTimestamp(&fileEvent.Header.Timestamp);
    fileEvent.Header.ProcessId = HandleToUlong(PsGetCurrentProcessId());
    fileEvent.Header.ThreadId = HandleToUlong(PsGetCurrentThreadId());
    fileEvent.Header.SessionId = 0;
    fileEvent.Header.IntegrityLevel = 0;
    fileEvent.Header.SequenceNumber = GetNextSequenceNumber();

    // Fill file-specific data
    RtlStringCchCopyW(fileEvent.FilePath, 520, filePathBuffer);

    //
    // Queue event to ring buffer
    //

    status = QueueEvent(
        &g_GlobalData.RingBuffer,
        &fileEvent,
        sizeof(EDR_FILE_EVENT)
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_DEBUG("Failed to queue file operation event: 0x%08X", status);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}
