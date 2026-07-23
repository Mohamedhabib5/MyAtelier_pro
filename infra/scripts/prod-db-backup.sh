#!/bin/bash
# MyAtelier Pro - Automated Production Backup Script
# Place this script in /usr/local/bin/ and add to crontab:
# 0 2 * * * /path/to/MyAtelier_pro/infra/scripts/prod-db-backup.sh

set -e

# Base directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/storage/backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=${RETENTION_DAYS:-7}

DB_NAME="${POSTGRES_DB:-myatelier_pro}"
DB_USER="${POSTGRES_USER:-beauty_admin}"

mkdir -p "$BACKUP_DIR"

echo "Starting automated database backup for $DB_NAME..."

# Execute dump directly via docker compose
cd "$PROJECT_ROOT"
docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Compress backup file
gzip -f "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Apply retention policy: remove files older than RETENTION_DAYS
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup successfully completed: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
