#!/bin/bash
# MyAtelier Pro - Automated Backup Script
# Place this script in /usr/local/bin/ and add to crontab:
# 0 2 * * * /usr/local/bin/backup-myatelier.sh

# Configuration
BACKUP_DIR="/path/to/your/backups/db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30
CONTAINER_NAME="myatelier-db" # Match docker-compose service name
DB_NAME="myatelier_pro"
DB_USER="beauty_admin"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup for $DB_NAME..."

# Perform backup using docker exec
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Cleanup old backups
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
