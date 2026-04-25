from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BackupRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: str
    size_bytes: int
    notes: str | None
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    database_ok: bool
    migrations_ok: bool


class OpsMetricsResponse(BaseModel):
    generated_at: datetime
    backups_total: int
    backups_last_24h: int
    last_backup_at: datetime | None
    last_backup_age_hours: float | None
    backup_stale_threshold_hours: int
    backup_stale: bool
    audit_logs_total: int


class OpsAlertTestRequest(BaseModel):
    severity: str = Field(default="P2", min_length=2, max_length=20)
    message: str = Field(default="Test alert from MyAtelier ops endpoint.", min_length=3, max_length=500)
    dry_run: bool = True


class OpsAlertResponse(BaseModel):
    sent: bool
    channel: str
    detail: str


class OpsBackupAlertRunRequest(BaseModel):
    dry_run: bool = False
    force: bool = False
    trigger_source: Literal["manual", "automation"] = "manual"


class OpsBackupAlertRunResponse(BaseModel):
    stale: bool
    sent: bool
    severity: str
    detail: str
    backup_age_hours: float | None


class NightlyFailureReportRequest(BaseModel):
    event: str = Field(min_length=3, max_length=120)
    repository: str = Field(min_length=3, max_length=200)
    ref: str = Field(min_length=3, max_length=200)
    run_id: str = Field(min_length=1, max_length=120)
    run_attempt: str = Field(min_length=1, max_length=30)
    run_url: str = Field(min_length=5, max_length=500)
    results: dict[str, str] = Field(default_factory=dict)
    failed_at_utc: str = Field(min_length=10, max_length=60)


class NightlyFailureIngestResponse(BaseModel):
    accepted: bool
    run_id: str
    stored_at: datetime


class NightlyRunSnapshotResponse(BaseModel):
    available: bool
    event: str | None
    repository: str | None
    ref: str | None
    run_id: str | None
    run_attempt: str | None
    run_url: str | None
    failed_at_utc: str | None
    results: dict[str, str]
    reported_at: datetime | None


class DestructiveReasonResponse(BaseModel):
    code: str
    category: str
    label_ar: str
    label_en: str
    actions: list[str]


class DestructivePreviewRequest(BaseModel):
    entity_type: str = Field(min_length=3, max_length=50)
    entity_id: str = Field(min_length=3, max_length=64)
    reason_code: str | None = Field(default=None, max_length=100)
    reason_text: str | None = Field(default=None, max_length=500)


class DestructivePreviewResponse(BaseModel):
    entity_type: str
    entity_id: str
    entity_label: str
    recommended_action: str
    eligible_for_hard_delete: bool
    blockers: list[str]
    impact: dict[str, int]
    reason_code: str
    reason_text: str | None


class DestructiveDeleteRequest(BaseModel):
    entity_type: str = Field(min_length=3, max_length=50)
    entity_id: str = Field(min_length=3, max_length=64)
    reason_code: str | None = Field(default=None, max_length=100)
    reason_text: str | None = Field(default=None, max_length=500)
    override_lock: bool = False
    override_reason: str | None = Field(default=None, max_length=500)


class DestructiveDeleteResponse(BaseModel):
    entity_type: str
    entity_id: str
    entity_label: str
    deleted: bool
    reason_code: str
    reason_text: str | None
    impact: dict[str, int]


class PeriodLockResponse(BaseModel):
    locked_through: date | None
    updated_by_user_id: str | None
    updated_at: datetime | None
    is_locked: bool


class PeriodLockUpdateRequest(BaseModel):
    locked_through: date | None = None
    note: str | None = Field(default=None, max_length=500)


class PeriodLockExceptionResponse(BaseModel):
    audit_id: str
    occurred_at: datetime
    actor_user_id: str | None
    actor_name: str | None
    target_type: str
    target_id: str | None
    action_key: str | None
    action_date: str | None
    locked_through: str | None
    override_reason: str | None


class AuditEventResponse(BaseModel):
    id: str
    occurred_at: datetime
    actor_user_id: str | None
    actor_name: str | None
    action: str
    target_type: str
    target_id: str | None
    branch_id: str | None
    summary: str
    reason_code: str | None
    reason_text: str | None
    success: bool | None
    error_code: str | None
    diff: dict


class AuditEventPageResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    page: int
    page_size: int
