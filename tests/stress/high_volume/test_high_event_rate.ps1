# Stress test: High volume file operations
# Purpose: Verify system stability under high event load

param(
    [int]$NumOperations = 10000,
    [int]$ConcurrentThreads = 4,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 80
Write-Host "YourEDR High Volume Stress Test"
Write-Host "=" * 80
Write-Host "Operations: $NumOperations"
Write-Host "Concurrent threads: $ConcurrentThreads"
Write-Host ""

# Verify driver loaded
if (-not (fltmc filters | Select-String "YourEDRFilter")) {
    throw "YourEDRFilter driver not loaded"
}

# Test directory
$testDir = "$env:TEMP\YourEDR_Stress_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -Path $testDir -ItemType Directory -Force | Out-Null

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Created test directory: $testDir"

# Performance counters
$script:OperationsCompleted = 0
$script:OperationsFailed = 0
$script:StartTime = Get-Date

# Worker function
$workerScript = {
    param($TestDir, $OperationsPerThread, $ThreadId)

    $success = 0
    $failed = 0

    for ($i = 0; $i < $OperationsPerThread; $i++) {
        try {
            $fileName = "thread${ThreadId}_file${i}.txt"
            $filePath = Join-Path $TestDir $fileName

            # Create file
            "Test data $i" | Out-File -FilePath $filePath -Force

            # Write to file
            Add-Content -Path $filePath -Value "More data"

            # Rename file
            $newName = "thread${ThreadId}_renamed${i}.txt"
            $newPath = Join-Path $TestDir $newName
            Rename-Item -Path $filePath -NewName $newName

            # Delete file
            Remove-Item -Path $newPath -Force

            $success++

            if ($i % 100 -eq 0 -and $i -gt 0) {
                Write-Host "[Thread $ThreadId] Progress: $i / $OperationsPerThread"
            }
        }
        catch {
            $failed++
        }
    }

    return @{
        Success = $success
        Failed  = $failed
    }
}

# Start performance monitoring job
$perfMonJob = Start-Job -ScriptBlock {
    param($Duration)
    $startTime = Get-Date

    while ((Get-Date) -lt $startTime.AddSeconds($Duration)) {
        $process = Get-Process -Name "YourEDRService" -ErrorAction SilentlyContinue
        if ($process) {
            [PSCustomObject]@{
                Timestamp     = Get-Date
                WorkingSetMB  = [math]::Round($process.WorkingSet64 / 1MB, 2)
                HandleCount   = $process.HandleCount
                ThreadCount   = $process.Threads.Count
                CPU           = [math]::Round($process.CPU, 2)
            }
        }
        Start-Sleep -Seconds 5
    }
} -ArgumentList 300  # Monitor for up to 5 minutes

# Start worker threads
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting $ConcurrentThreads worker threads..."

$opsPerThread = [math]::Floor($NumOperations / $ConcurrentThreads)
$jobs = @()

for ($t = 0; $t < $ConcurrentThreads; $t++) {
    $job = Start-Job -ScriptBlock $workerScript -ArgumentList $testDir, $opsPerThread, $t
    $jobs += $job
}

# Wait for completion
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Waiting for workers to complete..."

$jobs | Wait-Job | Out-Null

# Collect results
$totalSuccess = 0
$totalFailed = 0

foreach ($job in $jobs) {
    $result = Receive-Job -Job $job
    $totalSuccess += $result.Success
    $totalFailed += $result.Failed
    Remove-Job -Job $job
}

$endTime = Get-Date
$duration = ($endTime - $script:StartTime).TotalSeconds

# Stop performance monitoring
Stop-Job -Job $perfMonJob | Out-Null
$perfData = Receive-Job -Job $perfMonJob
Remove-Job -Job $perfMonJob

# Get driver statistics
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class DriverStats {
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
    public static extern bool DeviceIoControl(
        IntPtr hDevice,
        uint dwIoControlCode,
        IntPtr lpInBuffer,
        uint nInBufferSize,
        IntPtr lpOutBuffer,
        uint nOutBufferSize,
        out uint lpBytesReturned,
        IntPtr lpOverlapped);

    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr hObject);
}
"@

