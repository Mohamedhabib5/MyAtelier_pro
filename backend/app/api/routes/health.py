from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import inspect, text

from app.modules.core_platform.schemas import HealthResponse
from app.modules.core_platform.service import REQUIRED_FOUNDATION_TABLES

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    engine = request.app.state.engine
    database_ok = False
    migrations_ok = False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database_ok = True
        inspector = inspect(engine)
        migrations_ok = REQUIRED_FOUNDATION_TABLES.issubset(set(inspector.get_table_names()))
    except Exception:
        database_ok = False
        migrations_ok = False
    return HealthResponse(status="ok", database_ok=database_ok, migrations_ok=migrations_ok)