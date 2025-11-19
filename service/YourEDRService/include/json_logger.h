#pragma once

#include <windows.h>
#include <string>
#include <fstream>
#include <memory>
#include <mutex>
#include "../../../common/include/event_structures.h"

namespace YourEDR {

class JsonLogger {
public:
    JsonLogger();
    ~JsonLogger();

    // Initialize logger
    bool Initialize(const std::wstring& logDirectory, size_t maxFileSizeMB = 100);
    void Shutdown();

    // Log events
    bool LogEvent(const void* eventData, size_t eventSize);

    // Statistics
    uint64_t GetTotalEventsLogged() const { return m_totalEventsLogged; }
    uint64_t GetTotalBytesWritten() const { return m_totalBytesWritten; }

private:
    std::wstring m_logDirectory;
    std::wstring m_currentLogFile;
    std::ofstream m_logStream;
    size_t m_maxFileSize;
    size_t m_currentFileSize;
    uint64_t m_totalEventsLogged;
    uint64_t m_totalBytesWritten;
    mutable std::mutex m_mutex;

    // Internal helpers
    bool OpenNewLogFile();
    void CloseCurrentLogFile();
    std::string ConvertEventToJson(const void* eventData, size_t eventSize);
    std::string ConvertFileEventToJson(const EDR_FILE_EVENT* fileEvent);
    std::string ConvertProcessEventToJson(const EDR_PROCESS_CREATE_EVENT* processEvent);
    std::wstring GetCurrentTimestamp();
    std::string WideToUtf8(const std::wstring& wstr);
    std::string FormatTimestamp(const LARGE_INTEGER& timestamp);
};

} // namespace YourEDR
