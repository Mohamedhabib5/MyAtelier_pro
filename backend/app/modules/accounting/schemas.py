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
    level: int
    allows_posting: bool
    is_active: bool


class JournalEntryLineWriteRequest(BaseModel):
    account_id: str
    description: str | None = Field(default=None, max_length=255)
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    party_type: str | None = Field(default=None, max_length=30)
    party_id: str | None = None


class JournalEntryCreateRequest(BaseModel):
    fiscal_period_id: str | None = None
    branch_id: str | None = None
    entry_date: date
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    reference_type: str | None = Field(default=None, max_length=40)
    reference_id: str | None = None
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
    party_type: str | None = None
    party_id: str | None = None


class JournalEntryResponse(BaseModel):
    id: str
    company_id: str
    fiscal_period_id: str
    branch_id: str | None = None
    entry_number: str
    entry_date: date
    status: str
    reference: str | None
    notes: str | None
    reference_type: str | None = None
    reference_id: str | None = None
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
    branch_id: str | None = None
    included_statuses: list[str]
    rows: list[TrialBalanceRowResponse]
    summary: TrialBalanceSummaryResponse


# --- Income Statement Schemas ---

class IncomeStatementItemResponse(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: str | None = None
    level: int
    debit: Decimal
    credit: Decimal
    balance: Decimal


class IncomeStatementSectionResponse(BaseModel):
    items: list[IncomeStatementItemResponse]
    total: Decimal


class IncomeStatementResponse(BaseModel):
    as_of_date: date | None = None
    branch_id: str | None = None
    revenues: IncomeStatementSectionResponse
    expenses: IncomeStatementSectionResponse
    net_income: Decimal


# --- Aging Report Schemas ---

class AgingBucketResponse(BaseModel):
    current: Decimal = Field(default=Decimal("0.00"), description="0-30 Days")
    past_31_60: Decimal = Field(default=Decimal("0.00"), alias="31-60", description="31-60 Days")
    past_61_90: Decimal = Field(default=Decimal("0.00"), alias="61-90", description="61-90 Days")
    critical_90_plus: Decimal = Field(default=Decimal("0.00"), alias="91+", description="91+ Days")

    model_config = ConfigDict(populate_by_name=True)


class PartyAgingRowResponse(BaseModel):
    party_id: str
    party_name: str
    party_type: str
    total_outstanding: Decimal
    buckets: AgingBucketResponse


class AgingReportResponse(BaseModel):
    as_of_date: date
    party_type: str
    rows: list[PartyAgingRowResponse]
    total_receivable_or_payable: Decimal

