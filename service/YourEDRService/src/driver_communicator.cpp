#include "../include/driver_communicator.h"
#include <sstream>
#include <iomanip>

namespace YourEDR {

DriverCommunicator::DriverCommunicator()
    : m_deviceHandle(INVALID_HANDLE_VALUE)
    , m_lastError(ERROR_SUCCESS)
{
}

DriverCommunicator::~DriverCommunicator()
{
    Disconnect();
}

bool DriverCommunicator::Connect()
{
    if (m_deviceHandle != INVALID_HANDLE_VALUE) {
        return true; // Already connected
    }

    // Open handle to driver device
    m_deviceHandle = CreateFileW(
        YOUREDR_USER_DEVICE_NAME,
        GENERIC_READ | GENERIC_WRITE,
        0,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (m_deviceHandle == INVALID_HANDLE_VALUE) {
        m_lastError = ::GetLastError();
        return false;
    }

    m_lastError = ERROR_SUCCESS;
    return true;
}

void DriverCommunicator::Disconnect()
{
    if (m_deviceHandle != INVALID_HANDLE_VALUE) {
        CloseHandle(m_deviceHandle);
        m_deviceHandle = INVALID_HANDLE_VALUE;
    }
}

bool DriverCommunicator::GetVersion(YOUREDR_VERSION& version)
{
    DWORD bytesReturned = 0;

    return SendIoctl(
        IOCTL_YOUREDR_GET_VERSION,
        nullptr,
        0,
        &version,
        sizeof(YOUREDR_VERSION),
        bytesReturned
    );
}

bool DriverCommunicator::GetEvent(void* buffer, DWORD bufferSize, DWORD& bytesReturned)
{
    return SendIoctl(
        IOCTL_YOUREDR_GET_EVENT,
        nullptr,
        0,
        buffer,
        bufferSize,
        bytesReturned
    );
}

bool DriverCommunicator::SetConfig(const YOUREDR_CONFIG& config)
{
    DWORD bytesReturned = 0;

    return SendIoctl(
        IOCTL_YOUREDR_SET_CONFIG,
        (void*)&config,
        sizeof(YOUREDR_CONFIG),
        nullptr,
        0,
        bytesReturned
    );
}

bool DriverCommunicator::GetStats(YOUREDR_STATS& stats)
{
    DWORD bytesReturned = 0;

    return SendIoctl(
        IOCTL_YOUREDR_GET_STATS,
        nullptr,
        0,
        &stats,
        sizeof(YOUREDR_STATS),
        bytesReturned
    );
}

bool DriverCommunicator::ClearEvents()
{
    DWORD bytesReturned = 0;

    return SendIoctl(
        IOCTL_YOUREDR_CLEAR_EVENTS,
        nullptr,
        0,
        nullptr,
        0,
        bytesReturned
    );
}

std::wstring DriverCommunicator::GetLastErrorMessage() const
{
    if (m_lastError == ERROR_SUCCESS) {
        return L"Success";
    }

    LPWSTR buffer = nullptr;
    FormatMessageW(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        m_lastError,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPWSTR)&buffer,
        0,
        nullptr
    );

    std::wstring message = buffer ? buffer : L"Unknown error";
    if (buffer) {
        LocalFree(buffer);
    }

    return message;
}

bool DriverCommunicator::SendIoctl(
    DWORD ioctlCode,
    void* inputBuffer,
    DWORD inputSize,
    void* outputBuffer,
    DWORD outputSize,
    DWORD& bytesReturned)
{
    if (m_deviceHandle == INVALID_HANDLE_VALUE) {
        m_lastError = ERROR_INVALID_HANDLE;
        return false;
    }

    BOOL result = DeviceIoControl(
        m_deviceHandle,
        ioctlCode,
        inputBuffer,
        inputSize,
        outputBuffer,
        outputSize,
        &bytesReturned,
        nullptr
    );

    if (!result) {
        m_lastError = ::GetLastError();
        return false;
    }

    m_lastError = ERROR_SUCCESS;
    return true;
}

} // namespace YourEDR
