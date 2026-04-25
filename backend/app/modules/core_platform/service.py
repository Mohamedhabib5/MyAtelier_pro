from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy.orm import Session

from app.core.enums import BackupStatus
from app.core.exceptions import NotFoundError
from app.modules.core_platform.destructive_reasons import list_destructive_reasons as list_destructive_reason_rows
from app.modules.core_platform.backup_dump import create_database_dump
from app.modules.core_platform.audit import record_audit
from app.modules.core_platform.models import BackupRecord
from app.modules.core_platform.repository import CorePlatformRepository

logger = logging.getLogger(__name__)

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
        dump_path = Path(temp_dir) / "database_dump.sql"
        dump_info = create_database_dump(database_url, dump_path)
        manifest = {
            "created_at": timestamp.isoformat(),
            "company_name": company_name,
            "format_version": 2,
            "database_dump": dump_info,
        }

        with ZipFile(file_path, mode="w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            archive.write(dump_path, arcname=dump_info["path_in_archive"])
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


def list_destructive_reasons(action: str | None = None) -> list[dict]:
    return list_destructive_reason_rows(action)


def collect_ops_metrics(db: Session, *, backup_stale_threshold_hours: int) -> dict:
    repo = CorePlatformRepository(db)
    now = datetime.now(UTC)
    window_start = now - timedelta(hours=24)
    latest_backup = repo.latest_backup_record()
    last_backup_age_hours: float | None = None
    if latest_backup is not None:
        last_backup_at = latest_backup.created_at
        if last_backup_at.tzinfo is None:
            last_backup_at = last_backup_at.replace(tzinfo=UTC)
        delta = now - last_backup_at
        last_backup_age_hours = round(delta.total_seconds() / 3600, 2)
    return {
        "generated_at": now,
        "backups_total": repo.count_backup_records(),
        "backups_last_24h": repo.count_backup_records_since(window_start),
        "last_backup_at": latest_backup.created_at if latest_backup else None,
        "last_backup_age_hours": last_backup_age_hours,
        "backup_stale_threshold_hours": backup_stale_threshold_hours,
        "backup_stale": (last_backup_age_hours is None) or (last_backup_age_hours > backup_stale_threshold_hours),
        "audit_logs_total": repo.count_audit_logs(),
    }


def send_ops_webhook_alert(
    *,
    webhook_url: str,
    severity: str,
    message: str,
    dry_run: bool = True,
) -> tuple[bool, str]:
    cleaned_url = webhook_url.strip()
    if dry_run:
        return False, "Dry-run mode: request not sent."
    if not cleaned_url:
        return False, "Webhook URL not configured."

    payload = json.dumps(
        {
            "source": "myatelier_pro",
            "severity": severity,
            "message": message,
            "sent_at": datetime.now(UTC).isoformat(),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(cleaned_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=5) as response:
            status = getattr(response, "status", 200)
            if 200 <= status < 300:
                return True, f"Sent successfully with status {status}."
            return False, f"Webhook responded with status {status}."
    except URLError as exc:
        logger.warning("Ops webhook alert failed: %s", exc)
        reason = exc.reason if hasattr(exc, "reason") else str(exc)
        return False, f"Webhook request failed: {reason}"


def run_backup_stale_alert_check(
    db: Session,
    *,
    backup_stale_threshold_hours: int,
    webhook_url: str,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    metrics = collect_ops_metrics(db, backup_stale_threshold_hours=backup_stale_threshold_hours)
    stale = bool(metrics["backup_stale"])
    should_alert = stale or force
    severity = "P1" if stale else "P2"
    backup_age_hours = metrics["last_backup_age_hours"]

    if not should_alert:
        return {
            "stale": stale,
            "sent": False,
            "severity": severity,
            "detail": "No alert needed: latest backup is within threshold.",
            "backup_age_hours": backup_age_hours,
        }

    message = (
        f"Backup stale check triggered: stale={stale}, "
        f"age_hours={backup_age_hours}, threshold_hours={backup_stale_threshold_hours}."
    )
    sent, detail = send_ops_webhook_alert(
        webhook_url=webhook_url,
        severity=severity,
        message=message,
        dry_run=dry_run,
    )
    return {
        "stale": stale,
        "sent": sent,
        "severity": severity,
        "detail": detail,
        "backup_age_hours": backup_age_hours,
    }
