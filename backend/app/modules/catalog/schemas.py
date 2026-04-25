from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    code: str
    name: str
    is_active: bool
    is_dress_department: bool
    display_order: int


class DepartmentCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    display_order: int = 0


class DepartmentUpdateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    is_active: bool = True
    display_order: int = 0


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    department_id: str
    department_name: str
    name: str
    default_price: float
    tax_rate_percent: float
    duration_minutes: int | None
    notes: str | None
    is_active: bool
    display_order: int


class ServiceCreateRequest(BaseModel):
    department_id: str
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    tax_rate_percent: float = Field(default=0, ge=0, le=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None
    display_order: int = 0


class ServiceUpdateRequest(BaseModel):
    department_id: str
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    tax_rate_percent: float = Field(default=0, ge=0, le=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None
    is_active: bool = True
    display_order: int = 0


class CatalogArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class SetDressDepartmentRequest(BaseModel):
    department_id: str
