#include "../include/json_logger.h"
#include <sstream>
#include <iomanip>
#include <chrono>
#include <codecvt>
#include <locale>

namespace YourEDR {

JsonLogger::JsonLogger()
    : m_maxFileSize(100 * 1024 * 1024) // 100 MB default
    , m_currentFileSize(0)
    , m_totalEventsLogged(0)
    , m_totalBytesWritten(0)
{
}

JsonLogger::~JsonLogger()
{
    Shutdown();
}

bool JsonLogger::Initialize(const std::wstring& logDirectory, size_t maxFileSizeMB)
{
    std::lock_guard<std::mutex> lock(m_mutex);

    m_logDirectory = logDirectory;
    m_maxFileSize = maxFileSizeMB * 1024 * 1024;

    // Create log directory if it doesn't exist
    CreateDirectoryW(m_logDirectory.c_str(), nullptr);

    // Open initial log file
    return OpenNewLogFile();
}

void JsonLogger::Shutdown()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    CloseCurrentLogFile();
}

bool JsonLogger::LogEvent(const void* eventData, size_t eventSize)
{
    if (!eventData || eventSize < sizeof(EDR_EVENT_HEADER)) {
        return false;
    }

    std::lock_guard<std::mutex> lock(m_mutex);

    // Check if we need to rotate log file
    if (m_currentFileSize >= m_maxFileSize) {
        CloseCurrentLogFile();
        if (!OpenNewLogFile()) {
            return false;
        }
    }

    // Convert event to JSON
    std::string jsonLine = ConvertEventToJson(eventData, eventSize);
    if (jsonLine.empty()) {
        return false;
    }

    // Write JSON line to file
    m_logStream << jsonLine << "\n";
    m_logStream.flush();

    // Update statistics
    m_currentFileSize += jsonLine.length() + 1;
    m_totalBytesWritten += jsonLine.length() + 1;
    m_totalEventsLogged++;

    return true;
}

bool JsonLogger::OpenNewLogFile()
{
    // Generate log file name with timestamp
    std::wstring timestamp = GetCurrentTimestamp();
    m_currentLogFile = m_logDirectory + L"\\events_" + timestamp + L".jsonl";

    // Open file in append mode
    m_logStream.open(m_currentLogFile, std::ios::out | std::ios::app);
    if (!m_logStream.is_open()) {
        return false;
    }

    m_currentFileSize = 0;
    return true;
}

void JsonLogger::CloseCurrentLogFile()
{
    if (m_logStream.is_open()) {
        m_logStream.close();
    }
}

std::string JsonLogger::ConvertEventToJson(const void* eventData, size_t eventSize)
{
    const EDR_EVENT_HEADER* header = static_cast<const EDR_EVENT_HEADER*>(eventData);

    // Validate event type
    if (header->EventType <= EventTypeNone || header->EventType >= EventTypeMax) {
        return "";
    }

    // Route to specific event converter
    switch (header->EventType) {
    case EventTypeFileCreate:
    case EventTypeFileWrite:
    case EventTypeFileDelete:
    case EventTypeFileRename:
        return ConvertFileEventToJson(static_cast<const EDR_FILE_EVENT*>(eventData));

    case EventTypeProcessCreate:
    case EventTypeProcessExit:
        return ConvertProcessEventToJson(static_cast<const EDR_PROCESS_CREATE_EVENT*>(eventData));

    case EventTypeNetworkConnect:
    case EventTypeNetworkAccept:
    case EventTypeNetworkSend:
    case EventTypeNetworkReceive:
        return ConvertNetworkEventToJson(static_cast<const EDR_NETWORK_EVENT*>(eventData));

    default:
        return "";
    }
}

std::string JsonLogger::ConvertFileEventToJson(const EDR_FILE_EVENT* fileEvent)
{
    std::ostringstream json;

    json << "{";
    json << "\"eventType\":\"";

    switch (fileEvent->Header.EventType) {
    case EventTypeFileCreate: json << "FileCreate"; break;
    case EventTypeFileWrite: json << "FileWrite"; break;
    case EventTypeFileDelete: json << "FileDelete"; break;
    case EventTypeFileRename: json << "FileRename"; break;
    default: json << "Unknown"; break;
    }

    json << "\",";
    json << "\"timestamp\":\"" << FormatTimestamp(fileEvent->Header.Timestamp) << "\",";
    json << "\"sequenceNumber\":" << fileEvent->Header.SequenceNumber << ",";
    json << "\"processId\":" << fileEvent->Header.ProcessId << ",";
    json << "\"threadId\":" << fileEvent->Header.ThreadId << ",";
    json << "\"sessionId\":" << fileEvent->Header.SessionId << ",";
    json << "\"filePath\":\"" << WideToUtf8(fileEvent->FilePath) << "\",";
    json << "\"desiredAccess\":\"0x" << std::hex << fileEvent->DesiredAccess << std::dec << "\",";
    json << "\"fileSize\":" << fileEvent->FileSize;
    json << "}";

    return json.str();
}

std::string JsonLogger::ConvertProcessEventToJson(const EDR_PROCESS_CREATE_EVENT* processEvent)
{
    std::ostringstream json;

    json << "{";
    json << "\"eventType\":\"ProcessCreate\",";
    json << "\"timestamp\":\"" << FormatTimestamp(processEvent->Header.Timestamp) << "\",";
    json << "\"sequenceNumber\":" << processEvent->Header.SequenceNumber << ",";
    json << "\"processId\":" << processEvent->Header.ProcessId << ",";
    json << "\"parentProcessId\":" << processEvent->ParentProcessId << ",";
    json << "\"imagePath\":\"" << WideToUtf8(processEvent->ImagePath) << "\",";
    json << "\"commandLine\":\"" << WideToUtf8(processEvent->CommandLine) << "\"";
    json << "}";

    return json.str();
}

