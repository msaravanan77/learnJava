# Integration tests for driver-service communication
# Framework: Pester
# Requirements: Driver must be loaded, service must be running

Describe "Driver-Service Communication Integration Tests" {
    BeforeAll {
        # Verify prerequisites
        $driverLoaded = (fltmc filters | Select-String "YourEDRFilter") -ne $null
        if (-not $driverLoaded) {
            throw "YourEDRFilter driver is not loaded. Run: fltmc load YourEDRFilter"
        }

        $serviceRunning = (Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue)?.Status -eq "Running"
        if (-not $serviceRunning) {
            Write-Warning "YourEDRService is not running. Some tests may fail."
        }

        # Test device path
        $script:DevicePath = "\\.\ YourEDRFilter"
        $script:LogPath = "C:\ProgramData\YourEDR\Logs"
    }

    Context "Device Handle Operations" {
        It "Opens device handle successfully" {
            # Use P/Invoke to open device handle
            Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class DeviceIO {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern IntPtr CreateFile(
        string lpFileName,
        uint dwDesiredAccess,
        uint dwShareMode,
        IntPtr lpSecurityAttributes,
        uint dwCreationDisposition,
        uint dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr hObject);

    public const uint GENERIC_READ = 0x80000000;
    public const uint GENERIC_WRITE = 0x40000000;
    public const uint OPEN_EXISTING = 3;
    public const uint FILE_ATTRIBUTE_NORMAL = 0x80;
}
"@
            $handle = [DeviceIO]::CreateFile(
                $script:DevicePath,
                [DeviceIO]::GENERIC_READ -bor [DeviceIO]::GENERIC_WRITE,
                0,
                [IntPtr]::Zero,
                [DeviceIO]::OPEN_EXISTING,
                [DeviceIO]::FILE_ATTRIBUTE_NORMAL,
                [IntPtr]::Zero
            )

            $handle.ToInt64() | Should -Not -Be -1
            [DeviceIO]::CloseHandle($handle) | Should -Be $true
        }

        It "Fails to open with invalid path" {
            $handle = [DeviceIO]::CreateFile(
                "\\.\InvalidDevice",
                [DeviceIO]::GENERIC_READ,
                0,
                [IntPtr]::Zero,
                [DeviceIO]::OPEN_EXISTING,
                [DeviceIO]::FILE_ATTRIBUTE_NORMAL,
                [IntPtr]::Zero
            )

            $handle.ToInt64() | Should -Be -1
        }
    }

    Context "IOCTL Operations" {
        BeforeEach {
            # Open device handle for each test
            $script:DeviceHandle = [DeviceIO]::CreateFile(
                $script:DevicePath,
                [DeviceIO]::GENERIC_READ -bor [DeviceIO]::GENERIC_WRITE,
                0,
                [IntPtr]::Zero,
                [DeviceIO]::OPEN_EXISTING,
                [DeviceIO]::FILE_ATTRIBUTE_NORMAL,
                [IntPtr]::Zero
            )
        }

        AfterEach {
            if ($script:DeviceHandle -and $script:DeviceHandle.ToInt64() -ne -1) {
                [DeviceIO]::CloseHandle($script:DeviceHandle) | Out-Null
            }
        }

        It "Gets driver version via IOCTL" {
            # IOCTL_YOUREDR_GET_VERSION = CTL_CODE(FILE_DEVICE_YOUREDR, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
            # FILE_DEVICE_YOUREDR = 0x8000
            # IOCTL code calculation: (0x8000 << 16) | (0 << 14) | (0x800 << 2) | 0
            $ioctlGetVersion = 0x80002000

            Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class VersionStruct {
    public ushort Major;
    public ushort Minor;
    public ushort Build;
    public ushort Revision;
}

public class IOCTLHelper {
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool DeviceIoControl(
        IntPtr hDevice,
        uint dwIoControlCode,
        IntPtr lpInBuffer,
        uint nInBufferSize,
        IntPtr lpOutBuffer,
        uint nOutBufferSize,
        out uint lpBytesReturned,
        IntPtr lpOverlapped);
}
"@

            $outBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal(8)
            try {
                $bytesReturned = 0
                $result = [IOCTLHelper]::DeviceIoControl(
                    $script:DeviceHandle,
                    $ioctlGetVersion,
                    [IntPtr]::Zero,
                    0,
                    $outBuffer,
                    8,
                    [ref]$bytesReturned,
                    [IntPtr]::Zero
                )

                $result | Should -Be $true
                $bytesReturned | Should -Be 8

                # Read version
                $major = [Runtime.InteropServices.Marshal]::ReadInt16($outBuffer, 0)
                $minor = [Runtime.InteropServices.Marshal]::ReadInt16($outBuffer, 2)

                $major | Should -Be 2
                $minor | Should -Be 0
            }
            finally {
                [Runtime.InteropServices.Marshal]::FreeHGlobal($outBuffer)
            }
        }

        It "Gets statistics via IOCTL" {
            $ioctlGetStats = 0x8000200C  # IOCTL_YOUREDR_GET_STATS

            $outBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal(32)
            try {
                $bytesReturned = 0
                $result = [IOCTLHelper]::DeviceIoControl(
                    $script:DeviceHandle,
                    $ioctlGetStats,
                    [IntPtr]::Zero,
                    0,
                    $outBuffer,
                    32,
                    [ref]$bytesReturned,
                    [IntPtr]::Zero
                )

                $result | Should -Be $true
                $bytesReturned | Should -BeGreaterThan 0

                # Read stats
                $totalQueued = [Runtime.InteropServices.Marshal]::ReadInt64($outBuffer, 0)
                $totalQueued | Should -BeGreaterOrEqual 0
            }
            finally {
                [Runtime.InteropServices.Marshal]::FreeHGlobal($outBuffer)
            }
        }
    }

    Context "Event Retrieval" {
        It "Retrieves events after file operation" {
            # Perform file operation to generate event
            $testFile = "$env:TEMP\youredr_test_$(Get-Random).txt"
            "Test content" | Out-File -FilePath $testFile -Force

            # Wait for event to be queued
            Start-Sleep -Milliseconds 500

            # Check if event appears in log
            $logFiles = Get-ChildItem -Path $script:LogPath -Filter "events_*.jsonl" -ErrorAction SilentlyContinue
            $logFiles | Should -Not -BeNullOrEmpty

            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $events = Get-Content -Path $latestLog.FullName -Tail 100 | ConvertFrom-Json

            $fileCreateEvent = $events | Where-Object {
                $_.eventType -eq "FileCreate" -and $_.filePath -like "*youredr_test_*"
            }

            $fileCreateEvent | Should -Not -BeNullOrEmpty
            $fileCreateEvent.processId | Should -BeGreaterThan 0

            # Cleanup
            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }
    }

    Context "Configuration Management" {
        It "Sets configuration via IOCTL" {
            $ioctlSetConfig = 0x80002008  # IOCTL_YOUREDR_SET_CONFIG

            # Create config structure (simplified)
            $configSize = 16  # Size of YOUREDR_CONFIG
            $inBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal($configSize)
            try {
                # Set EnableFileMonitoring = TRUE
                [Runtime.InteropServices.Marshal]::WriteInt32($inBuffer, 0, 1)

                $bytesReturned = 0
                $result = [IOCTLHelper]::DeviceIoControl(
                    $script:DeviceHandle,
                    $ioctlSetConfig,
                    $inBuffer,
                    $configSize,
                    [IntPtr]::Zero,
                    0,
                    [ref]$bytesReturned,
                    [IntPtr]::Zero
                )

                $result | Should -Be $true
            }
            finally {
                [Runtime.InteropServices.Marshal]::FreeHGlobal($inBuffer)
            }
        }
    }
}
