from __future__ import annotations

import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from app.core.exceptions import ValidationAppError

BACKUP_DIR = Path("/app/backups")
STORAGE_DIR = Path("/app/storage")

class BackupMetadata(TypedDict):
    id: str
    filename: str
    size_bytes: int
    created_at: str
    kind: str  # 'db', 'media', 'full'

def ensure_backup_dir():
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def create_db_backup() -> BackupMetadata:
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"db_backup_{timestamp}.sql.gz"
    filepath = BACKUP_DIR / filename
    
    # Get DB credentials from env
    db_url = os.getenv("DATABASE_URL", "")
    # Parse URL: postgresql+psycopg://user:pass@host:port/dbname
    # We need to transform it for pg_dump
    try:
        # Simplistic parsing for standard Docker setup
        conn_str = db_url.replace("postgresql+psycopg://", "postgresql://")
        
        command = [
            "pg_dump",
            "--dbname", conn_str,
            "--no-owner",
            "--no-privileges",
            "--clean",
            "--if-exists"
        ]
        
        with open(filepath, "wb") as f:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Compress on the fly
            gzip_process = subprocess.Popen(["gzip"], stdin=process.stdout, stdout=f)
            process.stdout.close()
            _, stderr = process.communicate()
            gzip_process.communicate()
            
            if process.returncode != 0:
                if filepath.exists(): filepath.unlink()
                raise ValidationAppError(f"فشل إنشاء نسخة قاعدة البيانات: {stderr.decode()}")
                
    except Exception as e:
        if filepath.exists(): filepath.unlink()
        raise ValidationAppError(f"خطأ أثناء النسخ الاحتياطي: {str(e)}")
        
    return _get_metadata(filepath, "db")

def create_media_backup() -> BackupMetadata:
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"media_backup_{timestamp}.zip"
    filepath = BACKUP_DIR / filename
    
    if not STORAGE_DIR.exists():
        raise ValidationAppError("مجلد التخزين غير موجود")
        
    try:
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(STORAGE_DIR):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(file_path, file_path.relative_to(STORAGE_DIR))
    except Exception as e:
        if filepath.exists(): filepath.unlink()
        raise ValidationAppError(f"فشل أرشفة الملفات: {str(e)}")
        
    return _get_metadata(filepath, "media")

def create_full_backup() -> BackupMetadata:
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_backup_{timestamp}.zip"
    filepath = BACKUP_DIR / filename
    
    # 1. Create temp DB dump
    db_meta = create_db_backup()
    db_file = BACKUP_DIR / db_meta["filename"]
    
    try:
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add DB dump
            zipf.write(db_file, f"database/{db_file.name}")
            # Add Media
            for root, _, files in os.walk(STORAGE_DIR):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(file_path, f"storage/{file_path.relative_to(STORAGE_DIR)}")
    finally:
        # Cleanup temp DB file
        if db_file.exists(): db_file.unlink()
        
    return _get_metadata(filepath, "full")

def list_backups() -> list[BackupMetadata]:
    ensure_backup_dir()
    backups = []
    for p in BACKUP_DIR.glob("*_backup_*.*"):
        if p.is_file():
            kind = "db" if "db_" in p.name else "media" if "media_" in p.name else "full"
            backups.append(_get_metadata(p, kind))
    return sorted(backups, key=lambda x: x["created_at"], reverse=True)

def delete_backup(filename: str):
    filepath = BACKUP_DIR / filename
    if filepath.exists() and filepath.parent == BACKUP_DIR:
        filepath.unlink()
    else:
        raise ValidationAppError("الملف غير موجود")

def _get_metadata(path: Path, kind: str) -> BackupMetadata:
    stat = path.stat()
    return {
        "id": path.name,
        "filename": path.name,
        "size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "kind": kind
    }
