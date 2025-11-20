# YourEDR Test Framework

**Version**: 1.0
**Date**: 2025-11-19
**Status**: Complete Test Framework Implementation

---

## Overview

Comprehensive test framework for YourEDR Windows kernel driver and service, covering unit tests, integration tests, end-to-end tests, and stress tests.

---

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── driver/             # Kernel driver unit tests
│   ├── service/            # Service unit tests
│   └── run_unit_tests.ps1
├── integration/            # Integration tests
│   ├── driver_service/    # Driver-service communication
│   ├── json_output/       # JSON serialization
│   └── run_integration_tests.ps1
├── e2e/                    # End-to-end tests
│   ├── filesystem/        # File monitoring E2E
│   ├── network/           # Network monitoring E2E
│   └── run_e2e_tests.ps1
├── stress/                 # Stress and performance tests
│   ├── high_volume/       # High event volume
│   ├── memory_leak/       # Memory leak detection
│   └── run_stress_tests.ps1
├── fixtures/              # Test data and configurations
└── scripts/               # Test utilities

```

---

## Test Categories

### 1. Unit Tests

**Purpose**: Test individual components in isolation

**Coverage**:
- Ring buffer operations
- Event structure validation
- Path exclusion logic
- JSON serialization
- IOCTL communication

**Framework**: C++ with GoogleTest (driver), C# with NUnit (service)

### 2. Integration Tests

**Purpose**: Test component interactions

**Coverage**:
- Driver-to-service communication
- Event queuing and dequeuing
- Configuration management
- Log file rotation

**Framework**: PowerShell with Pester

### 3. End-to-End Tests

**Purpose**: Test complete workflows

**Coverage**:
- File create/write/delete/rename detection
- Network connection monitoring (TCP/UDP, IPv4/IPv6)
- Process attribution
- Event accuracy and completeness

**Framework**: PowerShell with validation scripts

### 4. Stress Tests

**Purpose**: Test system under load

**Coverage**:
- High event volume (>10,000 events/sec)
- Memory leak detection
- Long-running stability (24+ hours)
- Resource exhaustion scenarios

**Framework**: Custom PowerShell scripts

---

## Quick Start

### Run All Tests

```powershell
# Complete test suite (requires admin)
.\tests\run_all_tests.ps1

# Specific test categories
.\tests\unit\run_unit_tests.ps1
.\tests\integration\run_integration_tests.ps1
.\tests\e2e\run_e2e_tests.ps1
.\tests\stress\run_stress_tests.ps1
```

### Prerequisites

```powershell
# Install test dependencies
.\tests\scripts\install_test_dependencies.ps1

# Dependencies:
# - Pester (PowerShell testing)
# - NUnit (C# testing)
# - GoogleTest (C++ testing - for driver unit tests)
# - Windows Driver Kit (WDK)
```

---

## Test Details

### Unit Tests

#### Ring Buffer Tests (`tests/unit/driver/test_ring_buffer.cpp`)

```cpp
TEST(RingBuffer, InitializeSuccess) {
    // Test buffer initialization
}

TEST(RingBuffer, QueueEventSuccess) {
    // Test event queuing
}

TEST(RingBuffer, QueueEventBufferFull) {
    // Test buffer full scenario
}

TEST(RingBuffer, DequeueEventSuccess) {
    // Test event dequeuing
}

TEST(RingBuffer, ConcurrentAccess) {
    // Test thread safety
}
```

#### JSON Serialization Tests (`tests/unit/service/JsonLoggerTests.cs`)

```csharp
[Test]
public void ConvertFileEvent_ValidEvent_ReturnsCorrectJson() {
    // Test file event JSON conversion
}

[Test]
public void FormatIPAddress_IPv4_ReturnsCorrectFormat() {
    // Test IPv4 formatting
}

