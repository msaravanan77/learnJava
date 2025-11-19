#pragma once

#include <windows.h>
#include <string>
#include <memory>
#include "../../../common/include/event_structures.h"
#include "../../../common/include/ioctl_codes.h"

namespace YourEDR {

class DriverCommunicator {
public:
    DriverCommunicator();
    ~DriverCommunicator();

    // Connect to/disconnect from driver
    bool Connect();
    void Disconnect();
    bool IsConnected() const { return m_deviceHandle != INVALID_HANDLE_VALUE; }

    // Driver interaction
    bool GetVersion(YOUREDR_VERSION& version);
    bool GetEvent(void* buffer, DWORD bufferSize, DWORD& bytesReturned);
    bool SetConfig(const YOUREDR_CONFIG& config);
    bool GetStats(YOUREDR_STATS& stats);
    bool ClearEvents();

    // Error handling
    DWORD GetLastError() const { return m_lastError; }
    std::wstring GetLastErrorMessage() const;

private:
    HANDLE m_deviceHandle;
    DWORD m_lastError;

    bool SendIoctl(
        DWORD ioctlCode,
        void* inputBuffer,
        DWORD inputSize,
        void* outputBuffer,
        DWORD outputSize,
        DWORD& bytesReturned
    );
};

} // namespace YourEDR
