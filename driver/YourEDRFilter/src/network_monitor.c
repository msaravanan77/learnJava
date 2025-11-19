/*
 * YourEDR - Network Monitor
 * Windows Filtering Platform (WFP) integration for network monitoring
 *
 * Phase 2: TCP/UDP connection monitoring with IPv4/IPv6 support
 */

#include "../include/driver.h"

// WFP headers
#include <fwpsk.h>
#include <fwpmk.h>

// Network protocol constants
#define IPPROTO_TCP 6
#define IPPROTO_UDP 17

// WFP layer GUIDs (Transport layer for connection tracking)
#define FWPM_LAYER_ALE_AUTH_CONNECT_V4  FWPM_LAYER_ALE_AUTH_CONNECT_V4
#define FWPM_LAYER_ALE_AUTH_CONNECT_V6  FWPM_LAYER_ALE_AUTH_CONNECT_V6
#define FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4 FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4
#define FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V6 FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V6

//
// Global WFP state
//

typedef struct _YOUREDR_WFP_DATA {
    HANDLE EngineHandle;               // WFP engine handle
    UINT32 CalloutIdConnectV4;         // Callout ID for IPv4 connect
    UINT32 CalloutIdConnectV6;         // Callout ID for IPv6 connect
    UINT32 CalloutIdAcceptV4;          // Callout ID for IPv4 accept
    UINT32 CalloutIdAcceptV6;          // Callout ID for IPv6 accept
    UINT32 FilterIdConnectV4;          // Filter ID for IPv4 connect
    UINT32 FilterIdConnectV6;          // Filter ID for IPv6 connect
    UINT32 FilterIdAcceptV4;           // Filter ID for IPv4 accept
    UINT32 FilterIdAcceptV6;           // Filter ID for IPv6 accept
    BOOLEAN Initialized;               // Initialization status
    ULONG ConnectionIdCounter;         // Unique connection ID counter
    KSPIN_LOCK ConnectionIdLock;       // Lock for connection ID
} YOUREDR_WFP_DATA, *PYOUREDR_WFP_DATA;

YOUREDR_WFP_DATA g_WfpData = {0};

//
// Forward declarations
//

NTSTATUS RegisterCallouts(_In_ PDEVICE_OBJECT DeviceObject);
NTSTATUS RegisterFilters(VOID);
VOID UnregisterCallouts(VOID);
VOID UnregisterFilters(VOID);

// Callout classify functions
VOID NTAPI ConnectV4ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
);

VOID NTAPI ConnectV6ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
);

VOID NTAPI AcceptV4ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
);

VOID NTAPI AcceptV6ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
);

// Callout notify function
NTSTATUS NTAPI NotifyFn(
    _In_ FWPS_CALLOUT_NOTIFY_TYPE notifyType,
    _In_ const GUID* filterKey,
    _Inout_ FWPS_FILTER3* filter
);

// Helper functions
ULONG GetNextConnectionId(VOID);
VOID CaptureNetworkEvent(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _In_ UCHAR protocol,
    _In_ UCHAR direction,
    _In_ UCHAR addressFamily
);

//
// Initialize network monitoring
//

NTSTATUS
InitializeNetworkMonitoring(
    _In_ PDEVICE_OBJECT DeviceObject
)
{
    NTSTATUS status;
    FWPM_SESSION0 session = {0};

    YOUREDR_LOG_INFO("Initializing network monitoring (WFP)");

    //
    // Initialize global state
    //

    RtlZeroMemory(&g_WfpData, sizeof(YOUREDR_WFP_DATA));
    KeInitializeSpinLock(&g_WfpData.ConnectionIdLock);
    g_WfpData.ConnectionIdCounter = 1;

    //
    // Open WFP engine session
    //

    session.flags = FWPM_SESSION_FLAG_DYNAMIC;  // Dynamic session (no reboot required)

    status = FwpmEngineOpen0(
        NULL,                    // Local computer
        RPC_C_AUTHN_WINNT,       // Authentication service
        NULL,                    // Authentication identity
        &session,                // Session info
        &g_WfpData.EngineHandle  // OUT: Engine handle
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmEngineOpen0 failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_INFO("WFP engine opened successfully");

    //
    // Register callouts
    //

    status = RegisterCallouts(DeviceObject);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("RegisterCallouts failed: 0x%08X", status);
        FwpmEngineClose0(g_WfpData.EngineHandle);
        g_WfpData.EngineHandle = NULL;
        return status;
    }

    //
    // Register filters
    //

    status = RegisterFilters();
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("RegisterFilters failed: 0x%08X", status);
        UnregisterCallouts();
        FwpmEngineClose0(g_WfpData.EngineHandle);
        g_WfpData.EngineHandle = NULL;
        return status;
    }

    g_WfpData.Initialized = TRUE;
    YOUREDR_LOG_INFO("Network monitoring initialized successfully");

    return STATUS_SUCCESS;
}

