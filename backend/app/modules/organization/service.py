from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.organization.models import Branch, Company, DocumentSequence, FiscalPeriod
from app.modules.organization.repository import OrganizationRepository
from app.modules.organization.schemas import BranchCreateRequest, UpdateCompanyRequest


DEFAULT_BRANCH_CODE = 'MAIN'


def ensure_organization_foundation(db: Session, default_company_name: str) -> Company:
    repo = OrganizationRepository(db)
    company = repo.get_primary_company()
    if company is not None:
        return company

    year = date.today().year
    company = Company(name=default_company_name, legal_name=default_company_name, default_currency='EGP')
    repo.add_company(company)
    db.flush()
    repo.add_branch(Branch(company_id=company.id, code=DEFAULT_BRANCH_CODE, name='Main Branch', is_default=True, is_active=True))
    repo.add_fiscal_period(FiscalPeriod(company_id=company.id, name=f'FY {year}', starts_on=date(year, 1, 1), ends_on=date(year, 12, 31), is_active=True, is_locked=False))
    repo.add_document_sequence(DocumentSequence(company_id=company.id, key='backup', prefix='BKP', next_number=1, padding=6))
    db.commit()
    return repo.get_primary_company() or company


def get_company_settings(db: Session) -> Company:
    repo = OrganizationRepository(db)
    company = repo.get_primary_company()
    return company if company is not None else ensure_organization_foundation(db, 'MyAtelier Pro')


def update_company_settings(db: Session, payload: UpdateCompanyRequest, actor_user_id: str | None) -> Company:
    repo = OrganizationRepository(db)
    company = repo.get_primary_company()
    if company is None:
        company = ensure_organization_foundation(db, payload.name)
    company.name = payload.name.strip()
    company.legal_name = payload.legal_name.strip() if payload.legal_name else None
    company.default_currency = payload.default_currency.upper()
    record_audit(db, actor_user_id=actor_user_id, action='company.updated', target_type='company', target_id=company.id, summary=f'Updated company settings for {company.name}', diff={'name': company.name, 'default_currency': company.default_currency})
    db.commit()
    return repo.get_primary_company() or company


def create_branch(db: Session, payload: BranchCreateRequest, actor_user_id: str | None) -> Branch:
    company = get_company_settings(db)
    repo = OrganizationRepository(db)
    code = norm_text(payload.code).upper()
    name = norm_text(payload.name)
    if repo.get_branch_by_code(company.id, code) is not None:
        raise ValidationAppError('كود الفرع مستخدم بالفعل')
    branch = Branch(company_id=company.id, code=code, name=name, is_default=False, is_active=True)
    repo.add_branch(branch)
    db.flush()
    record_audit(db, actor_user_id=actor_user_id, action='branch.created', target_type='branch', target_id=branch.id, summary=f'Created branch {branch.name}', diff={'code': branch.code})
    db.commit()
    db.refresh(branch)
    return branch
