from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import or_
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.core_platform.models import AppSetting, AuditLog, BackupRecord


class CorePlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> AppSetting | None:
        return self.db.get(AppSetting, key)

    def set_setting(self, key: str, value: str) -> AppSetting:
        setting = self.db.get(AppSetting, key)
        if setting is None:
            setting = AppSetting(key=key, value=value)
            self.db.add(setting)
        else:
            setting.value = value
        return setting

    def add_audit_log(self, entry: AuditLog) -> AuditLog:
        self.db.add(entry)
        return entry

    def add_backup_record(self, entry: BackupRecord) -> BackupRecord:
        self.db.add(entry)
        return entry

    def list_backup_records(self) -> list[BackupRecord]:
        return list(self.db.scalars(select(BackupRecord).order_by(BackupRecord.created_at.desc())))

    def get_backup_record(self, backup_id: str) -> BackupRecord | None:
        return self.db.get(BackupRecord, backup_id)

    def count_backup_records(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(BackupRecord)) or 0)

    def count_backup_records_since(self, since: datetime) -> int:
        return int(self.db.scalar(select(func.count()).select_from(BackupRecord).where(BackupRecord.created_at >= since)) or 0)

    def latest_backup_record(self) -> BackupRecord | None:
        return self.db.scalar(select(BackupRecord).order_by(BackupRecord.created_at.desc()).limit(1))

    def count_audit_logs(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(AuditLog)) or 0)

    def list_audit_events_page(
        self,
        *,
        actions: Sequence[str] | None = None,
        actor_user_id: str | None = None,
        action: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        branch_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLog)
        if actions:
            stmt = stmt.where(AuditLog.action.in_(list(actions)))
        if actor_user_id:
            stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if target_type:
            stmt = stmt.where(AuditLog.target_type == target_type)
        if target_id:
            stmt = stmt.where(AuditLog.target_id == target_id)
        if branch_id:
            stmt = stmt.where(AuditLog.branch_id == branch_id)
        if date_from:
            stmt = stmt.where(AuditLog.occurred_at >= date_from)
        if date_to:
            stmt = stmt.where(AuditLog.occurred_at <= date_to)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    AuditLog.action.ilike(pattern),
                    AuditLog.target_type.ilike(pattern),
                    AuditLog.target_id.ilike(pattern),
                    AuditLog.summary.ilike(pattern),
                )
            )
        total = int(self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
        rows = list(
            self.db.scalars(
                stmt.order_by(AuditLog.occurred_at.desc(), AuditLog.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return rows, total
