from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    registration_date: str | None = None
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    full_name: str
    groom_name: str | None = None
    bride_name: str | None = None
    phone: str
    phone_2: str | None = None
    email: str | None
    address: str | None
    notes: str | None
    is_active: bool


class CustomerCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    groom_name: str | None = Field(default=None, max_length=160)
    bride_name: str | None = Field(default=None, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    phone_2: str | None = Field(default=None, max_length=30)
    registration_date: str | None = None
    email: str | None = Field(default=None, max_length=160)
    address: str = Field(min_length=2, max_length=255)
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    groom_name: str | None = Field(default=None, max_length=160)
    bride_name: str | None = Field(default=None, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    phone_2: str | None = Field(default=None, max_length=30)
    registration_date: str | None = None
    email: str | None = Field(default=None, max_length=160)
    address: str = Field(min_length=2, max_length=255)
    notes: str | None = None
    is_active: bool = True
    entity_version: int | None = None


class CustomerArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class CustomerStatementSummary(BaseModel):
    total_bookings_amount: float
    total_collections_amount: float
    total_refunds_amount: float
    remaining_balance: float
    accounting_ledger_balance: float


class CustomerBookingLineMovement(BaseModel):
    line_id: str
    line_number: int
    service_name: str
    department_name: str
    dress_code: str | None = None
    dress_name: str | None = None
    service_date: str
    status: str
    line_price: float
    revenue_recognized_at: str | None = None
    cancelled_at: str | None = None
    cancellation_reason: str | None = None


class CustomerBookingMovement(BaseModel):
    booking_id: str
    booking_number: str
    booking_date: str
    status: str
    branch_name: str
    total_amount: float
    paid_total: float
    remaining_amount: float
    cancelled_at: str | None = None
    cancellation_reason: str | None = None
    lines: list[CustomerBookingLineMovement] = []


class CustomerPaymentMovement(BaseModel):
    payment_id: str
    payment_number: str
    payment_date: str
    payment_method_name: str
    document_kind: str
    amount: float
    status: str
    voided_at: str | None = None
    void_reason: str | None = None
    notes: str | None = None


class CustomerLedgerMovement(BaseModel):
    entry_date: str
    entry_number: str
    reference: str | None = None
    description: str | None = None
    debit_amount: float
    credit_amount: float
    running_balance: float


class CustomerStatementResponse(BaseModel):
    customer: CustomerResponse
    summary: CustomerStatementSummary
    bookings: list[CustomerBookingMovement] = []
    payments: list[CustomerPaymentMovement] = []
    ledger_movements: list[CustomerLedgerMovement] = []

