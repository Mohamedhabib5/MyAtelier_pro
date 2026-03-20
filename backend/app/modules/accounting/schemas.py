from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ChartAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    code: str
    name: str
    account_type: str
    parent_account_id: str | None
    allows_posting: bool
    is_active: bool


class JournalEntryLineWriteRequest(BaseModel):
    account_id: str
    description: str | None = Field(default=None, max_length=255)
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class JournalEntryCreateRequest(BaseModel):
    fiscal_period_id: str | None = None
    entry_date: date
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    lines: list[JournalEntryLineWriteRequest] = Field(min_length=2)


class JournalEntryUpdateRequest(BaseModel):
    fiscal_period_id: str | None = None
    entry_date: date
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    lines: list[JournalEntryLineWriteRequest] = Field(min_length=2)


class JournalEntryReverseRequest(BaseModel):
    reverse_date: date | None = None
    notes: str | None = None


class JournalEntryLineResponse(BaseModel):
    id: str
    line_number: int
    account_id: str
    account_code: str
    account_name: str
    description: str | None
    debit_amount: Decimal
    credit_amount: Decimal


class JournalEntryResponse(BaseModel):
    id: str
    company_id: str
    fiscal_period_id: str
    entry_number: str
    entry_date: date
    status: str
    reference: str | None
    notes: str | None
    posted_at: datetime | None
    posted_by_user_id: str | None
    reversed_at: datetime | None
    reversed_by_user_id: str | None
    total_debit: Decimal
    total_credit: Decimal
    lines: list[JournalEntryLineResponse]


class TrialBalanceRowResponse(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    movement_debit: Decimal
    movement_credit: Decimal
    balance_debit: Decimal
    balance_credit: Decimal


class TrialBalanceSummaryResponse(BaseModel):
    movement_debit_total: Decimal
    movement_credit_total: Decimal
    balance_debit_total: Decimal
    balance_credit_total: Decimal
    entry_count: int


class TrialBalanceResponse(BaseModel):
    as_of_date: date | None
    fiscal_period_id: str | None
    included_statuses: list[str]
    rows: list[TrialBalanceRowResponse]
    summary: TrialBalanceSummaryResponse
