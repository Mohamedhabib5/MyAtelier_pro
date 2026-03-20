from __future__ import annotations

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
