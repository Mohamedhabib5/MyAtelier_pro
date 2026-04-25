param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$Username = "admin",
    [string]$Password = "admin123",
    [bool]$DryRun = $false,
    [bool]$Force = $false
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
        force = $Force
        trigger_source = "automation"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/settings/ops/alerts/run-backup-check" -WebSession $session -Body $payload -ContentType "application/json"
    Write-Host "Backup stale check result: $($result | ConvertTo-Json -Compress)"

    if (-not $result.stale -and -not $result.sent) {
        exit 0
    }

    if ($result.stale -and -not $result.sent -and -not $DryRun) {
        Write-Error "Stale backup detected but alert was not sent."
        exit 2
    }

    exit 0
}
catch {
    Write-Error "Failed to run backup stale alert check: $_"
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
