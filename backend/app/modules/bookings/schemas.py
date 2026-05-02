from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BookingLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    booking_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    line_number: int
    department_id: str
    department_name: str
    service_id: str
    service_name: str
    dress_id: str | None
    dress_code: str | None
    service_date: str
    suggested_price: float
    line_price: float
    tax_rate_percent: float
    tax_amount: float
    paid_total: float
    remaining_amount: float
    payment_state: str
    status: str
    revenue_journal_entry_id: str | None
    revenue_journal_entry_number: str | None
    revenue_journal_entry_status: str | None
    revenue_recognized_at: str | None
    notes: str | None
    is_locked: bool


class BookingSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    branch_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    branch_name: str
    booking_number: str
    customer_id: str
    customer_name: str
    booking_date: str
    status: str
    line_count: int
    service_summary: str
    next_service_date: str | None
    total_amount: float
    paid_total: float
    remaining_amount: float
    notes: str | None
    external_code: str | None


class BookingDocumentResponse(BookingSummaryResponse):
    lines: list[BookingLineResponse]


class BookingSummaryPageResponse(BaseModel):
    items: list[BookingSummaryResponse]
    total: int
    page: int
    page_size: int


class BookingLineInput(BaseModel):
    id: str | None = None
    department_id: str
    service_id: str
    service_date: str
    dress_id: str | None = None
    suggested_price: float | None = Field(default=None, ge=0)
    line_price: float = Field(ge=0)
    initial_payment_amount: float | None = Field(default=None, ge=0)
    status: str = Field(min_length=2, max_length=40)
    notes: str | None = None


class BookingDocumentCreateRequest(BaseModel):
    customer_id: str
    initial_payment_method_id: str | None = None
    booking_date: str | None = None
    notes: str | None = None
    external_code: str | None = None
    lines: list[BookingLineInput] = Field(min_length=1)


class BookingDocumentUpdateRequest(BookingDocumentCreateRequest):
    pass


class CalendarEventResponse(BaseModel):
    id: str
    booking_id: str
    title: str
    start: str
    end: str
    status: str
    department_name: str
    service_name: str
    customer_name: str
    booking_number: str
    external_code: str | None


class BookingCompensationCreateRequest(BaseModel):
    department_id: str
    service_id: str
    amount: float = Field(gt=0)
    notes: str | None = None
