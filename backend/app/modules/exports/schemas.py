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
