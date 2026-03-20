from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    full_name: str
    phone: str
    email: str | None
    address: str | None
    notes: str | None
    is_active: bool


class CustomerCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    email: str | None = Field(default=None, max_length=160)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class CustomerUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=3, max_length=30)
    email: str | None = Field(default=None, max_length=160)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool = True
