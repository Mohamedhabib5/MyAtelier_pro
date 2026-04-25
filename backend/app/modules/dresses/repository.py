from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.dresses.models import DressResource


class DressesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_dresses(self, company_id: str, *, is_active: bool | None = None) -> list[DressResource]:
        stmt = select(DressResource).where(DressResource.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(DressResource.is_active == is_active)
        stmt = stmt.order_by(DressResource.code.asc())
        return list(self.db.scalars(stmt))

    def get_dress(self, dress_id: str) -> DressResource | None:
        return self.db.get(DressResource, dress_id)

    def get_dress_by_code(self, company_id: str, code: str) -> DressResource | None:
        stmt = select(DressResource).where(DressResource.company_id == company_id, DressResource.code == code)
        return self.db.scalars(stmt).first()

    def add_dress(self, dress: DressResource) -> DressResource:
        self.db.add(dress)
        return dress
