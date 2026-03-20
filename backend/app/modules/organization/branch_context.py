from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.organization.models import Branch
from app.modules.organization.repository import OrganizationRepository
from app.modules.organization.service import get_company_settings

SESSION_BRANCH_KEY = 'active_branch_id'


def ensure_active_branch(db: Session, session: MutableMapping[str, Any]) -> Branch:
    company = get_company_settings(db)
    repository = OrganizationRepository(db)
    branch = repository.get_branch(session.get(SESSION_BRANCH_KEY))
    if branch and branch.company_id == company.id and branch.is_active:
        return branch
    default_branch = repository.get_default_branch(company.id)
    if default_branch is None or not default_branch.is_active:
        raise NotFoundError('لا يوجد فرع نشط متاح')
    session[SESSION_BRANCH_KEY] = default_branch.id
    return default_branch


def resolve_branch_scope(db: Session, session: MutableMapping[str, Any], branch_id: str | None) -> Branch:
    if not branch_id:
        return ensure_active_branch(db, session)
    company = get_company_settings(db)
    repository = OrganizationRepository(db)
    branch = repository.get_branch(branch_id)
    if branch is None or branch.company_id != company.id:
        raise NotFoundError('لم يتم العثور على الفرع')
    if not branch.is_active:
        raise ValidationAppError('لا يمكن اختيار فرع موقوف')
    return branch


def set_active_branch(db: Session, session: MutableMapping[str, Any], branch_id: str) -> Branch:
    branch = resolve_branch_scope(db, session, branch_id)
    session[SESSION_BRANCH_KEY] = branch.id
    return branch
