param(
    [string]$BackupDir = "..\..\storage\backups",
    [int]$DailyDays = 14,
    [int]$WeeklyWeeks = 8,
    [int]$MonthlyMonths = 12
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedDir = Resolve-Path $BackupDir
$files = Get-ChildItem -Path $resolvedDir -File -Filter "*.zip" | Sort-Object LastWriteTime

if ($files.Count -le 1) {
    Write-Host "Skipping retention cleanup: only one or zero backup files found."
    exit 0
}

$now = Get-Date
$dailyCutoff = $now.AddDays(-$DailyDays)
$weeklyCutoff = $now.AddDays(-7 * $WeeklyWeeks)
$monthlyCutoff = $now.AddMonths(-$MonthlyMonths)

$keep = New-Object System.Collections.Generic.HashSet[string]

# Keep all recent daily backups.
foreach ($file in $files) {
    if ($file.LastWriteTime -ge $dailyCutoff) {
        [void]$keep.Add($file.FullName)
    }
}

# Keep one backup per ISO week in weekly window.
$weeklyCandidates = $files | Where-Object { $_.LastWriteTime -lt $dailyCutoff -and $_.LastWriteTime -ge $weeklyCutoff }
$weeklyGroups = $weeklyCandidates | Group-Object { "{0:yyyy}-{1:d2}" -f $_.LastWriteTime.Year, [System.Globalization.CultureInfo]::InvariantCulture.Calendar.GetWeekOfYear($_.LastWriteTime, [System.Globalization.CalendarWeekRule]::FirstFourDayWeek, [DayOfWeek]::Monday) }
foreach ($group in $weeklyGroups) {
    $latest = $group.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    [void]$keep.Add($latest.FullName)
}

# Keep one backup per month in monthly window.
$monthlyCandidates = $files | Where-Object { $_.LastWriteTime -lt $weeklyCutoff -and $_.LastWriteTime -ge $monthlyCutoff }
$monthlyGroups = $monthlyCandidates | Group-Object { "{0:yyyy-MM}" -f $_.LastWriteTime }
foreach ($group in $monthlyGroups) {
    $latest = $group.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    [void]$keep.Add($latest.FullName)
}

# Always keep latest backup as safety guard.
$latestOverall = $files | Select-Object -Last 1
[void]$keep.Add($latestOverall.FullName)

$toDelete = $files | Where-Object { -not $keep.Contains($_.FullName) }
foreach ($file in $toDelete) {
    Write-Host "Deleting old backup: $($file.FullName)"
    Remove-Item -Path $file.FullName -Force
}

Write-Host "Retention cleanup complete. Kept $($keep.Count) backup file(s), deleted $($toDelete.Count)."
