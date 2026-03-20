from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.organization.models import Branch, Company, DocumentSequence, FiscalPeriod


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_primary_company(self) -> Company | None:
        stmt = select(Company).options(selectinload(Company.branches)).order_by(Company.created_at.asc())
        return self.db.scalars(stmt).first()

    def get_branch(self, branch_id: str | None) -> Branch | None:
        if not branch_id:
            return None
        return self.db.get(Branch, branch_id)

    def get_branch_by_code(self, company_id: str, code: str) -> Branch | None:
        stmt = select(Branch).where(Branch.company_id == company_id, Branch.code == code)
        return self.db.scalars(stmt).first()

    def list_branches(self, company_id: str) -> list[Branch]:
        stmt = select(Branch).where(Branch.company_id == company_id).order_by(Branch.is_default.desc(), Branch.name.asc())
        return list(self.db.scalars(stmt))

    def get_default_branch(self, company_id: str) -> Branch | None:
        stmt = select(Branch).where(Branch.company_id == company_id, Branch.is_default.is_(True)).order_by(Branch.created_at.asc())
        return self.db.scalars(stmt).first()

    def add_company(self, company: Company) -> Company:
        self.db.add(company)
        return company

    def add_branch(self, branch: Branch) -> Branch:
        self.db.add(branch)
        return branch

    def add_fiscal_period(self, fiscal_period: FiscalPeriod) -> FiscalPeriod:
        self.db.add(fiscal_period)
        return fiscal_period

    def add_document_sequence(self, sequence: DocumentSequence) -> DocumentSequence:
        self.db.add(sequence)
        return sequence
