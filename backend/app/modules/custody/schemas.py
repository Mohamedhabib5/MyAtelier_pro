from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CustodyCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    branch_id: str
    booking_id: str | None
    booking_line_id: str | None
    customer_id: str | None
    dress_id: str | None
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    case_number: str
    custody_date: str
    status: str
    case_type: str
    notes: str | None
    product_condition: str | None = None
    return_outcome: str | None = None
    security_deposit_amount: float | None = None
    security_deposit_document_text: str | None = None
    security_deposit_payment_document_id: str | None = None
    security_deposit_refund_payment_document_id: str | None = None
    compensation_amount: float | None = None
    compensation_collected_on: str | None = None
    compensation_payment_document_id: str | None = None
    customer_name: str | None = None
    booking_number: str | None = None
    dress_code: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class CustodyCaseCreateRequest(BaseModel):
    booking_line_id: str = Field(min_length=3, max_length=64)
    custody_date: str
    case_type: str = Field(default="handover", min_length=3, max_length=30)
    notes: str | None = Field(default=None, max_length=1000)
    product_condition: str | None = Field(default=None, max_length=200)
    security_deposit_amount: float | None = Field(default=None, ge=0)
    security_deposit_document_text: str | None = Field(default=None, max_length=500)
    payment_method_id: str | None = Field(default=None, min_length=3, max_length=64)


class CustodyCaseActionRequest(BaseModel):
    action: str = Field(min_length=3, max_length=40)
    action_date: str
    note: str | None = Field(default=None, max_length=1000)
    product_condition: str | None = Field(default=None, max_length=200)
    return_outcome: str | None = Field(default=None, max_length=20)
    compensation_amount: float | None = Field(default=None, gt=0)
    payment_method_id: str | None = Field(default=None, min_length=3, max_length=64)


class CustodyCompensationCollectRequest(BaseModel):
    compensation_type_id: str = Field(min_length=3, max_length=64)
    amount: float = Field(gt=0)
    payment_date: str
    note: str | None = Field(default=None, max_length=1000)
    payment_method_id: str | None = Field(default=None, min_length=3, max_length=64)
    override_lock: bool = False
    override_reason: str | None = Field(default=None, max_length=500)
