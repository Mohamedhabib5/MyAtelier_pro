#!/bin/bash
# ==============================================================================
# MyAtelier Pro - Automated Production Server Initialization Script
# Designed for Linux Server (Ubuntu/Debian) Deployment
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "================================================================="
echo " MyAtelier Pro - Automated Production Setup Wizard"
echo " Working Directory: $PROJECT_ROOT"
echo "================================================================="

# 1. Create storage directories with full permissions
echo "[1/4] Setting up storage directories..."
mkdir -p "$PROJECT_ROOT/storage/attachments"
mkdir -p "$PROJECT_ROOT/storage/backups"
chmod -R 777 "$PROJECT_ROOT/storage"
echo "   [✓] Storage directories created and permissions assigned."

# 2. Check and generate production SSL certificates if missing
CERT_DIR="$PROJECT_ROOT/infra/certs/live/app"
echo "[2/4] Checking SSL certificates in $CERT_DIR..."
mkdir -p "$CERT_DIR"
if [ ! -f "$CERT_DIR/fullchain.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo "   [!] SSL certificates missing. Generating temporary self-signed certificate for Nginx startup..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_DIR/privkey.pem" \
        -out "$CERT_DIR/fullchain.pem" \
        -subj "/CN=myatelier.local/O=MyAtelier Pro/C=EG"
    chmod 644 "$CERT_DIR/fullchain.pem"
    chmod 600 "$CERT_DIR/privkey.pem"
    echo "   [✓] Temporary SSL certificate generated successfully."
else
    echo "   [✓] Valid SSL certificate files found."
fi

# 3. Environment configuration (.env)
echo "[3/4] Checking production environment file (.env)..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "   [!] .env file not found. Launching environment wizard..."
    if command -v python3 >/dev/null 2>&1; then
        python3 "$PROJECT_ROOT/scripts/generate_prod_env.py"
    else
        echo "   [X] Python3 is required to generate .env file. Please install python3 or copy .env.prod manually."
        exit 1
    fi
else
    echo "   [✓] Existing .env file detected."
fi

# 4. Register automated daily DB backup into Crontab
echo "[4/4] Registering daily backup job in Crontab..."
BACKUP_SCRIPT="$PROJECT_ROOT/infra/scripts/prod-db-backup.sh"
chmod +x "$BACKUP_SCRIPT"

# Check if crontab entry already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "   [✓] Daily backup job is already registered in Crontab."
else
    (crontab -l 2>/dev/null; echo "0 2 * * * /bin/bash $BACKUP_SCRIPT >> $PROJECT_ROOT/storage/backups/backup.log 2>&1") | crontab -
    echo "   [✓] Registered daily backup job (02:00 AM) in Crontab."
fi

echo "================================================================="
echo " 🎉 PRODUCTION INITIALIZATION COMPLETED SUCCESSFULLY!"
echo "================================================================="
echo " Next step to start application:"
echo "   docker compose -f infra/docker-compose.prod.yml up -d --build"
echo "================================================================="
