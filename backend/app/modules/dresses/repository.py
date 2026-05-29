from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.modules.dresses.models import DressResource


class DressesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_dresses(self, company_id: str, *, is_active: bool | None = None) -> list[DressResource]:
        stmt = select(DressResource).options(joinedload(DressResource.dress_type)).where(DressResource.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(DressResource.is_active == is_active)
        stmt = stmt.order_by(DressResource.code.asc())
        return list(self.db.scalars(stmt))

    def count_dresses(self, company_id: str, *, is_active: bool | None = None, status: str | None = None) -> int:
        stmt = select(func.count(DressResource.id)).where(DressResource.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(DressResource.is_active == is_active)
        if status is not None:
            stmt = stmt.where(DressResource.status == status)
        return self.db.scalar(stmt) or 0

    def get_dress_status_counts(self, company_id: str) -> list[dict]:
        stmt = (
            select(DressResource.status.label('key'), func.count(DressResource.id).label('count'))
            .where(DressResource.company_id == company_id)
            .group_by(DressResource.status)
            .order_by(func.count(DressResource.id).desc())
        )
        results = self.db.execute(stmt).all()
        return [{'key': r.key, 'count': r.count} for r in results]

    def get_dress(self, dress_id: str) -> DressResource | None:
        stmt = select(DressResource).options(joinedload(DressResource.dress_type)).where(DressResource.id == dress_id)
        return self.db.scalars(stmt).first()

    def get_dress_by_code(self, company_id: str, code: str) -> DressResource | None:
        stmt = select(DressResource).options(joinedload(DressResource.dress_type)).where(DressResource.company_id == company_id, DressResource.code == code)
        return self.db.scalars(stmt).first()

    def add_dress(self, dress: DressResource) -> DressResource:
        self.db.add(dress)
        return dress
