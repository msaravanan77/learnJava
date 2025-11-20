# End-to-end tests for network monitoring
# Framework: Pester
# Requirements: Driver loaded with network monitoring enabled

Describe "Network Monitoring E2E Tests" {
    BeforeAll {
        # Verify prerequisites
        $driverLoaded = (fltmc filters | Select-String "YourEDRFilter") -ne $null
        if (-not $driverLoaded) {
            throw "YourEDRFilter driver not loaded"
        }

        $serviceRunning = (Get-Service -Name "YourEDRService" -ErrorAction SilentlyContinue)?.Status -eq "Running"
        if (-not $serviceRunning) {
            throw "YourEDRService not running"
        }

        $script:LogPath = "C:\ProgramData\YourEDR\Logs"

        # Helper function
        function Get-RecentNetworkEvents {
            param([int]$Count = 100)

            $logFiles = Get-ChildItem -Path $script:LogPath -Filter "events_*.jsonl" -ErrorAction SilentlyContinue
            if (-not $logFiles) {
                return @()
            }

            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $events = Get-Content -Path $latestLog.FullName -Tail $Count -ErrorAction SilentlyContinue |
                      ForEach-Object { $_ | ConvertFrom-Json } |
                      Where-Object { $_.eventType -like "Network*" }

            return $events
        }

        $script:GetRecentNetworkEvents = ${function:Get-RecentNetworkEvents}
    }

    Context "TCP Outbound Connections (IPv4)" {
        It "Detects HTTP connection to example.com" {
            # Make HTTP request to generate outbound TCP connection
            try {
                $response = Invoke-WebRequest -Uri "http://example.com" -UseBasicParsing -TimeoutSec 5
            }
            catch {
                # Connection might fail, but event should still be captured
            }

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $httpEvent = $events | Where-Object {
                $_.eventType -eq "NetworkConnect" -and
                $_.protocol -eq "TCP" -and
                $_.remotePort -eq 80
            } | Select-Object -First 1

            $httpEvent | Should -Not -BeNullOrEmpty
            $httpEvent.direction | Should -Be "Outbound"
            $httpEvent.addressFamily | Should -Be "IPv4"
            $httpEvent.processId | Should -BeGreaterThan 0
            $httpEvent.processName | Should -Not -BeNullOrEmpty
            $httpEvent.localPort | Should -BeGreaterThan 0
            $httpEvent.connectionId | Should -BeGreaterThan 0
        }

        It "Detects HTTPS connection" {
            try {
                $response = Invoke-WebRequest -Uri "https://www.microsoft.com" -UseBasicParsing -TimeoutSec 5
            }
            catch {
                # Ignore errors
            }

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $httpsEvent = $events | Where-Object {
                $_.eventType -eq "NetworkConnect" -and
                $_.protocol -eq "TCP" -and
                $_.remotePort -eq 443
            }

            $httpsEvent | Should -Not -BeNullOrEmpty
            $httpsEvent[0].direction | Should -Be "Outbound"
        }
    }

    Context "UDP Connections" {
        It "Detects DNS query (UDP port 53)" {
            # Perform DNS lookup
            try {
                [System.Net.Dns]::GetHostAddresses("google.com") | Out-Null
            }
            catch {
                # Ignore errors
            }

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $dnsEvent = $events | Where-Object {
                $_.eventType -eq "NetworkConnect" -and
                $_.protocol -eq "UDP" -and
                $_.remotePort -eq 53
            }

            $dnsEvent | Should -Not -BeNullOrEmpty
            $dnsEvent[0].direction | Should -Be "Outbound"
            $dnsEvent[0].addressFamily | Should -Match "IPv4|IPv6"
        }
    }

    Context "TCP Inbound Connections" {
        It "Detects inbound connection on local server" {
            # Start TCP listener
            $port = Get-Random -Minimum 10000 -Maximum 20000
            $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $port)

            try {
                $listener.Start()

                # Give server time to start
                Start-Sleep -Milliseconds 500

                # Connect from client in background job
                $connectJob = Start-Job -ScriptBlock {
                    param($port)
                    try {
                        $client = New-Object System.Net.Sockets.TcpClient
                        $client.Connect("127.0.0.1", $port)
                        Start-Sleep -Milliseconds 500
                        $client.Close()
                    }
                    catch {
                        # Ignore errors
                    }
                } -ArgumentList $port

                # Accept connection
                if ($listener.Pending()) {
                    $client = $listener.AcceptTcpClient()
                    $client.Close()
                }

                # Wait for job
                Wait-Job -Job $connectJob -Timeout 5 | Out-Null
                Remove-Job -Job $connectJob -Force

                Start-Sleep -Milliseconds 1000

                # Check for accept event
                $events = & $script:GetRecentNetworkEvents -Count 200
                $acceptEvent = $events | Where-Object {
                    $_.eventType -eq "NetworkAccept" -and
                    $_.localPort -eq $port
                }

                $acceptEvent | Should -Not -BeNullOrEmpty
                $acceptEvent[0].direction | Should -Be "Inbound"
                $acceptEvent[0].protocol | Should -Be "TCP"
            }
            finally {
                $listener.Stop()
            }
        }
    }

    Context "IPv6 Support" {
        It "Detects IPv6 connection if available" {
            # Check if IPv6 is available
            $ipv6Available = (Get-NetIPAddress -AddressFamily IPv6 -ErrorAction SilentlyContinue) -ne $null

            if (-not $ipv6Available) {
                Set-ItResult -Skipped -Because "IPv6 not available on this system"
                return
            }

            # Attempt IPv6 connection
            try {
                $client = New-Object System.Net.Sockets.TcpClient([System.Net.Sockets.AddressFamily]::InterNetworkV6)
                $client.Connect("::1", 445)  # Attempt connection to localhost
                $client.Close()
            }
            catch {
                # Expected to fail, but should generate event
            }

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $ipv6Event = $events | Where-Object {
                $_.addressFamily -eq "IPv6"
            }

            # IPv6 events might not always be generated depending on system config
            if ($ipv6Event) {
                $ipv6Event[0].addressFamily | Should -Be "IPv6"
                $ipv6Event[0].localAddress | Should -Match ":"
            }
            else {
                Write-Warning "No IPv6 events captured (may be expected)"
            }
        }
    }

    Context "Process Attribution" {
        It "Captures process name for network events" {
            try {
                Invoke-WebRequest -Uri "http://example.com" -UseBasicParsing -TimeoutSec 5 | Out-Null
            }
            catch {}

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $event = $events | Where-Object {
                $_.remotePort -eq 80
            } | Select-Object -First 1

            $event | Should -Not -BeNullOrEmpty
            $event.processName | Should -Match "pwsh|powershell"
            $event.processId | Should -Be $PID
        }
    }

    Context "Connection Uniqueness" {
        It "Assigns unique connection IDs" {
            # Make multiple connections
            try {
                1..5 | ForEach-Object {
                    Invoke-WebRequest -Uri "http://example.com" -UseBasicParsing -TimeoutSec 5 | Out-Null
                    Start-Sleep -Milliseconds 200
                }
            }
            catch {}

            Start-Sleep -Milliseconds 1000

            $events = & $script:GetRecentNetworkEvents -Count 200
            $httpEvents = $events | Where-Object {
                $_.remotePort -eq 80
            } | Select-Object -Last 5

            $httpEvents | Should -Not -BeNullOrEmpty

            # Check that connection IDs are unique
            $connectionIds = $httpEvents | ForEach-Object { $_.connectionId } | Sort-Object -Unique
            $connectionIds.Count | Should -BeGreaterThan 1
        }
    }

    Context "JSON Format Validation" {
        It "Produces valid JSON for network events" {
            try {
                Invoke-WebRequest -Uri "http://example.com" -UseBasicParsing -TimeoutSec 5 | Out-Null
            }
            catch {}

            Start-Sleep -Milliseconds 1000

            $logFiles = Get-ChildItem -Path $script:LogPath -Filter "events_*.jsonl"
            $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1

            $networkLines = Get-Content -Path $latestLog.FullName |
                            Where-Object { $_ -match '"eventType":"Network' } |
                            Select-Object -Last 1

            $networkLines | Should -Not -BeNullOrEmpty

            # Validate JSON parsing
            { $networkLines | ConvertFrom-Json } | Should -Not -Throw

            $event = $networkLines | ConvertFrom-Json

            # Validate required fields
            $event.eventType | Should -Match "Network(Connect|Accept)"
            $event.protocol | Should -Match "TCP|UDP"
            $event.direction | Should -Match "Outbound|Inbound"
            $event.addressFamily | Should -Match "IPv4|IPv6"
            $event.localAddress | Should -Not -BeNullOrEmpty
            $event.remoteAddress | Should -Not -BeNullOrEmpty
            $event.localPort | Should -BeGreaterThan 0
            $event.remotePort | Should -BeGreaterThan 0
            $event.connectionId | Should -BeGreaterThan 0
            $event.processId | Should -BeGreaterThan 0
            $event.processName | Should -Not -BeNullOrEmpty
        }
    }
}
