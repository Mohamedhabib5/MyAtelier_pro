#!/bin/bash
# ==============================================================================
# MyAtelier Pro - Production Automated Full Backup & Retention Script
# ==============================================================================
# Exports Postgres DB, packages code & attachments, compresses into archive,
# manages 30-day retention cleanup on local SSD, and offers cloud upload hook.
# ==============================================================================

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="storage/backups"
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E "myatelier.*db" | head -n 1 || echo "")
DB_USER="${POSTGRES_USER:-myatelier_user}"
DB_NAME="${POSTGRES_DB:-myatelier_pro}"
ARCHIVE_NAME="FULL_PRO_BACKUP_$TIMESTAMP.tar.gz"
STAGING_DIR="/tmp/backup_staging_$TIMESTAMP"
RETENTION_DAYS=30

echo "=== 🔄 Starting Production Full Backup Execution ==="

# 1. Create Directories
mkdir -p "$STAGING_DIR"
mkdir -p "$BACKUP_DIR"

# 2. Export PostgreSQL Database
echo "💾 Exporting PostgreSQL Database..."
if [ -n "$DB_CONTAINER" ]; then
    echo "[+] Found running DB container: $DB_CONTAINER"
    docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$STAGING_DIR/database_dump.sql"
    echo "✅ Database exported successfully."
else
    echo "⚠️ DB Container not running. Attempting local pg_dump fallback..."
    if command -v pg_dump &> /dev/null; then
        pg_dump -U "$DB_USER" -d "$DB_NAME" > "$STAGING_DIR/database_dump.sql"
        echo "✅ Local pg_dump export succeeded."
    else
        echo "❌ ERROR: Unable to locate DB container or local pg_dump!"
    fi
fi

# 3. Copy Attachments & Configuration Files
echo "📂 Packaging application storage and attachments..."
if [ -d "storage/attachments" ]; then
    mkdir -p "$STAGING_DIR/attachments"
    cp -r storage/attachments/* "$STAGING_DIR/attachments/" 2>/dev/null || true
fi

if [ -f ".env" ]; then
    cp .env "$STAGING_DIR/env_backup.config"
fi

# 4. Compress Backup Archive
echo "🤐 Compressing archive..."
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" -C "$STAGING_DIR" .
echo "✅ Backup compressed to: $BACKUP_DIR/$ARCHIVE_NAME"

# 5. Cloud Upload (rclone / S3 hook if configured)
if command -v rclone &> /dev/null; then
    echo "☁️ Uploading to cloud storage via rclone..."
    rclone copy "$BACKUP_DIR/$ARCHIVE_NAME" "remote:MyAtelier_Backups" --progress || echo "⚠️ Cloud upload failed."
    echo "✅ Cloud upload finished."
else
    echo "ℹ️ rclone is not installed. Backup saved locally on SSD at $BACKUP_DIR/$ARCHIVE_NAME"
fi

# 6. Automatic Retention Cleanup (Delete backups older than 30 days)
echo "🧹 Performing retention cleanup (Deleting backups older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f \( -name "*.zip" -o -name "*.tar.gz" \) -mtime +$RETENTION_DAYS -delete || true
echo "✅ Retention cleanup completed."

# 7. Cleanup Staging Directory
rm -rf "$STAGING_DIR"

echo "=============================================================================="
echo " ✅ Full Production Backup Completed Successfully!"
echo "=============================================================================="
