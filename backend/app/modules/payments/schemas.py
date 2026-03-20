from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaymentAllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_document_id: str
    booking_id: str
    booking_number: str
    booking_status: str
    booking_line_id: str
    booking_line_number: int
    service_name: str
    department_name: str
    dress_code: str | None
    service_date: str
    line_status: str
    line_price: float
    allocated_amount: float


class PaymentDocumentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    branch_id: str
    branch_name: str
    customer_id: str
    customer_name: str
    payment_number: str
    payment_date: str
    document_kind: str
    status: str
    total_amount: float
    allocation_count: int
    booking_numbers: list[str]
    journal_entry_id: str | None
    journal_entry_number: str | None
    journal_entry_status: str | None
    voided_at: str | None
    void_reason: str | None
    notes: str | None


class PaymentDocumentResponse(PaymentDocumentSummaryResponse):
    allocations: list[PaymentAllocationResponse]


class PaymentAllocationInput(BaseModel):
    booking_id: str
    booking_line_id: str
    allocated_amount: float = Field(gt=0)


class PaymentDocumentCreateRequest(BaseModel):
    customer_id: str
    payment_date: str
    notes: str | None = None
    allocations: list[PaymentAllocationInput] = Field(min_length=1)


class PaymentDocumentUpdateRequest(PaymentDocumentCreateRequest):
    pass


class PaymentVoidRequest(BaseModel):
    void_date: str
    reason: str = Field(min_length=3, max_length=500)


class PaymentTargetSearchResult(BaseModel):
    kind: str
    id: str
    label: str
    customer_id: str
    customer_name: str
    booking_id: str | None = None
    booking_number: str | None = None


class PaymentTargetLineResponse(BaseModel):
    line_id: str
    line_number: int
    service_name: str
    department_name: str
    dress_code: str | None
    service_date: str
    line_status: str
    line_price: float
    paid_total: float
    remaining_amount: float
    payment_state: str


class PaymentTargetBookingResponse(BaseModel):
    booking_id: str
    booking_number: str
    booking_date: str
    booking_status: str
    total_amount: float
    paid_total: float
    remaining_amount: float
    lines: list[PaymentTargetLineResponse]


class PaymentTargetDetailResponse(BaseModel):
    scope_kind: str
    scope_id: str
    customer_id: str
    customer_name: str
    branch_id: str
    branch_name: str
    total_remaining: float
    bookings: list[PaymentTargetBookingResponse]
