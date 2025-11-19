/*
 * YourEDR Service - Main Entry Point
 * Windows service that communicates with kernel driver
 * and logs events to JSON files
 *
 * Phase 1: File system event logging
 */

#include "../include/service.h"
#include <stdio.h>

// Global service instance
YourEDR::EDRService* g_serviceInstance = nullptr;
SERVICE_STATUS g_serviceStatus = {0};
SERVICE_STATUS_HANDLE g_serviceStatusHandle = nullptr;

//
// Service control handler
//

void WINAPI ServiceCtrlHandler(DWORD controlCode)
{
    switch (controlCode) {
    case SERVICE_CONTROL_STOP:
        g_serviceStatus.dwCurrentState = SERVICE_STOP_PENDING;
        SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

        if (g_serviceInstance) {
            g_serviceInstance->Stop();
        }
        break;

    case SERVICE_CONTROL_PAUSE:
        g_serviceStatus.dwCurrentState = SERVICE_PAUSED;
        SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

        if (g_serviceInstance) {
            g_serviceInstance->Pause();
        }
        break;

    case SERVICE_CONTROL_CONTINUE:
        g_serviceStatus.dwCurrentState = SERVICE_RUNNING;
        SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

        if (g_serviceInstance) {
            g_serviceInstance->Continue();
        }
        break;

    case SERVICE_CONTROL_INTERROGATE:
        break;

    default:
        break;
    }

    SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);
}

//
// Service main function
//

void WINAPI ServiceMain(DWORD argc, LPWSTR* argv)
{
    // Register service control handler
    g_serviceStatusHandle = RegisterServiceCtrlHandlerW(L"YourEDRService", ServiceCtrlHandler);
    if (g_serviceStatusHandle == nullptr) {
        return;
    }

    // Initialize service status
    g_serviceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    g_serviceStatus.dwCurrentState = SERVICE_START_PENDING;
    g_serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_PAUSE_CONTINUE;
    g_serviceStatus.dwWin32ExitCode = NO_ERROR;
    g_serviceStatus.dwServiceSpecificExitCode = 0;
    g_serviceStatus.dwCheckPoint = 0;
    g_serviceStatus.dwWaitHint = 0;

    SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

    // Create service instance
    g_serviceInstance = new YourEDR::EDRService();

    // Initialize service
    if (!g_serviceInstance->Initialize()) {
        g_serviceStatus.dwCurrentState = SERVICE_STOPPED;
        g_serviceStatus.dwWin32ExitCode = ERROR_SERVICE_SPECIFIC_ERROR;
        g_serviceStatus.dwServiceSpecificExitCode = 1;
        SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

        delete g_serviceInstance;
        g_serviceInstance = nullptr;
        return;
    }

    // Service is running
    g_serviceStatus.dwCurrentState = SERVICE_RUNNING;
    g_serviceStatus.dwWin32ExitCode = NO_ERROR;
    g_serviceStatus.dwCheckPoint = 0;
    g_serviceStatus.dwWaitHint = 0;
    SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

    // Run service
    g_serviceInstance->Run();

    // Service stopped
    g_serviceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

    delete g_serviceInstance;
    g_serviceInstance = nullptr;
}

//
// Install service
//

bool InstallService()
{
    SC_HANDLE scm = OpenSCManagerW(nullptr, nullptr, SC_MANAGER_CREATE_SERVICE);
    if (scm == nullptr) {
        wprintf(L"Failed to open Service Control Manager: %d\n", GetLastError());
        return false;
    }

    wchar_t path[MAX_PATH];
    GetModuleFileNameW(nullptr, path, MAX_PATH);

    SC_HANDLE service = CreateServiceW(
        scm,
        L"YourEDRService",
        L"YourEDR Service",
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_AUTO_START,
        SERVICE_ERROR_NORMAL,
        path,
        nullptr,
        nullptr,
        L"YourEDRFilter\0",  // Depends on driver
        nullptr,
        nullptr
    );

    if (service == nullptr) {
        DWORD error = GetLastError();
        if (error == ERROR_SERVICE_EXISTS) {
            wprintf(L"Service already exists\n");
        } else {
            wprintf(L"Failed to create service: %d\n", error);
        }
        CloseServiceHandle(scm);
        return false;
    }

    wprintf(L"Service installed successfully\n");

    // Set description
    SERVICE_DESCRIPTIONW desc;
    desc.lpDescription = const_cast<LPWSTR>(L"YourEDR file system monitoring service");
    ChangeServiceConfig2W(service, SERVICE_CONFIG_DESCRIPTION, &desc);

    CloseServiceHandle(service);
    CloseServiceHandle(scm);
    return true;
}

//
// Uninstall service
//

