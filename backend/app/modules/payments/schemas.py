from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    code: str
    name: str
    is_active: bool
    display_order: int
    linked_account_id: str | None = None
    linked_account_code: str | None = None
    linked_account_name: str | None = None


class PaymentMethodCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=40)
    is_active: bool = True
    linked_account_id: str | None = None


class PaymentMethodUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    is_active: bool | None = None
    display_order: int | None = Field(default=None, ge=1, le=100000)
    linked_account_id: str | None = None


class PaymentAllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_document_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
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
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    branch_name: str
    customer_id: str
    customer_name: str
    customer_phone: str | None
    customer_address: str | None
    payment_method_id: str | None
    payment_method_name: str | None
    payment_number: str
    payment_date: str
    document_kind: str
    direct_amount: float
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


class PaymentDocumentSummaryPageResponse(BaseModel):
    items: list[PaymentDocumentSummaryResponse]
    total: int
    page: int
    page_size: int


class PaymentAllocationInput(BaseModel):
    booking_id: str
    booking_line_id: str
    allocated_amount: float = Field(gt=0)


class PaymentDocumentCreateRequest(BaseModel):
    customer_id: str
    payment_method_id: str | None = None
    payment_date: str
    document_kind: str = "collection"
    notes: str | None = None
    allocations: list[PaymentAllocationInput] = Field(min_length=1)


class PaymentDocumentUpdateRequest(BaseModel):
    customer_id: str
    payment_method_id: str | None = None
    payment_date: str
    document_kind: str = "collection"
    notes: str | None = None
    allocations: list[PaymentAllocationInput] = Field(min_length=1)
    reason_code: str | None = None
    override_lock: bool = False
    override_reason: str | None = Field(default=None, max_length=500)


class PaymentVoidRequest(BaseModel):
    void_date: str
    override_lock: bool = False
    override_reason: str | None = Field(default=None, max_length=500)
    reason_code: str | None = None
    reason: str = Field(min_length=3, max_length=500)


class PaymentTargetSearchResult(BaseModel):
    kind: str
    id: str
    label: str
    customer_id: str
    customer_name: str
    customer_phone: str | None
    customer_address: str | None
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
    customer_phone: str | None
    customer_address: str | None
    branch_id: str
    branch_name: str
    total_remaining: float
    bookings: list[PaymentTargetBookingResponse]


class DisbursementVoucherSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    branch_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    branch_name: str | None = None
    payment_method_id: str
    payment_method_name: str | None = None
    voucher_number: str
    voucher_date: str
    amount: float
    payee_type: str
    payee_id: str | None = None
    payee_name: str | None = None
    expense_account_id: str | None = None
    expense_account_code: str | None = None
    expense_account_name: str | None = None
    status: str
    journal_entry_id: str | None = None
    journal_entry_number: str | None = None
    journal_entry_status: str | None = None
    voided_at: str | None = None
    void_reason: str | None = None
    notes: str | None = None
    source_table: str | None = None
    booking_numbers: list[str] | None = None


class DisbursementVoucherResponse(DisbursementVoucherSummaryResponse):
    pass


class DisbursementVoucherSummaryPageResponse(BaseModel):
    items: list[DisbursementVoucherSummaryResponse]
    total: int
    page: int
    page_size: int


class DisbursementVoucherCreateRequest(BaseModel):
    payment_method_id: str
    voucher_date: str
    amount: float = Field(gt=0)
    payee_type: str = Field(min_length=1, max_length=30)  # 'customer', 'supplier', 'employee', 'expense'
    payee_id: str | None = None
    payee_name: str | None = None
    expense_account_id: str | None = None
    notes: str | None = None


class DisbursementVoucherUpdateRequest(BaseModel):
    payment_method_id: str | None = None
    voucher_date: str | None = None
    amount: float | None = Field(default=None, gt=0)
    payee_type: str | None = None
    payee_id: str | None = None
    payee_name: str | None = None
    expense_account_id: str | None = None
    notes: str | None = None
    reason_code: str | None = None
    override_lock: bool = False
    override_reason: str | None = Field(default=None, max_length=500)

