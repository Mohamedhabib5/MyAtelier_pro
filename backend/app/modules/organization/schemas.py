from __future__ import annotations

from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    is_default: bool
    is_active: bool


class ActiveBranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    is_default: bool
    is_active: bool


class BranchCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)


class SetActiveBranchRequest(BaseModel):
    branch_id: str = Field(min_length=1)


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    legal_name: str | None
    default_currency: str
    is_active: bool
    branches: list[BranchResponse]


class UpdateCompanyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    legal_name: str | None = Field(default=None, max_length=180)
    default_currency: str = Field(default='EGP', min_length=3, max_length=3)


class FiscalPeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    starts_on: date
    ends_on: date
    is_active: bool
    is_locked: bool


class FiscalPeriodCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    starts_on: date
    ends_on: date


class FiscalPeriodUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    is_active: bool | None = None
    is_locked: bool | None = None