//
// Cleanup network monitoring
//

VOID
CleanupNetworkMonitoring(VOID)
{
    if (!g_WfpData.Initialized) {
        return;
    }

    YOUREDR_LOG_INFO("Cleaning up network monitoring");

    //
    // Unregister filters
    //

    UnregisterFilters();

    //
    // Unregister callouts
    //

    UnregisterCallouts();

    //
    // Close WFP engine
    //

    if (g_WfpData.EngineHandle != NULL) {
        FwpmEngineClose0(g_WfpData.EngineHandle);
        g_WfpData.EngineHandle = NULL;
    }

    g_WfpData.Initialized = FALSE;
    YOUREDR_LOG_INFO("Network monitoring cleanup complete");
}

//
// Register WFP callouts
//

NTSTATUS
RegisterCallouts(
    _In_ PDEVICE_OBJECT DeviceObject
)
{
    NTSTATUS status;
    FWPS_CALLOUT0 callout = {0};

    //
    // Register IPv4 connect callout
    //

    RtlZeroMemory(&callout, sizeof(FWPS_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_CONNECT_V4_GUID;
    callout.classifyFn = ConnectV4ClassifyFn;
    callout.notifyFn = NotifyFn;
    callout.flowDeleteFn = NULL;

    status = FwpsCalloutRegister0(
        DeviceObject,
        &callout,
        &g_WfpData.CalloutIdConnectV4
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpsCalloutRegister0 (ConnectV4) failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered ConnectV4 callout (ID: %u)", g_WfpData.CalloutIdConnectV4);

    //
    // Register IPv6 connect callout
    //

    RtlZeroMemory(&callout, sizeof(FWPS_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_CONNECT_V6_GUID;
    callout.classifyFn = ConnectV6ClassifyFn;
    callout.notifyFn = NotifyFn;
    callout.flowDeleteFn = NULL;

    status = FwpsCalloutRegister0(
        DeviceObject,
        &callout,
        &g_WfpData.CalloutIdConnectV6
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpsCalloutRegister0 (ConnectV6) failed: 0x%08X", status);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV4);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered ConnectV6 callout (ID: %u)", g_WfpData.CalloutIdConnectV6);

    //
    // Register IPv4 accept callout
    //

    RtlZeroMemory(&callout, sizeof(FWPS_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_ACCEPT_V4_GUID;
    callout.classifyFn = AcceptV4ClassifyFn;
    callout.notifyFn = NotifyFn;
    callout.flowDeleteFn = NULL;

    status = FwpsCalloutRegister0(
        DeviceObject,
        &callout,
        &g_WfpData.CalloutIdAcceptV4
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpsCalloutRegister0 (AcceptV4) failed: 0x%08X", status);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV4);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV6);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered AcceptV4 callout (ID: %u)", g_WfpData.CalloutIdAcceptV4);

    //
    // Register IPv6 accept callout
    //

    RtlZeroMemory(&callout, sizeof(FWPS_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_ACCEPT_V6_GUID;
    callout.classifyFn = AcceptV6ClassifyFn;
    callout.notifyFn = NotifyFn;
    callout.flowDeleteFn = NULL;

    status = FwpsCalloutRegister0(
        DeviceObject,
        &callout,
        &g_WfpData.CalloutIdAcceptV6
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpsCalloutRegister0 (AcceptV6) failed: 0x%08X", status);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV4);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV6);
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdAcceptV4);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered AcceptV6 callout (ID: %u)", g_WfpData.CalloutIdAcceptV6);

    return STATUS_SUCCESS;
}

//
// Unregister WFP callouts
//

VOID
UnregisterCallouts(VOID)
{
    if (g_WfpData.CalloutIdConnectV4 != 0) {
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV4);
        g_WfpData.CalloutIdConnectV4 = 0;
    }

    if (g_WfpData.CalloutIdConnectV6 != 0) {
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdConnectV6);
        g_WfpData.CalloutIdConnectV6 = 0;
    }

    if (g_WfpData.CalloutIdAcceptV4 != 0) {
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdAcceptV4);
        g_WfpData.CalloutIdAcceptV4 = 0;
    }

    if (g_WfpData.CalloutIdAcceptV6 != 0) {
        FwpsCalloutUnregisterById0(g_WfpData.CalloutIdAcceptV6);
        g_WfpData.CalloutIdAcceptV6 = 0;
    }

    YOUREDR_LOG_DEBUG("Unregistered all callouts");
}

//
// Register WFP filters
//

NTSTATUS
RegisterFilters(VOID)
{
    NTSTATUS status;
    FWPM_FILTER0 filter = {0};
    FWPM_CALLOUT0 callout = {0};

    //
    // Add callout to filter engine (ConnectV4)
    //

    RtlZeroMemory(&callout, sizeof(FWPM_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_CONNECT_V4_GUID;
    callout.displayData.name = L"YourEDR Connect V4 Callout";
    callout.displayData.description = L"Monitors outbound IPv4 TCP/UDP connections";
    callout.applicableLayer = FWPM_LAYER_ALE_AUTH_CONNECT_V4;

    status = FwpmCalloutAdd0(
        g_WfpData.EngineHandle,
        &callout,
        NULL,
        NULL
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmCalloutAdd0 (ConnectV4) failed: 0x%08X", status);
        return status;
    }

    //
    // Add filter (ConnectV4)
    //

    RtlZeroMemory(&filter, sizeof(FWPM_FILTER0));
    filter.displayData.name = L"YourEDR Connect V4 Filter";
    filter.displayData.description = L"Filter for outbound IPv4 connections";
    filter.layerKey = FWPM_LAYER_ALE_AUTH_CONNECT_V4;
    filter.action.type = FWP_ACTION_CALLOUT_INSPECTION;  // Inspection only, allow traffic
    filter.action.calloutKey = YOUREDR_CALLOUT_CONNECT_V4_GUID;
    filter.weight.type = FWP_EMPTY;  // Auto-weight
    filter.numFilterConditions = 0;  // No conditions, monitor all

    status = FwpmFilterAdd0(
        g_WfpData.EngineHandle,
        &filter,
        NULL,
        &g_WfpData.FilterIdConnectV4
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmFilterAdd0 (ConnectV4) failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered ConnectV4 filter (ID: %u)", g_WfpData.FilterIdConnectV4);

    //
    // Add callout and filter for ConnectV6
    //

    RtlZeroMemory(&callout, sizeof(FWPM_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_CONNECT_V6_GUID;
    callout.displayData.name = L"YourEDR Connect V6 Callout";
    callout.displayData.description = L"Monitors outbound IPv6 TCP/UDP connections";
    callout.applicableLayer = FWPM_LAYER_ALE_AUTH_CONNECT_V6;

    status = FwpmCalloutAdd0(g_WfpData.EngineHandle, &callout, NULL, NULL);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmCalloutAdd0 (ConnectV6) failed: 0x%08X", status);
        return status;
    }

    RtlZeroMemory(&filter, sizeof(FWPM_FILTER0));
    filter.displayData.name = L"YourEDR Connect V6 Filter";
    filter.layerKey = FWPM_LAYER_ALE_AUTH_CONNECT_V6;
    filter.action.type = FWP_ACTION_CALLOUT_INSPECTION;
    filter.action.calloutKey = YOUREDR_CALLOUT_CONNECT_V6_GUID;
    filter.weight.type = FWP_EMPTY;
    filter.numFilterConditions = 0;

    status = FwpmFilterAdd0(g_WfpData.EngineHandle, &filter, NULL, &g_WfpData.FilterIdConnectV6);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmFilterAdd0 (ConnectV6) failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered ConnectV6 filter (ID: %u)", g_WfpData.FilterIdConnectV6);

    //
    // Add callout and filter for AcceptV4
    //

    RtlZeroMemory(&callout, sizeof(FWPM_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_ACCEPT_V4_GUID;
    callout.displayData.name = L"YourEDR Accept V4 Callout";
    callout.displayData.description = L"Monitors inbound IPv4 TCP/UDP connections";
    callout.applicableLayer = FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4;

    status = FwpmCalloutAdd0(g_WfpData.EngineHandle, &callout, NULL, NULL);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmCalloutAdd0 (AcceptV4) failed: 0x%08X", status);
        return status;
    }

    RtlZeroMemory(&filter, sizeof(FWPM_FILTER0));
    filter.displayData.name = L"YourEDR Accept V4 Filter";
    filter.layerKey = FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4;
    filter.action.type = FWP_ACTION_CALLOUT_INSPECTION;
    filter.action.calloutKey = YOUREDR_CALLOUT_ACCEPT_V4_GUID;
    filter.weight.type = FWP_EMPTY;
    filter.numFilterConditions = 0;

    status = FwpmFilterAdd0(g_WfpData.EngineHandle, &filter, NULL, &g_WfpData.FilterIdAcceptV4);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmFilterAdd0 (AcceptV4) failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered AcceptV4 filter (ID: %u)", g_WfpData.FilterIdAcceptV4);

    //
    // Add callout and filter for AcceptV6
    //

    RtlZeroMemory(&callout, sizeof(FWPM_CALLOUT0));
    callout.calloutKey = YOUREDR_CALLOUT_ACCEPT_V6_GUID;
    callout.displayData.name = L"YourEDR Accept V6 Callout";
    callout.displayData.description = L"Monitors inbound IPv6 TCP/UDP connections";
    callout.applicableLayer = FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V6;

    status = FwpmCalloutAdd0(g_WfpData.EngineHandle, &callout, NULL, NULL);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmCalloutAdd0 (AcceptV6) failed: 0x%08X", status);
        return status;
    }

    RtlZeroMemory(&filter, sizeof(FWPM_FILTER0));
    filter.displayData.name = L"YourEDR Accept V6 Filter";
    filter.layerKey = FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V6;
    filter.action.type = FWP_ACTION_CALLOUT_INSPECTION;
    filter.action.calloutKey = YOUREDR_CALLOUT_ACCEPT_V6_GUID;
    filter.weight.type = FWP_EMPTY;
    filter.numFilterConditions = 0;

    status = FwpmFilterAdd0(g_WfpData.EngineHandle, &filter, NULL, &g_WfpData.FilterIdAcceptV6);
    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_ERROR("FwpmFilterAdd0 (AcceptV6) failed: 0x%08X", status);
        return status;
    }

    YOUREDR_LOG_DEBUG("Registered AcceptV6 filter (ID: %u)", g_WfpData.FilterIdAcceptV6);

    return STATUS_SUCCESS;
}

//
// Unregister WFP filters
//

VOID
UnregisterFilters(VOID)
{
    if (g_WfpData.EngineHandle == NULL) {
        return;
    }

    if (g_WfpData.FilterIdConnectV4 != 0) {
        FwpmFilterDeleteById0(g_WfpData.EngineHandle, g_WfpData.FilterIdConnectV4);
        g_WfpData.FilterIdConnectV4 = 0;
    }

    if (g_WfpData.FilterIdConnectV6 != 0) {
        FwpmFilterDeleteById0(g_WfpData.EngineHandle, g_WfpData.FilterIdConnectV6);
        g_WfpData.FilterIdConnectV6 = 0;
    }

    if (g_WfpData.FilterIdAcceptV4 != 0) {
        FwpmFilterDeleteById0(g_WfpData.EngineHandle, g_WfpData.FilterIdAcceptV4);
        g_WfpData.FilterIdAcceptV4 = 0;
    }

    if (g_WfpData.FilterIdAcceptV6 != 0) {
        FwpmFilterDeleteById0(g_WfpData.EngineHandle, g_WfpData.FilterIdAcceptV6);
        g_WfpData.FilterIdAcceptV6 = 0;
    }

    YOUREDR_LOG_DEBUG("Unregistered all filters");
}

//
// IPv4 connect callout classify function
//

VOID NTAPI
ConnectV4ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
)
{
    UNREFERENCED_PARAMETER(layerData);
    UNREFERENCED_PARAMETER(classifyContext);
    UNREFERENCED_PARAMETER(filter);
    UNREFERENCED_PARAMETER(flowContext);

    //
    // Check if network monitoring is enabled
    //

    if (!g_GlobalData.Config.EnableNetworkMonitoring) {
        classifyOut->actionType = FWP_ACTION_PERMIT;
        return;
    }

    //
    // Capture network event
    //

    CaptureNetworkEvent(
        inFixedValues,
        inMetaValues,
        IPPROTO_TCP,  // Assume TCP for now (can be determined from inFixedValues)
        0,            // Outbound
        AF_INET       // IPv4
    );

    //
    // Permit the connection (monitoring only)
    //

    classifyOut->actionType = FWP_ACTION_PERMIT;
}

//
// IPv6 connect callout classify function
//

VOID NTAPI
ConnectV6ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
)
{
    UNREFERENCED_PARAMETER(layerData);
    UNREFERENCED_PARAMETER(classifyContext);
    UNREFERENCED_PARAMETER(filter);
    UNREFERENCED_PARAMETER(flowContext);

    if (!g_GlobalData.Config.EnableNetworkMonitoring) {
        classifyOut->actionType = FWP_ACTION_PERMIT;
        return;
    }

    CaptureNetworkEvent(
        inFixedValues,
        inMetaValues,
        IPPROTO_TCP,
        0,            // Outbound
        AF_INET6      // IPv6
    );

    classifyOut->actionType = FWP_ACTION_PERMIT;
}

//
// IPv4 accept callout classify function
//

VOID NTAPI
AcceptV4ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
)
{
    UNREFERENCED_PARAMETER(layerData);
    UNREFERENCED_PARAMETER(classifyContext);
    UNREFERENCED_PARAMETER(filter);
    UNREFERENCED_PARAMETER(flowContext);

    if (!g_GlobalData.Config.EnableNetworkMonitoring) {
        classifyOut->actionType = FWP_ACTION_PERMIT;
        return;
    }

    CaptureNetworkEvent(
        inFixedValues,
        inMetaValues,
        IPPROTO_TCP,
        1,            // Inbound
        AF_INET       // IPv4
    );

    classifyOut->actionType = FWP_ACTION_PERMIT;
}

//
// IPv6 accept callout classify function
//

VOID NTAPI
AcceptV6ClassifyFn(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _Inout_opt_ void* layerData,
    _In_opt_ const void* classifyContext,
    _In_ const FWPS_FILTER3* filter,
    _In_ UINT64 flowContext,
    _Inout_ FWPS_CLASSIFY_OUT0* classifyOut
)
{
    UNREFERENCED_PARAMETER(layerData);
    UNREFERENCED_PARAMETER(classifyContext);
    UNREFERENCED_PARAMETER(filter);
    UNREFERENCED_PARAMETER(flowContext);

    if (!g_GlobalData.Config.EnableNetworkMonitoring) {
        classifyOut->actionType = FWP_ACTION_PERMIT;
        return;
    }

    CaptureNetworkEvent(
        inFixedValues,
        inMetaValues,
        IPPROTO_TCP,
        1,            // Inbound
        AF_INET6      // IPv6
    );

    classifyOut->actionType = FWP_ACTION_PERMIT;
}

//
// Callout notify function
//

NTSTATUS NTAPI
NotifyFn(
    _In_ FWPS_CALLOUT_NOTIFY_TYPE notifyType,
    _In_ const GUID* filterKey,
    _Inout_ FWPS_FILTER3* filter
)
{
    UNREFERENCED_PARAMETER(filterKey);
    UNREFERENCED_PARAMETER(filter);

    switch (notifyType) {
    case FWPS_CALLOUT_NOTIFY_ADD_FILTER:
        YOUREDR_LOG_DEBUG("WFP: Filter added");
        break;

    case FWPS_CALLOUT_NOTIFY_DELETE_FILTER:
        YOUREDR_LOG_DEBUG("WFP: Filter deleted");
        break;

    default:
        break;
    }

    return STATUS_SUCCESS;
}

//
// Capture network event and queue to ring buffer
//

VOID
CaptureNetworkEvent(
    _In_ const FWPS_INCOMING_VALUES0* inFixedValues,
    _In_ const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    _In_ UCHAR protocol,
    _In_ UCHAR direction,
    _In_ UCHAR addressFamily
)
{
    NTSTATUS status;
    EDR_NETWORK_EVENT networkEvent;
    UINT32 localAddr32, remoteAddr32;
    UINT16 localPort, remotePort;

    //
    // Initialize network event structure
    //

    RtlZeroMemory(&networkEvent, sizeof(EDR_NETWORK_EVENT));

    //
    // Fill common header
    //

    networkEvent.Header.EventSize = sizeof(EDR_NETWORK_EVENT);
    networkEvent.Header.EventType = (direction == 0) ? EventTypeNetworkConnect : EventTypeNetworkAccept;
    GetCurrentTimestamp(&networkEvent.Header.Timestamp);
    networkEvent.Header.ProcessId = HandleToUlong(PsGetCurrentProcessId());
    networkEvent.Header.ThreadId = HandleToUlong(PsGetCurrentThreadId());
    networkEvent.Header.SessionId = 0;  // TODO: Get session ID
    networkEvent.Header.IntegrityLevel = 0;  // TODO: Get integrity level
    networkEvent.Header.SequenceNumber = GetNextSequenceNumber();

    //
    // Fill network-specific fields
    //

    networkEvent.Protocol = protocol;
    networkEvent.Direction = direction;
    networkEvent.AddressFamily = addressFamily;
    networkEvent.ConnectionId = GetNextConnectionId();

    //
    // Extract IP addresses and ports from inFixedValues
    // The exact field indices depend on the WFP layer
    //

    if (addressFamily == AF_INET) {
        // IPv4 addresses
        localAddr32 = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
        remoteAddr32 = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
        localPort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_PORT].value.uint16;
        remotePort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_PORT].value.uint16;

        // Convert IPv4 to IPv6-mapped format
        RtlZeroMemory(networkEvent.LocalAddress, 16);
        RtlZeroMemory(networkEvent.RemoteAddress, 16);

        // IPv4-mapped IPv6 format: ::ffff:x.x.x.x
        networkEvent.LocalAddress[10] = 0xFF;
        networkEvent.LocalAddress[11] = 0xFF;
        RtlCopyMemory(&networkEvent.LocalAddress[12], &localAddr32, 4);

        networkEvent.RemoteAddress[10] = 0xFF;
        networkEvent.RemoteAddress[11] = 0xFF;
        RtlCopyMemory(&networkEvent.RemoteAddress[12], &remoteAddr32, 4);

        networkEvent.LocalPort = localPort;
        networkEvent.RemotePort = remotePort;

    } else {
        // IPv6 addresses
        FWP_BYTE_ARRAY16* localAddrV6 = (FWP_BYTE_ARRAY16*)inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V6_IP_LOCAL_ADDRESS].value.byteArray16;
        FWP_BYTE_ARRAY16* remoteAddrV6 = (FWP_BYTE_ARRAY16*)inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V6_IP_REMOTE_ADDRESS].value.byteArray16;

        RtlCopyMemory(networkEvent.LocalAddress, localAddrV6->byteArray16, 16);
        RtlCopyMemory(networkEvent.RemoteAddress, remoteAddrV6->byteArray16, 16);

        networkEvent.LocalPort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V6_IP_LOCAL_PORT].value.uint16;
        networkEvent.RemotePort = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V6_IP_REMOTE_PORT].value.uint16;
    }

    //
    // Get protocol from metadata if available
    //

    if (FWPS_IS_METADATA_FIELD_PRESENT(inMetaValues, FWPS_METADATA_FIELD_TRANSPORT_HEADER_SIZE)) {
        // Can determine TCP vs UDP from protocol field
        // For now, we assume TCP (most common)
    }

    //
    // Get process name if available
    //

    if (FWPS_IS_METADATA_FIELD_PRESENT(inMetaValues, FWPS_METADATA_FIELD_PROCESS_PATH)) {
        UNICODE_STRING* processPath = (UNICODE_STRING*)inMetaValues->processPath;
        if (processPath && processPath->Buffer && processPath->Length > 0) {
            // Extract just the filename (not full path)
            WCHAR* lastSlash = wcsrchr(processPath->Buffer, L'\\');
            if (lastSlash) {
                ULONG nameLen = min((processPath->Length - (ULONG)((lastSlash - processPath->Buffer + 1) * sizeof(WCHAR))) / sizeof(WCHAR), 63);
                RtlCopyMemory(networkEvent.ProcessName, lastSlash + 1, nameLen * sizeof(WCHAR));
                networkEvent.ProcessName[nameLen] = L'\0';
            }
        }
    }

    //
    // Bytes sent/received are not available at connect/accept time
    // These would be tracked via flow context in a more advanced implementation
    //

    networkEvent.BytesSent = 0;
    networkEvent.BytesReceived = 0;

    //
    // Queue event to ring buffer
    //

    status = QueueEvent(
        &g_GlobalData.RingBuffer,
        &networkEvent,
        sizeof(EDR_NETWORK_EVENT)
    );

    if (!NT_SUCCESS(status)) {
        YOUREDR_LOG_DEBUG("Failed to queue network event: 0x%08X", status);
    }
}

//
// Get next unique connection ID
//

ULONG
GetNextConnectionId(VOID)
{
    KIRQL oldIrql;
    ULONG connectionId;

    KeAcquireSpinLock(&g_WfpData.ConnectionIdLock, &oldIrql);
    connectionId = g_WfpData.ConnectionIdCounter++;
    KeReleaseSpinLock(&g_WfpData.ConnectionIdLock, oldIrql);

    return connectionId;
}
