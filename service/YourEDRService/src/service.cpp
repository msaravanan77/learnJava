#include "../include/service.h"
#include <shlwapi.h>
#include <strsafe.h>

#pragma comment(lib, "shlwapi.lib")

namespace YourEDR {

EDRService::EDRService()
    : m_isRunning(false)
    , m_isPaused(false)
    , m_shouldStop(false)
    , m_stopEvent(nullptr)
    , m_workerThread(nullptr)
{
    m_driverComm = std::make_unique<DriverCommunicator>();
    m_logger = std::make_unique<JsonLogger>();
}

EDRService::~EDRService()
{
    Shutdown();
}

bool EDRService::Initialize()
{
    // Create stop event
    m_stopEvent = CreateEvent(nullptr, TRUE, FALSE, nullptr);
    if (m_stopEvent == nullptr) {
        return false;
    }

    // Connect to driver
    if (!m_driverComm->Connect()) {
        OutputDebugStringW(L"Failed to connect to driver\n");
        return false;
    }

    // Get driver version
    YOUREDR_VERSION version;
    if (m_driverComm->GetVersion(version)) {
        wchar_t buffer[256];
        StringCchPrintfW(buffer, 256, L"Connected to driver v%d.%d.%d.%d\n",
            version.MajorVersion, version.MinorVersion, version.PatchVersion, version.BuildNumber);
        OutputDebugStringW(buffer);
    }

    // Initialize logger
    std::wstring logDir = GetLogDirectory();
    if (!m_logger->Initialize(logDir, 100)) {
        OutputDebugStringW(L"Failed to initialize logger\n");
        return false;
    }

    // Load configuration
    LoadConfiguration();

    return true;
}

void EDRService::Run()
{
    m_isRunning = true;
    m_shouldStop = false;

    // Create worker thread
    m_workerThread = CreateThread(
        nullptr,
        0,
        WorkerThreadProc,
        this,
        0,
        nullptr
    );

    if (m_workerThread == nullptr) {
        m_isRunning = false;
        return;
    }

    // Wait for stop signal
    WaitForSingleObject(m_stopEvent, INFINITE);
}

void EDRService::Shutdown()
{
    m_shouldStop = true;

    // Signal stop event
    if (m_stopEvent != nullptr) {
        SetEvent(m_stopEvent);
    }

    // Wait for worker thread
    if (m_workerThread != nullptr) {
        WaitForSingleObject(m_workerThread, 5000);
        CloseHandle(m_workerThread);
        m_workerThread = nullptr;
    }

    // Cleanup
    m_logger->Shutdown();
    m_driverComm->Disconnect();

    if (m_stopEvent != nullptr) {
        CloseHandle(m_stopEvent);
        m_stopEvent = nullptr;
    }

    m_isRunning = false;
}

void EDRService::Stop()
{
    m_shouldStop = true;
    if (m_stopEvent != nullptr) {
        SetEvent(m_stopEvent);
    }
}

void EDRService::Pause()
{
    m_isPaused = true;
}

void EDRService::Continue()
{
    m_isPaused = false;
}

DWORD WINAPI EDRService::WorkerThreadProc(LPVOID parameter)
{
    EDRService* service = static_cast<EDRService*>(parameter);
    service->WorkerThreadMain();
    return 0;
}

void EDRService::WorkerThreadMain()
{
    OutputDebugStringW(L"YourEDR worker thread started\n");

    const DWORD pollIntervalMs = 100;
    BYTE eventBuffer[4096]; // Buffer for receiving events

    while (!m_shouldStop) {
        // Check if paused
        if (m_isPaused) {
            Sleep(1000);
            continue;
        }

        // Poll driver for events
        DWORD bytesReturned = 0;
        if (m_driverComm->GetEvent(eventBuffer, sizeof(eventBuffer), bytesReturned)) {
            if (bytesReturned > 0) {
                // Log event to JSON file
                m_logger->LogEvent(eventBuffer, bytesReturned);

                // Continue polling immediately if we got an event
                continue;
            }
        }

        // No events available, sleep briefly
        Sleep(pollIntervalMs);
    }

    OutputDebugStringW(L"YourEDR worker thread stopped\n");
}

bool EDRService::LoadConfiguration()
{
    // TODO: Load configuration from file
    // For Phase 1, use defaults

    YOUREDR_CONFIG config = {0};
    config.EnableFileMonitoring = TRUE;
    config.EnableProcessMonitoring = FALSE;
    config.EnableNetworkMonitoring = FALSE;
    config.MaxEventsPerSecond = 10000;
    config.ExcludedPathCount = 0;

    return m_driverComm->SetConfig(config);
}

std::wstring EDRService::GetInstallDirectory()
{
    wchar_t path[MAX_PATH];
    GetModuleFileNameW(nullptr, path, MAX_PATH);
    PathRemoveFileSpecW(path);
    return path;
}

std::wstring EDRService::GetLogDirectory()
{
    // Use C:\ProgramData\YourEDR\Logs
    wchar_t path[MAX_PATH];
    SHGetFolderPathW(nullptr, CSIDL_COMMON_APPDATA, nullptr, 0, path);
    PathAppendW(path, L"YourEDR\\Logs");
    return path;
}

} // namespace YourEDR
