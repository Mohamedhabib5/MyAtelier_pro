from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy.orm import Session

from app.core.enums import BackupStatus
from app.core.exceptions import NotFoundError
from app.modules.core_platform.backup_dump import create_database_dump
from app.modules.core_platform.models import AuditLog, BackupRecord
from app.modules.core_platform.repository import CorePlatformRepository


REQUIRED_FOUNDATION_TABLES = {
    "app_settings",
    "audit_logs",
    "backup_records",
    "companies",
    "branches",
    "fiscal_periods",
    "document_sequences",
    "users",
    "roles",
    "permissions",
    "role_permissions",
    "user_roles",
}


def record_audit(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    target_type: str,
    target_id: str | None,
    summary: str,
    diff: dict | None = None,
) -> AuditLog:
    repo = CorePlatformRepository(db)
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        diff_json=json.dumps(diff, ensure_ascii=False) if diff else None,
    )
    repo.add_audit_log(entry)
    return entry


def create_backup(
    db: Session,
    *,
    backup_dir: Path,
    attachment_dir: Path,
    database_url: str,
    created_by_user_id: str | None,
    company_name: str,
) -> BackupRecord:
    repo = CorePlatformRepository(db)
    backup_dir.mkdir(parents=True, exist_ok=True)
    attachment_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC)
    filename = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
    file_path = backup_dir / filename
    with TemporaryDirectory() as temp_dir:
        dump_path = Path(temp_dir) / 'database_dump.sql'
        dump_info = create_database_dump(database_url, dump_path)
        manifest = {
            "created_at": timestamp.isoformat(),
            "company_name": company_name,
            "format_version": 2,
            "database_dump": dump_info,
        }

        with ZipFile(file_path, mode="w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.write(dump_path, arcname=dump_info['path_in_archive'])
            for path in attachment_dir.rglob("*"):
                if path.is_file():
                    archive.write(path, arcname=Path("attachments") / path.relative_to(attachment_dir))

    backup_record = BackupRecord(
        created_by_user_id=created_by_user_id,
        filename=filename,
        file_path=str(file_path),
        status=BackupStatus.CREATED.value,
        size_bytes=file_path.stat().st_size,
        notes="Generated from settings backup panel",
    )
    repo.add_backup_record(backup_record)
    record_audit(
        db,
        actor_user_id=created_by_user_id,
        action="backup.created",
        target_type="backup_record",
        target_id=backup_record.id,
        summary=f"Created backup {filename}",
    )
    db.commit()
    db.refresh(backup_record)
    return backup_record


def resolve_backup_download_path(backup_dir: Path, backup_record: BackupRecord) -> Path:
    resolved_backup_dir = backup_dir.resolve()
    candidate = Path(backup_record.file_path).resolve()
    try:
        candidate.relative_to(resolved_backup_dir)
    except ValueError as exc:
        raise NotFoundError("لم يتم العثور على ملف النسخة الاحتياطية") from exc
    if not candidate.is_file():
        raise NotFoundError("لم يتم العثور على ملف النسخة الاحتياطية")
    return candidate


def record_backup_download(db: Session, *, actor_user_id: str, backup_record: BackupRecord) -> None:
    record_audit(
        db,
        actor_user_id=actor_user_id,
        action="backup.downloaded",
        target_type="backup_record",
        target_id=backup_record.id,
        summary=f"Downloaded backup {backup_record.filename}",
    )
    db.commit()


def list_backups(db: Session) -> list[BackupRecord]:
    return CorePlatformRepository(db).list_backup_records()


def get_backup_or_404(db: Session, backup_id: str) -> BackupRecord:
    record = CorePlatformRepository(db).get_backup_record(backup_id)
    if record is None:
        raise NotFoundError("لم يتم العثور على سجل النسخة الاحتياطية")
    return record
