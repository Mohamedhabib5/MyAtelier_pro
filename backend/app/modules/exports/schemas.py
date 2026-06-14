from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExportScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    export_type: str
    cadence: str
    branch_id: str | None
    branch_name: str | None
    next_run_on: str
    last_run_at: str | None
    is_active: bool


class ExportScheduleCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    export_type: str = Field(min_length=3, max_length=40)
    cadence: str = Field(min_length=3, max_length=20)
    start_on: str | None = None


class ExportScheduleRunResponse(BaseModel):
    schedule: ExportScheduleResponse
    run_url: str


class ExportScheduleToggleResponse(BaseModel):
    schedule: ExportScheduleResponse


class ExportScheduleRunDueRequest(BaseModel):
    dry_run: bool = False
    limit: int = Field(default=50, ge=1, le=500)
    notify: bool = False
    delivery_dry_run: bool = True
    trigger_source: Literal["manual", "automation"] = "manual"


class ExportScheduleRunDueItem(BaseModel):
    schedule_id: str
    schedule_name: str
    run_url: str
    executed: bool


class ExportScheduleRunDueResponse(BaseModel):
    total_due: int
    executed_count: int
    skipped_count: int
    delivery_sent: bool
    delivery_detail: str
    runs: list[ExportScheduleRunDueItem]


class DailyEmailReportConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    name: str
    sender_email: str
    sender_password: str
    smtp_server: str
    smtp_port: int
    recipient_email: str
    send_hour: int
    is_active: bool

    send_daily_summary: bool
    notify_booking_created: bool
    notify_booking_modified: bool
    notify_payment_captured: bool
    notify_payment_refunded: bool
    notify_entity_deleted: bool
    notify_operations_daily: bool
    notify_financial_critical: bool
    notify_backup_warnings: bool
    booking_email_template: str
    payment_email_template: str


class DailyEmailReportConfigCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    sender_email: str = Field(min_length=5, max_length=120)
    sender_password: str = Field(min_length=1, max_length=255)
    smtp_server: str = Field(default='smtp.gmail.com', max_length=120)
    smtp_port: int = Field(default=587, ge=1, le=65535)
    recipient_email: str = Field(min_length=5, max_length=255)
    send_hour: int = Field(default=21, ge=0, le=23)
    is_active: bool = True

    send_daily_summary: bool = True
    notify_booking_created: bool = False
    notify_booking_modified: bool = False
    notify_payment_captured: bool = False
    notify_payment_refunded: bool = False
    notify_entity_deleted: bool = True
    notify_operations_daily: bool = True
    notify_financial_critical: bool = True
    notify_backup_warnings: bool = True
    booking_email_template: str = Field(default='detailed', max_length=40)
    payment_email_template: str = Field(default='detailed', max_length=40)


class DailyEmailReportConfigUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    sender_email: str | None = Field(default=None, min_length=5, max_length=120)
    sender_password: str | None = Field(default=None, min_length=1, max_length=255)
    smtp_server: str | None = Field(default=None, max_length=120)
    smtp_port: int | None = Field(default=None, ge=1, le=65535)
    recipient_email: str | None = Field(default=None, min_length=5, max_length=255)
    send_hour: int | None = Field(default=None, ge=0, le=23)
    is_active: bool | None = None

    send_daily_summary: bool | None = None
    notify_booking_created: bool | None = None
    notify_booking_modified: bool | None = None
    notify_payment_captured: bool | None = None
    notify_payment_refunded: bool | None = None
    notify_entity_deleted: bool | None = None
    notify_operations_daily: bool | None = None
    notify_financial_critical: bool | None = None
    notify_backup_warnings: bool | None = None
    booking_email_template: str | None = Field(default=None, max_length=40)
    payment_email_template: str | None = Field(default=None, max_length=40)
