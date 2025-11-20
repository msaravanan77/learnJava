# End-to-end tests for file system monitoring
# Framework: Pester
# Requirements: Driver loaded, service running

Describe "File System Monitoring E2E Tests" {
    BeforeAll {
        # Verify driver and service
        $driverLoaded = (fltmc filters | Select-String "YourEDRFilter") -ne $null
        if (-not $driverLoaded) {
            throw "YourEDRFilter driver not loaded"
        }

        $serviceStatus = (Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue)?.Status
        if ($serviceStatus -ne "Running") {
            throw "YourEDRService not running. Status: $serviceStatus"
        }

        $script:LogPath = "C:\ProgramData\YourEDR\Logs"
        $script:TestDir = "$env:TEMP\YourEDR_E2E_Tests"

        # Create test directory
        if (-not (Test-Path $script:TestDir)) {
            New-Item -Path $script:TestDir -ItemType Directory | Out-Null
        }

        # Helper function to get recent events
        function Get-RecentEDREvents {
            param([int]$Count = 50)

            $logFiles = Get-ChildItem -Path $script:LogPath -Filter "events_*.jsonl" -ErrorAction SilentlyContinue
            if (-not $logFiles) {
                return @()
            }

            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $events = Get-Content -Path $latestLog.FullName -Tail $Count -ErrorAction SilentlyContinue |
                      ForEach-Object { $_ | ConvertFrom-Json }

            return $events
        }

        $script:GetRecentEDREvents = ${function:Get-RecentEDREvents}
    }

    AfterAll {
        # Cleanup test directory
        if (Test-Path $script:TestDir) {
            Remove-Item -Path $script:TestDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Context "File Create Operations" {
        It "Detects file creation with CreateFile" {
            $testFile = Join-Path $script:TestDir "test_create_$(Get-Random).txt"

            # Create file
            "Test content" | Out-File -FilePath $testFile -Force

            # Wait for event processing
            Start-Sleep -Milliseconds 500

            # Check for event
            $events = & $script:GetRecentEDREvents -Count 100
            $createEvent = $events | Where-Object {
                $_.eventType -eq "FileCreate" -and
                $_.filePath -like "*test_create_*"
            } | Select-Object -First 1

            $createEvent | Should -Not -BeNullOrEmpty
            $createEvent.processId | Should -BeGreaterThan 0
            $createEvent.threadId | Should -BeGreaterThan 0
            $createEvent.timestamp | Should -Not -BeNullOrEmpty
            $createEvent.desiredAccess | Should -Not -BeNullOrEmpty

            # Cleanup
            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }

        It "Detects new file creation" {
            $testFile = Join-Path $script:TestDir "newfile_$(Get-Random).bin"

            # Use .NET to create file
            [System.IO.File]::WriteAllBytes($testFile, @(0x01, 0x02, 0x03))

            Start-Sleep -Milliseconds 500

            $events = & $script:GetRecentEDREvents -Count 100
            $createEvent = $events | Where-Object {
                $_.eventType -eq "FileCreate" -and
                $_.filePath -like "*newfile_*"
            }

            $createEvent | Should -Not -BeNullOrEmpty

            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }
    }

    Context "File Write Operations" {
        It "Detects file write" {
            $testFile = Join-Path $script:TestDir "test_write_$(Get-Random).txt"

            # Create file first
            "Initial" | Out-File -FilePath $testFile -Force
            Start-Sleep -Milliseconds 300

            # Append to file (generates write event)
            Add-Content -Path $testFile -Value "Appended data"

            Start-Sleep -Milliseconds 500

            $events = & $script:GetRecentEDREvents -Count 100
            $writeEvent = $events | Where-Object {
                $_.eventType -eq "FileWrite" -and
                $_.filePath -like "*test_write_*"
            }

            $writeEvent | Should -Not -BeNullOrEmpty
            $writeEvent.processId | Should -BeGreaterThan 0

            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }
    }

    Context "File Delete Operations" {
        It "Detects file deletion" {
            $testFile = Join-Path $script:TestDir "test_delete_$(Get-Random).txt"

            # Create file
            "To be deleted" | Out-File -FilePath $testFile -Force
            Start-Sleep -Milliseconds 300

            # Delete file
            Remove-Item -Path $testFile -Force

            Start-Sleep -Milliseconds 500

            $events = & $script:GetRecentEDREvents -Count 100
            $deleteEvent = $events | Where-Object {
                $_.eventType -eq "FileDelete" -and
                $_.filePath -like "*test_delete_*"
            }

            $deleteEvent | Should -Not -BeNullOrEmpty
            $deleteEvent.processId | Should -BeGreaterThan 0
        }
    }

    Context "File Rename Operations" {
        It "Detects file rename" {
            $sourceName = "test_rename_source_$(Get-Random).txt"
            $targetName = "test_rename_target_$(Get-Random).txt"
            $sourceFile = Join-Path $script:TestDir $sourceName
            $targetFile = Join-Path $script:TestDir $targetName

            # Create source file
            "Rename me" | Out-File -FilePath $sourceFile -Force
            Start-Sleep -Milliseconds 300

            # Rename file
            Rename-Item -Path $sourceFile -NewName $targetName

            Start-Sleep -Milliseconds 500

            $events = & $script:GetRecentEDREvents -Count 100
            $renameEvent = $events | Where-Object {
                $_.eventType -eq "FileRename" -and
                $_.filePath -like "*test_rename_source_*"
            }

            $renameEvent | Should -Not -BeNullOrEmpty
            $renameEvent.processId | Should -BeGreaterThan 0

            # Cleanup
            Remove-Item -Path $targetFile -Force -ErrorAction SilentlyContinue
        }
    }

    Context "Path Exclusions" {
        It "Excludes .tmp files from monitoring" {
            $testFile = Join-Path $script:TestDir "excluded_$(Get-Random).tmp"

            # Create .tmp file
            "Excluded" | Out-File -FilePath $testFile -Force

            Start-Sleep -Milliseconds 500

            # Check that NO event was generated
            $events = & $script:GetRecentEDREvents -Count 100
            $tmpEvent = $events | Where-Object {
                $_.filePath -like "*excluded_*.tmp"
            }

            $tmpEvent | Should -BeNullOrEmpty

            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }

        It "Excludes system32 directory" {
            # Attempt to create file in System32 (if possible)
            # This test may require admin privileges
            try {
                $testFile = "C:\Windows\System32\youredr_test_$(Get-Random).txt"
                "Test" | Out-File -FilePath $testFile -Force -ErrorAction Stop

                Start-Sleep -Milliseconds 500

                $events = & $script:GetRecentEDREvents -Count 100
                $sys32Event = $events | Where-Object {
                    $_.filePath -like "C:\Windows\System32\youredr_test_*"
                }

                $sys32Event | Should -BeNullOrEmpty

                Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
            }
            catch {
                # If we can't write to System32, skip this test
                Set-ItResult -Skipped -Because "Cannot write to System32 (expected without admin)"
            }
        }
    }

    Context "Process Attribution" {
        It "Captures correct process ID" {
            $testFile = Join-Path $script:TestDir "test_pid_$(Get-Random).txt"
            $currentPID = $PID

            "Test PID" | Out-File -FilePath $testFile -Force

            Start-Sleep -Milliseconds 500

            $events = & $script:GetRecentEDREvents -Count 100
            $pidEvent = $events | Where-Object {
                $_.filePath -like "*test_pid_*"
            } | Select-Object -First 1

            $pidEvent | Should -Not -BeNullOrEmpty
            $pidEvent.processId | Should -Be $currentPID

            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }
    }

    Context "JSON Format Validation" {
        It "Produces valid JSON output" {
            $testFile = Join-Path $script:TestDir "test_json_$(Get-Random).txt"

            "JSON test" | Out-File -FilePath $testFile -Force

            Start-Sleep -Milliseconds 500

            # Read raw JSON line
            $logFiles = Get-ChildItem -Path $script:LogPath -Filter "events_*.jsonl"
            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $jsonLine = Get-Content -Path $latestLog.FullName -Tail 1

            # Validate JSON parse
            { $jsonLine | ConvertFrom-Json } | Should -Not -Throw

            $event = $jsonLine | ConvertFrom-Json

            # Validate required fields
            $event.eventType | Should -Not -BeNullOrEmpty
            $event.timestamp | Should -Not -BeNullOrEmpty
            $event.processId | Should -BeGreaterThan 0
            $event.filePath | Should -Not -BeNullOrEmpty

            Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue
        }
    }
}
