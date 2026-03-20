from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


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