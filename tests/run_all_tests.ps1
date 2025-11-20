# Master test runner for YourEDR
# Runs all test suites: unit, integration, E2E, and optionally stress tests

param(
    [switch]$SkipUnit,
    [switch]$SkipIntegration,
    [switch]$SkipE2E,
    [switch]$IncludeStress,
    [switch]$GenerateReport,
    [string]$ReportPath = ".\tests\reports",
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "=" * 80
Write-Host "YourEDR Comprehensive Test Suite"
Write-Host "=" * 80
Write-Host "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Verify prerequisites
Write-Host "Verifying prerequisites..."

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as administrator. Some tests may fail."
}

# Check driver
$driverLoaded = (fltmc filters | Select-String "YourEDRFilter") -ne $null
if (-not $driverLoaded) {
    Write-Error "YourEDRFilter driver is not loaded!"
    Write-Host "Run: fltmc load YourEDRFilter"
    exit 1
}
Write-Host "✓ Driver loaded"

# Check service
$serviceStatus = (Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue)?.Status
if ($serviceStatus -ne "Running") {
    Write-Error "YourEDRService is not running! Status: $serviceStatus"
    exit 1
}
Write-Host "✓ Service running"

# Check Pester
if (-not (Get-Module -ListAvailable -Name Pester)) {
    Write-Error "Pester module not installed!"
    Write-Host "Run: Install-Module -Name Pester -Force -SkipPublisherCheck"
    exit 1
}
Write-Host "✓ Pester installed"

Write-Host ""

# Initialize results
$results = @{
    Unit        = $null
    Integration = $null
    E2E         = $null
    Stress      = $null
}

$startTime = Get-Date

# Run Unit Tests
if (-not $SkipUnit) {
    Write-Host "─" * 80
    Write-Host "Running Unit Tests..."
    Write-Host "─" * 80

    # Note: Unit tests require GoogleTest compilation
    # For now, we'll check if they exist
    $unitTestExe = ".\tests\unit\driver\test_ring_buffer.exe"
    if (Test-Path $unitTestExe) {
        $unitResult = & $unitTestExe
        $results.Unit = @{
            ExitCode = $LASTEXITCODE
            Output   = $unitResult
        }
        Write-Host "Unit tests exit code: $LASTEXITCODE"
    }
    else {
        Write-Warning "Unit test executable not found. Skipping unit tests."
        Write-Host "Build unit tests first: compile test_ring_buffer.cpp with GoogleTest"
    }

    Write-Host ""
}

# Run Integration Tests
if (-not $SkipIntegration) {
    Write-Host "─" * 80
    Write-Host "Running Integration Tests..."
    Write-Host "─" * 80

    $integrationTests = Get-ChildItem -Path ".\tests\integration" -Filter "*.Tests.ps1" -Recurse

    foreach ($test in $integrationTests) {
        Write-Host "Running: $($test.Name)"
        $testResult = Invoke-Pester -Path $test.FullName -PassThru

        if (-not $results.Integration) {
            $results.Integration = @()
        }
        $results.Integration += $testResult
    }

    Write-Host ""
}

# Run E2E Tests
if (-not $SkipE2E) {
    Write-Host "─" * 80
    Write-Host "Running End-to-End Tests..."
    Write-Host "─" * 80

    $e2eTests = Get-ChildItem -Path ".\tests\e2e" -Filter "*.Tests.ps1" -Recurse

    foreach ($test in $e2eTests) {
        Write-Host "Running: $($test.Name)"
        $testResult = Invoke-Pester -Path $test.FullName -PassThru

        if (-not $results.E2E) {
            $results.E2E = @()
        }
        $results.E2E += $testResult
    }

    Write-Host ""
}

# Run Stress Tests
if ($IncludeStress) {
    Write-Host "─" * 80
    Write-Host "Running Stress Tests..."
    Write-Host "─" * 80
    Write-Warning "Stress tests can take several minutes..."

    $stressResult = & ".\tests\stress\high_volume\test_high_event_rate.ps1" -NumOperations 5000

    $results.Stress = @{
        ExitCode = $LASTEXITCODE
    }

    Write-Host ""
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

# Summary
Write-Host "=" * 80
Write-Host "TEST SUMMARY"
Write-Host "=" * 80

$totalPassed = 0
$totalFailed = 0
$totalSkipped = 0

if ($results.Integration) {
    foreach ($result in $results.Integration) {
        $totalPassed += $result.PassedCount
        $totalFailed += $result.FailedCount
        $totalSkipped += $result.SkippedCount
    }
}

if ($results.E2E) {
    foreach ($result in $results.E2E) {
        $totalPassed += $result.PassedCount
        $totalFailed += $result.FailedCount
        $totalSkipped += $result.SkippedCount
    }
}

Write-Host "Total Tests Passed:  $totalPassed"
Write-Host "Total Tests Failed:  $totalFailed"
Write-Host "Total Tests Skipped: $totalSkipped"
Write-Host "Duration:            $([math]::Round($duration, 2)) seconds"
Write-Host ""

if ($results.Unit -and $results.Unit.ExitCode -ne 0) {
    Write-Host "Unit Tests:        FAILED ✗"
} elseif ($results.Unit) {
    Write-Host "Unit Tests:        PASSED ✓"
}

if ($results.Integration) {
    $integrationPassed = ($results.Integration | Measure-Object -Property FailedCount -Sum).Sum -eq 0
    Write-Host "Integration Tests: $(if ($integrationPassed) { 'PASSED ✓' } else { 'FAILED ✗' })"
}

if ($results.E2E) {
    $e2ePassed = ($results.E2E | Measure-Object -Property FailedCount -Sum).Sum -eq 0
    Write-Host "E2E Tests:         $(if ($e2ePassed) { 'PASSED ✓' } else { 'FAILED ✗' })"
}

if ($results.Stress) {
    Write-Host "Stress Tests:      $(if ($results.Stress.ExitCode -eq 0) { 'PASSED ✓' } else { 'FAILED ✗' })"
}

# Generate report
if ($GenerateReport) {
    if (-not (Test-Path $ReportPath)) {
        New-Item -Path $ReportPath -ItemType Directory -Force | Out-Null
    }

    $reportFile = Join-Path $ReportPath "test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>YourEDR Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .passed { color: green; font-weight: bold; }
        .failed { color: red; font-weight: bold; }
        .summary { background-color: #f0f0f0; padding: 15px; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>YourEDR Test Results</h1>
    <div class="summary">
        <p><strong>Date:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p><strong>Duration:</strong> $([math]::Round($duration, 2)) seconds</p>
        <p><strong>Total Passed:</strong> <span class="passed">$totalPassed</span></p>
        <p><strong>Total Failed:</strong> <span class="failed">$totalFailed</span></p>
        <p><strong>Total Skipped:</strong> $totalSkipped</p>
    </div>
</body>
</html>
"@

    $html | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Host ""
    Write-Host "Report generated: $reportFile"
}

Write-Host "=" * 80

# Exit with appropriate code
$overallPassed = $totalFailed -eq 0
exit $(if ($overallPassed) { 0 } else { 1 })