$deviceHandle = [DriverStats]::CreateFile(
    "\\.\YourEDRFilter",
    0xC0000000,  # GENERIC_READ | GENERIC_WRITE
    0,
    [IntPtr]::Zero,
    3,  # OPEN_EXISTING
    0x80,  # FILE_ATTRIBUTE_NORMAL
    [IntPtr]::Zero
)

$stats = $null
if ($deviceHandle.ToInt64() -ne -1) {
    $ioctlGetStats = 0x8000200C
    $outBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal(32)
    try {
        $bytesReturned = 0
        $result = [DriverStats]::DeviceIoControl(
            $deviceHandle,
            $ioctlGetStats,
            [IntPtr]::Zero,
            0,
            $outBuffer,
            32,
            [ref]$bytesReturned,
            [IntPtr]::Zero
        )

        if ($result) {
            $stats = @{
                TotalQueued   = [Runtime.InteropServices.Marshal]::ReadInt64($outBuffer, 0)
                TotalDropped  = [Runtime.InteropServices.Marshal]::ReadInt64($outBuffer, 8)
                TotalProcessed = [Runtime.InteropServices.Marshal]::ReadInt64($outBuffer, 16)
            }
        }
    }
    finally {
        [Runtime.InteropServices.Marshal]::FreeHGlobal($outBuffer)
        [DriverStats]::CloseHandle($deviceHandle) | Out-Null
    }
}

# Cleanup
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Cleaning up test directory..."
Remove-Item -Path $testDir -Recurse -Force -ErrorAction SilentlyContinue

# Results
Write-Host ""
Write-Host "=" * 80
Write-Host "STRESS TEST RESULTS"
Write-Host "=" * 80
Write-Host "Total Operations:    $($totalSuccess + $totalFailed)"
Write-Host "Successful:          $totalSuccess"
Write-Host "Failed:              $totalFailed"
Write-Host "Duration:            $([math]::Round($duration, 2)) seconds"
Write-Host "Operations/sec:      $([math]::Round($totalSuccess / $duration, 2))"
Write-Host ""

if ($stats) {
    Write-Host "Driver Statistics:"
    Write-Host "  Events Queued:     $($stats.TotalQueued)"
    Write-Host "  Events Dropped:    $($stats.TotalDropped)"
    Write-Host "  Events Processed:  $($stats.TotalProcessed)"
    $dropRate = if ($stats.TotalQueued -gt 0) {
        [math]::Round(($stats.TotalDropped / $stats.TotalQueued) * 100, 2)
    } else { 0 }
    Write-Host "  Drop Rate:         $dropRate%"
    Write-Host ""
}

if ($perfData) {
    Write-Host "Service Performance:"
    $avgWorkingSet = ($perfData | Measure-Object -Property WorkingSetMB -Average).Average
    $maxWorkingSet = ($perfData | Measure-Object -Property WorkingSetMB -Maximum).Maximum
    $avgHandles = ($perfData | Measure-Object -Property HandleCount -Average).Average

    Write-Host "  Avg Working Set:   $([math]::Round($avgWorkingSet, 2)) MB"
    Write-Host "  Max Working Set:   $([math]::Round($maxWorkingSet, 2)) MB"
    Write-Host "  Avg Handle Count:  $([math]::Round($avgHandles, 0))"
    Write-Host ""
}

# Pass/Fail criteria
$passed = $true
$issues = @()

if ($totalFailed -gt ($totalSuccess * 0.01)) {  # More than 1% failure
    $passed = $false
    $issues += "High failure rate: $totalFailed failed operations"
}

if ($stats -and $stats.TotalDropped -gt ($stats.TotalQueued * 0.001)) {  # More than 0.1% dropped
    $passed = $false
    $issues += "High event drop rate: $($stats.TotalDropped) events dropped"
}

if ($perfData) {
    $memGrowth = ($perfData[-1].WorkingSetMB - $perfData[0].WorkingSetMB)
    if ($memGrowth -gt 50) {  # More than 50 MB growth
        $passed = $false
        $issues += "Possible memory leak: $([math]::Round($memGrowth, 2)) MB growth"
    }
}

Write-Host "Test Result: $(if ($passed) { 'PASSED ✓' } else { 'FAILED ✗' })"

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "Issues:"
    $issues | ForEach-Object { Write-Host "  - $_" }
}

Write-Host "=" * 80

exit $(if ($passed) { 0 } else { 1 })
