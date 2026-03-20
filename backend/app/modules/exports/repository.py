from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.exports.models import ExportSchedule


class ExportSchedulesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_schedules(self, company_id: str) -> list[ExportSchedule]:
        stmt = (
            select(ExportSchedule)
            .options(joinedload(ExportSchedule.branch))
            .where(ExportSchedule.company_id == company_id)
            .order_by(ExportSchedule.is_active.desc(), ExportSchedule.next_run_on.asc(), ExportSchedule.created_at.asc())
        )
        return list(self.db.scalars(stmt))

    def get_schedule(self, schedule_id: str) -> ExportSchedule | None:
        stmt = select(ExportSchedule).options(joinedload(ExportSchedule.branch)).where(ExportSchedule.id == schedule_id)
        return self.db.scalars(stmt).first()

    def add_schedule(self, schedule: ExportSchedule) -> ExportSchedule:
        self.db.add(schedule)
        return schedule
