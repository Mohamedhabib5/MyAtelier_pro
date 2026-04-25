param(
    [string]$TaskName = "MyAtelier-BackupStaleAlertCheck",
    [string]$BaseUrl = "http://localhost:8000",
    [string]$Username = "admin",
    [string]$Password = "admin123",
    [int]$IntervalMinutes = 60,
    [string]$RunAsUser = "",
    [string]$RunAsPassword = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "run-backup-stale-alert-check.ps1"
if (-not (Test-Path $scriptPath)) {
    throw "Missing runner script: $scriptPath"
}

$escapedScript = "`"$scriptPath`""
$arguments = "-NoProfile -ExecutionPolicy Bypass -File $escapedScript -BaseUrl `"$BaseUrl`" -Username `"$Username`" -Password `"$Password`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments

$repetition = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

if ([string]::IsNullOrWhiteSpace($RunAsUser)) {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $repetition -Settings $settings -Force | Out-Null
}
else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $repetition -Settings $settings -User $RunAsUser -Password $RunAsPassword -Force | Out-Null
}

Write-Host "Scheduled task registered successfully: $TaskName"
Write-Host "Runner: $scriptPath"
Write-Host "Interval minutes: $IntervalMinutes"
