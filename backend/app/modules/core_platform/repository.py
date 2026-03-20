from __future__ import annotations

from sqlalchemy import select
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