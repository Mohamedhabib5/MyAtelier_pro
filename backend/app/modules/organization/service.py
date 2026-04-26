from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.organization.models import Branch, Company, DocumentSequence, FiscalPeriod
from app.modules.organization.repository import OrganizationRepository
from app.modules.organization.schemas import (
    BranchCreateRequest,
    FiscalPeriodCreateRequest,
    FiscalPeriodUpdateRequest,
    UpdateCompanyRequest,
)


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
    if company is None:
        company = ensure_organization_foundation(db, 'MyAtelier Pro')
    
    # Always ensure there is at least one active fiscal period
    from app.modules.accounting.repository import AccountingRepository
    acc_repo = AccountingRepository(db)
    if not acc_repo.get_active_fiscal_period(company.id):
        year = date.today().year
        new_period = FiscalPeriod(
            company_id=company.id,
            name=f'FY {year}',
            starts_on=date(year, 1, 1),
            ends_on=date(year, 12, 31),
            is_active=True,
            is_locked=False
        )
        repo.add_fiscal_period(new_period)
        db.commit()
        
    return company


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


def list_fiscal_periods(db: Session) -> list[FiscalPeriod]:
    company = get_company_settings(db)
    repo = OrganizationRepository(db)
    return repo.list_fiscal_periods(company.id)


def create_fiscal_period(db: Session, payload: FiscalPeriodCreateRequest, actor_user_id: str | None) -> FiscalPeriod:
    company = get_company_settings(db)
    repo = OrganizationRepository(db)
    
    # Check for overlaps
    existing_periods = repo.list_fiscal_periods(company.id)
    for existing in existing_periods:
        # Overlap logic: (S1 <= E2) and (S2 <= E1)
        if payload.starts_on <= existing.ends_on and existing.starts_on <= payload.ends_on:
            raise ValidationAppError(f'تتداخل هذه الفترة مع فترة موجودة بالفعل: {existing.name}')

    period = FiscalPeriod(
        company_id=company.id,
        name=payload.name.strip(),
        starts_on=payload.starts_on,
        ends_on=payload.ends_on,
        is_active=True,
        is_locked=False
    )
    repo.add_fiscal_period(period)
    db.flush()
    record_audit(db, actor_user_id=actor_user_id, action='fiscal_period.created', target_type='fiscal_period', target_id=period.id, summary=f'Created fiscal period {period.name}', diff={'name': period.name, 'starts_on': str(payload.starts_on)})
    db.commit()
    db.refresh(period)
    return period


def update_fiscal_period(db: Session, period_id: str, payload: FiscalPeriodUpdateRequest, actor_user_id: str | None) -> FiscalPeriod:
    repo = OrganizationRepository(db)
    period = repo.get_fiscal_period(period_id)
    if period is None:
        raise ValidationAppError('لم يتم العثور على الفترة المالية')
    
    old_values = {'name': period.name, 'is_active': period.is_active, 'is_locked': period.is_locked}
    if payload.name is not None:
        period.name = payload.name.strip()
    if payload.is_active is not None:
        period.is_active = payload.is_active
    if payload.is_locked is not None:
        period.is_locked = payload.is_locked
    
    record_audit(db, actor_user_id=actor_user_id, action='fiscal_period.updated', target_type='fiscal_period', target_id=period.id, summary=f'Updated fiscal period {period.name}', diff=old_values)
    db.commit()
    db.refresh(period)
    return period


def delete_fiscal_period(db: Session, period_id: str, actor_user_id: str | None) -> None:
    repo = OrganizationRepository(db)
    period = repo.get_fiscal_period(period_id)
    if period is None:
        return
    
    # Optional: Prevent deletion of active periods if they have transactions (though repository might handle constraints)
    repo.delete_fiscal_period(period)
    record_audit(db, actor_user_id=actor_user_id, action='fiscal_period.deleted', target_type='fiscal_period', target_id=period_id, summary=f'Deleted fiscal period {period.name}')
    db.commit()
