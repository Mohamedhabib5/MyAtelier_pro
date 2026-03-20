from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_accounting_manage, require_accounting_view
from app.db.session import get_db
from app.modules.accounting.journal_service import (
    create_draft_journal_entry,
    get_journal_entry,
    list_journal_entries,
    post_journal_entry,
    reverse_journal_entry,
    update_draft_journal_entry,
)
from app.modules.accounting.schemas import (
    ChartAccountResponse,
    JournalEntryCreateRequest,
    JournalEntryResponse,
    JournalEntryReverseRequest,
    JournalEntryUpdateRequest,
    TrialBalanceResponse,
)
from app.modules.accounting.service import list_chart_accounts
from app.modules.accounting.trial_balance_service import build_trial_balance
from app.modules.identity.models import User

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/chart-of-accounts", response_model=list[ChartAccountResponse])
def get_chart_of_accounts(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> list[ChartAccountResponse]:
    return [ChartAccountResponse.model_validate(item) for item in list_chart_accounts(db)]


@router.get("/journal-entries", response_model=list[JournalEntryResponse])
def get_journal_entries(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> list[JournalEntryResponse]:
    return [JournalEntryResponse.model_validate(item) for item in list_journal_entries(db)]


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry_route(
    entry_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(get_journal_entry(db, entry_id))


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry_route(
    payload: JournalEntryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(create_draft_journal_entry(db, current_user, payload))


@router.patch("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
def update_journal_entry_route(
    entry_id: str,
    payload: JournalEntryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(update_draft_journal_entry(db, current_user, entry_id, payload))


@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
def post_journal_entry_route(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(post_journal_entry(db, current_user, entry_id))


@router.post("/journal-entries/{entry_id}/reverse", response_model=JournalEntryResponse)
def reverse_journal_entry_route(
    entry_id: str,
    payload: JournalEntryReverseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(reverse_journal_entry(db, current_user, entry_id, payload))


@router.get("/trial-balance", response_model=TrialBalanceResponse)
def get_trial_balance(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
    as_of_date: date | None = Query(default=None),
    fiscal_period_id: str | None = Query(default=None),
    include_zero_accounts: bool = Query(default=False),
) -> TrialBalanceResponse:
    return TrialBalanceResponse.model_validate(
        build_trial_balance(
            db,
            as_of_date=as_of_date,
            fiscal_period_id=fiscal_period_id,
            include_zero_accounts=include_zero_accounts,
        )
    )
