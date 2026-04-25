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
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    groom_name: str | None = Field(default=None, max_length=160)
    bride_name: str | None = Field(default=None, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    phone_2: str | None = Field(default=None, max_length=30)
    registration_date: str | None = None
    email: str | None = Field(default=None, max_length=160)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool = True


class CustomerArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
