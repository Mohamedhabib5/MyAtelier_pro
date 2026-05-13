$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "full_backup_$timestamp"
$destinationZip = "storage\backups\FULL_PRO_BACKUP_$timestamp.zip"

Write-Host "Starting full backup at $timestamp..."

# 1. Create staging directory
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# 2. Copy source code and config (excluding heavy/temp dirs)
Write-Host "Copying source files..."
robocopy . $backupDir /E /XD .git node_modules venv __pycache__ .pytest_cache .continue .vscode storage backups /NJH /NJS /NDL /NC /NS /NP | Out-Null

# 3. Copy attachments from storage
Write-Host "Copying attachments..."
if (Test-Path "storage\attachments") {
    robocopy storage\attachments "$backupDir\storage\attachments" /E /NJH /NJS /NDL /NC /NS /NP | Out-Null
}

# 4. Copy the DB dump we just made (find latest manual sql)
Write-Host "Including database dump..."
$latestDbDump = Get-ChildItem "storage\backups\db_backup_manual_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latestDbDump) {
    Copy-Item $latestDbDump.FullName -Destination "$backupDir\database_dump.sql"
}

# 5. Compress
Write-Host "Compressing to $destinationZip..."
Compress-Archive -Path "$backupDir\*" -DestinationPath $destinationZip -Force

# 6. Cleanup
Write-Host "Cleaning up staging directory..."
Remove-Item -Recurse -Force $backupDir

Write-Host "Backup completed successfully: $destinationZip"
