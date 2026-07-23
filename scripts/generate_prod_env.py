#!/usr/bin/env python3
"""
MyAtelier Pro - Interactive & Automated Production Environment Setup (.env Generator)
Generates a fully valid, highly secure .env file compliant with runtime security rules.
"""

import secrets
import sys
from pathlib import Path


def generate_secure_secret(length: int = 48) -> str:
    return secrets.token_hex(length // 2)


def main() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    target_env = root_dir / ".env"
    prod_template_env = root_dir / ".env.prod"

    print("=================================================================")
    print(" MyAtelier Pro - Production Environment (.env) Setup Wizard")
    print("=================================================================")

    if target_env.exists():
        backup_path = target_env.with_name(".env.backup")
        target_env.rename(backup_path)
        print(f"[!] Existing .env file backed up to: {backup_path.name}")

    domain = input("Enter your public Domain or IP (e.g. atelier.company.com or 192.168.1.100) [localhost]: ").strip() or "localhost"
    proto = "https" if domain != "localhost" else "http"

    app_secret_key = generate_secure_secret(64)
    db_password = generate_secure_secret(32)
    redis_password = generate_secure_secret(32)
    admin_password = input("Enter admin password (min 10 chars) [or press Enter to auto-generate]: ").strip()
    if not admin_password or len(admin_password) < 10:
        admin_password = generate_secure_secret(16)
        print(f"[+] Auto-generated Admin Password: {admin_password}")

    frontend_origins = f"{proto}://{domain}" if domain != "localhost" else "http://localhost:5173"
    allowed_hosts = f"{domain},backend,nginx,localhost,127.0.0.1"

    env_content = f"""# ==============================================================================
# MyAtelier Pro - Production Environment Configuration
# Auto-generated on setup
# ==============================================================================

APP_NAME="MyAtelier Pro"
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY={app_secret_key}
CSRF_SECRET_KEY={generate_secure_secret(64)}

# Database Credentials
POSTGRES_DB=myatelier_pro
POSTGRES_USER=myatelier_user
POSTGRES_PASSWORD={db_password}

# Redis Credentials
REDIS_PASSWORD={redis_password}
REDIS_URL=redis://:{redis_password}@redis:6379/0

# Default Admin User
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD={admin_password}
DEFAULT_COMPANY_NAME="MyAtelier Pro"

# Session & Security Settings
SESSION_COOKIE_NAME=myatelier_pro_session
SESSION_SAME_SITE=lax
SESSION_HTTPS_ONLY={"true" if proto == "https" else "false"}
SESSION_MAX_AGE_SECONDS=43200

# CORS & Trusted Hosts Restrictions
APP_FRONTEND_ORIGIN={frontend_origins}
APP_FRONTEND_ORIGINS={frontend_origins}
ALLOWED_HOSTS={allowed_hosts}

# File Upload Limits
MAX_IMAGE_SIZE_BYTES=307200

# Storage Directories
STORAGE_ROOT=./storage
BACKUP_STORAGE_DIR=./storage/backups
ATTACHMENT_STORAGE_DIR=./storage/attachments
"""

    with open(target_env, "w", encoding="utf-8") as f:
        f.write(env_content)

    with open(prod_template_env, "w", encoding="utf-8") as f:
        f.write(env_content)

    print(f"\n[+] Success! Production .env file created at: {target_env}")
    print("=================================================================")
    print(" SUMMARY OF CREATED CREDENTIALS:")
    print(f" - Admin Username: admin")
    print(f" - Admin Password: {admin_password}")
    print(f" - Postgres User:  myatelier_user")
    print(f" - Postgres Pass:  {db_password}")
    print("=================================================================")


if __name__ == "__main__":
    main()