[Test]
public void FormatIPAddress_IPv6_ReturnsCorrectFormat() {
    // Test IPv6 formatting
}
```

### Integration Tests

#### Driver-Service Communication (`tests/integration/driver_service/test_communication.Tests.ps1`)

```powershell
Describe "Driver-Service Communication" {
    It "Opens device handle successfully" {
        # Test device open
    }

    It "Retrieves driver version" {
        # Test IOCTL_GET_VERSION
    }

    It "Gets events from ring buffer" {
        # Test IOCTL_GET_EVENT
    }

    It "Sets configuration" {
        # Test IOCTL_SET_CONFIG
    }

    It "Gets statistics" {
        # Test IOCTL_GET_STATS
    }
}
```

### End-to-End Tests

#### File Monitoring E2E (`tests/e2e/filesystem/test_file_operations.Tests.ps1`)

```powershell
Describe "File Monitoring E2E" {
    It "Detects file creation" {
        # Create file, verify event
    }

    It "Detects file write" {
        # Write to file, verify event
    }

    It "Detects file deletion" {
        # Delete file, verify event
    }

    It "Detects file rename" {
        # Rename file, verify event
    }

    It "Respects path exclusions" {
        # Create file in excluded path, verify no event
    }
}
```

#### Network Monitoring E2E (`tests/e2e/network/test_network_connections.Tests.ps1`)

```powershell
Describe "Network Monitoring E2E" {
    It "Detects outbound TCP connection" {
        # Connect to remote server, verify event
    }

    It "Detects inbound TCP connection" {
        # Start server, accept connection, verify event
    }

    It "Detects outbound UDP connection" {
        # Send UDP packet, verify event
    }

    It "Detects IPv6 connections" {
        # Connect via IPv6, verify event
    }

    It "Captures process name" {
        # Verify process attribution
    }
}
```

### Stress Tests

#### High Volume Test (`tests/stress/high_volume/test_high_event_rate.ps1`)

```powershell
# Generate 100,000 file operations
# Verify:
# - No events dropped (or acceptable drop rate)
# - Service remains responsive
# - Memory usage stable
# - CPU usage acceptable
```

#### Memory Leak Test (`tests/stress/memory_leak/test_memory_stability.ps1`)

```powershell
# Run for 1 hour with continuous events
# Monitor:
# - Driver non-paged pool usage
# - Service working set
# - Handle count
# - Verify no leaks
```

---

## Test Execution

### Manual Testing Checklist

#### Phase 1: File System Monitoring

- [ ] File create detection
- [ ] File write detection
- [ ] File delete detection
- [ ] File rename detection
- [ ] Path exclusions work
- [ ] Process ID captured correctly
- [ ] Timestamps accurate
- [ ] JSON format valid
- [ ] Log rotation works
- [ ] Driver survives system stress

#### Phase 2: Network Monitoring

- [ ] TCP outbound connections (IPv4)
- [ ] TCP outbound connections (IPv6)
- [ ] TCP inbound connections (IPv4)
- [ ] TCP inbound connections (IPv6)
- [ ] UDP connections (IPv4)
- [ ] UDP connections (IPv6)
- [ ] Process name captured
- [ ] Connection ID unique
- [ ] IP addresses formatted correctly
- [ ] Ports captured correctly

### Automated Test Runs

```powershell
# Full regression suite
.\tests\run_all_tests.ps1 -Verbose -GenerateReport

