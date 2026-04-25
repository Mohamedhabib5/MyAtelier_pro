param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$Username = "admin",
    [string]$Password = "admin123",
    [bool]$DryRun = $false,
    [int]$Limit = 50
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

try {
    $loginBody = @{
        username = $Username
        password = $Password
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -WebSession $session -Body $loginBody -ContentType "application/json" | Out-Null

    $payload = @{
        dry_run = $DryRun
        limit = $Limit
        trigger_source = "automation"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/exports/schedules/run-due" -WebSession $session -Body $payload -ContentType "application/json"
    Write-Host "Run due export schedules result: $($result | ConvertTo-Json -Compress)"

    if ($DryRun) {
        exit 0
    }

    if ($result.executed_count -lt 0) {
        Write-Error "Invalid executed count in response."
        exit 2
    }

    exit 0
}
catch {
    Write-Error "Failed to run due export schedules: $_"
    exit 1
}
finally {
    try {
        Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/logout" -WebSession $session | Out-Null
    }
    catch {
        # Ignore logout failures in cleanup.
    }
}
