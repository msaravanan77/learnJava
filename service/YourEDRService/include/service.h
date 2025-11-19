#pragma once

#include <windows.h>
#include <memory>
#include "driver_communicator.h"
#include "json_logger.h"

namespace YourEDR {

class EDRService {
public:
    EDRService();
    ~EDRService();

    // Service lifecycle
    bool Initialize();
    void Run();
    void Shutdown();

    // Service control
    void Stop();
    void Pause();
    void Continue();

    // Status
    bool IsRunning() const { return m_isRunning; }
    bool IsPaused() const { return m_isPaused; }

private:
    std::unique_ptr<DriverCommunicator> m_driverComm;
    std::unique_ptr<JsonLogger> m_logger;

    bool m_isRunning;
    bool m_isPaused;
    bool m_shouldStop;
    HANDLE m_stopEvent;
    HANDLE m_workerThread;

    // Worker thread
    static DWORD WINAPI WorkerThreadProc(LPVOID parameter);
    void WorkerThreadMain();

    // Configuration
    bool LoadConfiguration();
    std::wstring GetInstallDirectory();
    std::wstring GetLogDirectory();
};

} // namespace YourEDR

// Windows Service globals and functions
extern YourEDR::EDRService* g_serviceInstance;

void WINAPI ServiceMain(DWORD argc, LPWSTR* argv);
void WINAPI ServiceCtrlHandler(DWORD controlCode);
bool InstallService();
bool UninstallService();
bool StartServiceProcess();
bool StopServiceProcess();