# Output:
# - HTML test report: tests\reports\test_results.html
# - JUnit XML: tests\reports\test_results.xml
# - Code coverage: tests\reports\coverage.html
```

---

## Expected Results

### Unit Tests
- **Target**: 100% pass rate
- **Coverage**: >80% code coverage
- **Duration**: <2 minutes

### Integration Tests
- **Target**: 100% pass rate
- **Duration**: <5 minutes

### E2E Tests
- **Target**: >95% pass rate (some timing-dependent tests may be flaky)
- **Duration**: <10 minutes

### Stress Tests
- **Target**: No crashes, acceptable performance degradation
- **Duration**: 1-24 hours

---

## Performance Benchmarks

### File System Monitoring

| Metric | Target | Acceptance Criteria |
|--------|--------|---------------------|
| File open latency overhead | <50 μs | +20% max |
| Throughput degradation | <5% | Acceptable |
| CPU overhead (idle) | <1% | Acceptable |
| Memory usage | <5 MB | Fixed overhead |
| Max event rate | >10,000/sec | Configurable limit |
| Event drop rate | <0.1% | At max throughput |

### Network Monitoring

| Metric | Target | Acceptance Criteria |
|--------|--------|---------------------|
| Connection latency overhead | <20 μs | Minimal impact |
| Throughput degradation | <2% | Acceptable |
| CPU overhead (idle) | <0.5% | Acceptable |
| Memory usage | <3 MB | Fixed overhead |
| Max connection rate | >5,000/sec | High volume |

---

## Test Data

### Fixtures

**File**: `tests/fixtures/test_files.json`
```json
{
  "testFiles": [
    {"path": "C:\\TestData\\test1.txt", "content": "Test file 1"},
    {"path": "C:\\TestData\\test2.bin", "content": "Binary data"},
    {"path": "C:\\TestData\\excluded.tmp", "excluded": true}
  ]
}
```

**File**: `tests/fixtures/network_targets.json`
```json
{
  "targets": [
    {"host": "example.com", "port": 80, "protocol": "TCP"},
    {"host": "8.8.8.8", "port": 53, "protocol": "UDP"},
    {"host": "::1", "port": 8080, "protocol": "TCP", "ipv6": true}
  ]
}
```

---

## Continuous Integration

### GitHub Actions Workflow (`.github/workflows/test.yml`)

```yaml
name: YourEDR Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-2022
    steps:
      - uses: actions/checkout@v3
      - name: Install WDK
        run: choco install windowsdriverkit10
      - name: Build driver
        run: .\scripts\build.ps1 -Configuration Debug
      - name: Sign driver
        run: .\scripts\sign.ps1 -TestCert
      - name: Install driver
        run: .\scripts\install-local.ps1
      - name: Run tests
        run: .\tests\run_all_tests.ps1 -GenerateReport
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/reports/
```

---

## Troubleshooting

### Common Test Failures

#### "Driver not loaded"
```powershell
# Check driver status
fltmc filters | findstr YourEDR

# Reload driver
fltmc unload YourEDRFilter
fltmc load YourEDRFilter
```

#### "Service not responding"
```powershell
# Restart service
Restart-Service YourEDRService

# Check logs
Get-Content C:\ProgramData\YourEDR\Logs\*.jsonl -Tail 100
```

#### "Test isolation issues"
```powershell
# Clean test environment
.\tests\scripts\cleanup_test_environment.ps1

# Run tests with cleanup
.\tests\run_all_tests.ps1 -CleanBefore -CleanAfter
```

---

## Test Maintenance

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `test_<component>.Tests.ps1` or `Test<Component>.cs`
3. Add test to relevant runner script
4. Update this documentation
5. Ensure test is idempotent and isolated

### Test Review Checklist

- [ ] Test is deterministic (no random failures)
- [ ] Test cleans up after itself
- [ ] Test has clear assertions
- [ ] Test has meaningful error messages
- [ ] Test runs in <1 minute (unit/integration) or has `[Slow]` tag
- [ ] Test is documented

---

## References

- [Build Verification Guide](BUILD_VERIFICATION_GUIDE.md)
- [Development Testing Guide](docs/technical/06-development-testing-guide.md)
- [Phase 1 Testing](docs/technical/PHASE1_FILESYSTEM_MONITORING.md#testing)
- [Phase 2 Testing](docs/technical/PHASE2_NETWORK_MONITORING.md#testing)

---

**Document End**

**Last Updated**: 2025-11-19
**Maintained by**: Development Team