std::string JsonLogger::ConvertNetworkEventToJson(const EDR_NETWORK_EVENT* networkEvent)
{
    std::ostringstream json;

    json << "{";
    json << "\"eventType\":\"";

    switch (networkEvent->Header.EventType) {
    case EventTypeNetworkConnect: json << "NetworkConnect"; break;
    case EventTypeNetworkAccept: json << "NetworkAccept"; break;
    case EventTypeNetworkSend: json << "NetworkSend"; break;
    case EventTypeNetworkReceive: json << "NetworkReceive"; break;
    default: json << "Unknown"; break;
    }

    json << "\",";
    json << "\"timestamp\":\"" << FormatTimestamp(networkEvent->Header.Timestamp) << "\",";
    json << "\"sequenceNumber\":" << networkEvent->Header.SequenceNumber << ",";
    json << "\"processId\":" << networkEvent->Header.ProcessId << ",";
    json << "\"threadId\":" << networkEvent->Header.ThreadId << ",";
    json << "\"sessionId\":" << networkEvent->Header.SessionId << ",";
    json << "\"connectionId\":" << networkEvent->ConnectionId << ",";

    // Protocol
    json << "\"protocol\":\"";
    switch (networkEvent->Protocol) {
    case 6: json << "TCP"; break;
    case 17: json << "UDP"; break;
    default: json << "Unknown(" << (int)networkEvent->Protocol << ")"; break;
    }
    json << "\",";

    // Direction
    json << "\"direction\":\"" << (networkEvent->Direction == 0 ? "Outbound" : "Inbound") << "\",";

    // Address family
    json << "\"addressFamily\":\"";
    switch (networkEvent->AddressFamily) {
    case 2: json << "IPv4"; break;
    case 23: json << "IPv6"; break;
    default: json << "Unknown"; break;
    }
    json << "\",";

    // Local address and port
    json << "\"localAddress\":\"" << FormatIPAddress(networkEvent->LocalAddress, networkEvent->AddressFamily) << "\",";
    json << "\"localPort\":" << networkEvent->LocalPort << ",";

    // Remote address and port
    json << "\"remoteAddress\":\"" << FormatIPAddress(networkEvent->RemoteAddress, networkEvent->AddressFamily) << "\",";
    json << "\"remotePort\":" << networkEvent->RemotePort << ",";

    // Data transfer stats
    json << "\"bytesSent\":" << networkEvent->BytesSent << ",";
    json << "\"bytesReceived\":" << networkEvent->BytesReceived;

    // Process name (if available)
    if (networkEvent->ProcessName[0] != L'\0') {
        json << ",\"processName\":\"" << WideToUtf8(networkEvent->ProcessName) << "\"";
    }

    json << "}";

    return json.str();
}

std::wstring JsonLogger::GetCurrentTimestamp()
{
    SYSTEMTIME st;
    GetLocalTime(&st);

    wchar_t buffer[64];
    swprintf_s(buffer, 64, L"%04d%02d%02d_%02d%02d%02d",
        st.wYear, st.wMonth, st.wDay,
        st.wHour, st.wMinute, st.wSecond);

    return buffer;
}

std::string JsonLogger::WideToUtf8(const std::wstring& wstr)
{
    if (wstr.empty()) return "";

    int size = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), -1, nullptr, 0, nullptr, nullptr);
    if (size <= 0) return "";

    std::string result(size - 1, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), -1, &result[0], size, nullptr, nullptr);

    // Escape backslashes and quotes for JSON
    std::string escaped;
    for (char c : result) {
        if (c == '\\' || c == '\"') {
            escaped += '\\';
        }
        escaped += c;
    }

    return escaped;
}

std::string JsonLogger::FormatTimestamp(const LARGE_INTEGER& timestamp)
{
    // Convert Windows FILETIME (100ns intervals since 1601) to ISO 8601
    FILETIME ft;
    ft.dwLowDateTime = timestamp.LowPart;
    ft.dwHighDateTime = timestamp.HighPart;

    SYSTEMTIME st;
    FileTimeToSystemTime(&ft, &st);

    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ",
        st.wYear, st.wMonth, st.wDay,
        st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);

    return buffer;
}

std::string JsonLogger::FormatIPAddress(const UCHAR* address, UCHAR addressFamily)
{
    char buffer[64];

    if (addressFamily == 2) {  // AF_INET (IPv4)
        // IPv4 stored as IPv6-mapped (::ffff:x.x.x.x)
        // Bytes 12-15 contain the IPv4 address
        snprintf(buffer, sizeof(buffer), "%u.%u.%u.%u",
            address[12], address[13], address[14], address[15]);
    }
    else if (addressFamily == 23) {  // AF_INET6 (IPv6)
        // Format as full IPv6 address
        snprintf(buffer, sizeof(buffer),
            "%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x:%02x%02x",
            address[0], address[1], address[2], address[3],
            address[4], address[5], address[6], address[7],
            address[8], address[9], address[10], address[11],
            address[12], address[13], address[14], address[15]);
    }
    else {
        snprintf(buffer, sizeof(buffer), "Unknown");
    }

    return buffer;
}

} // namespace YourEDR