bool UninstallService()
{
    SC_HANDLE scm = OpenSCManagerW(nullptr, nullptr, SC_MANAGER_CONNECT);
    if (scm == nullptr) {
        wprintf(L"Failed to open Service Control Manager: %d\n", GetLastError());
        return false;
    }

    SC_HANDLE service = OpenServiceW(scm, L"YourEDRService", SERVICE_STOP | DELETE);
    if (service == nullptr) {
        wprintf(L"Failed to open service: %d\n", GetLastError());
        CloseServiceHandle(scm);
        return false;
    }

    // Stop service if running
    SERVICE_STATUS status;
    ControlService(service, SERVICE_CONTROL_STOP, &status);

    // Delete service
    if (!DeleteService(service)) {
        wprintf(L"Failed to delete service: %d\n", GetLastError());
        CloseServiceHandle(service);
        CloseServiceHandle(scm);
        return false;
    }

    wprintf(L"Service uninstalled successfully\n");

    CloseServiceHandle(service);
    CloseServiceHandle(scm);
    return true;
}

//
// Start service
//

bool StartServiceProcess()
{
    SC_HANDLE scm = OpenSCManagerW(nullptr, nullptr, SC_MANAGER_CONNECT);
    if (scm == nullptr) {
        wprintf(L"Failed to open Service Control Manager: %d\n", GetLastError());
        return false;
    }

    SC_HANDLE service = OpenServiceW(scm, L"YourEDRService", SERVICE_START);
    if (service == nullptr) {
        wprintf(L"Failed to open service: %d\n", GetLastError());
        CloseServiceHandle(scm);
        return false;
    }

    if (!StartServiceW(service, 0, nullptr)) {
        DWORD error = GetLastError();
        if (error == ERROR_SERVICE_ALREADY_RUNNING) {
            wprintf(L"Service is already running\n");
        } else {
            wprintf(L"Failed to start service: %d\n", error);
            CloseServiceHandle(service);
            CloseServiceHandle(scm);
            return false;
        }
    } else {
        wprintf(L"Service started successfully\n");
    }

    CloseServiceHandle(service);
    CloseServiceHandle(scm);
    return true;
}

//
// Stop service
//

bool StopServiceProcess()
{
    SC_HANDLE scm = OpenSCManagerW(nullptr, nullptr, SC_MANAGER_CONNECT);
    if (scm == nullptr) {
        wprintf(L"Failed to open Service Control Manager: %d\n", GetLastError());
        return false;
    }

    SC_HANDLE service = OpenServiceW(scm, L"YourEDRService", SERVICE_STOP);
    if (service == nullptr) {
        wprintf(L"Failed to open service: %d\n", GetLastError());
        CloseServiceHandle(scm);
        return false;
    }

    SERVICE_STATUS status;
    if (!ControlService(service, SERVICE_CONTROL_STOP, &status)) {
        DWORD error = GetLastError();
        if (error == ERROR_SERVICE_NOT_ACTIVE) {
            wprintf(L"Service is not running\n");
        } else {
            wprintf(L"Failed to stop service: %d\n", error);
            CloseServiceHandle(service);
            CloseServiceHandle(scm);
            return false;
        }
    } else {
        wprintf(L"Service stopped successfully\n");
    }

    CloseServiceHandle(service);
    CloseServiceHandle(scm);
    return true;
}

//
// Main entry point
//

int wmain(int argc, wchar_t* argv[])
{
    if (argc > 1) {
        if (_wcsicmp(argv[1], L"install") == 0) {
            return InstallService() ? 0 : 1;
        } else if (_wcsicmp(argv[1], L"uninstall") == 0) {
            return UninstallService() ? 0 : 1;
        } else if (_wcsicmp(argv[1], L"start") == 0) {
            return StartServiceProcess() ? 0 : 1;
        } else if (_wcsicmp(argv[1], L"stop") == 0) {
            return StopServiceProcess() ? 0 : 1;
        } else {
            wprintf(L"Usage: %s [install|uninstall|start|stop]\n", argv[0]);
            return 1;
        }
    }

    // Run as service
    SERVICE_TABLE_ENTRYW serviceTable[] = {
        { const_cast<LPWSTR>(L"YourEDRService"), ServiceMain },
        { nullptr, nullptr }
    };

    if (!StartServiceCtrlDispatcherW(serviceTable)) {
        DWORD error = GetLastError();
        if (error == ERROR_FAILED_SERVICE_CONTROLLER_CONNECT) {
            wprintf(L"Error: This program must be run as a Windows service\n");
            wprintf(L"Usage: %s [install|uninstall|start|stop]\n", argv[0]);
        }
        return 1;
    }

    return 0;
}
