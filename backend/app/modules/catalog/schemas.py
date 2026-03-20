from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    code: str
    name: str
    is_active: bool


class DepartmentCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=120)


class DepartmentUpdateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    is_active: bool = True


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    department_id: str
    department_name: str
    name: str
    default_price: float
    duration_minutes: int | None
    notes: str | None
    is_active: bool


class ServiceCreateRequest(BaseModel):
    department_id: str
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None


class ServiceUpdateRequest(BaseModel):
    department_id: str
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None
    is_active: bool = True
