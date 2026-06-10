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
    dresses_mode: str
    branches: list[BranchResponse]
    daily_report_sender_email: str | None = None
    daily_report_sender_password: str | None = None
    daily_report_smtp_server: str | None = None
    daily_report_smtp_port: int | None = None
    daily_report_recipient_email: str | None = None
    daily_report_send_hour: int = 21


class UpdateCompanyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    legal_name: str | None = Field(default=None, max_length=180)
    default_currency: str = Field(default='EGP', min_length=3, max_length=3)
    dresses_mode: str = Field(default='free', min_length=2, max_length=20)
    daily_report_sender_email: str | None = Field(default=None, max_length=120)
    daily_report_sender_password: str | None = Field(default=None, max_length=255)
    daily_report_smtp_server: str | None = Field(default='smtp.gmail.com', max_length=120)
    daily_report_smtp_port: int | None = Field(default=587, ge=1, le=65535)
    daily_report_recipient_email: str | None = Field(default=None, max_length=255)
    daily_report_send_hour: int = Field(default=21, ge=0, le=23)


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
