from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_by_user_id: str | None
    updated_by_user_id: str | None
    entity_version: int
    code: str
    name: str
    dress_type_id: str | None
    dress_type_name: str | None = None
    purchase_date: str | None
    status: str
    description: str | None
    image_path: str | None
    is_active: bool


class DressCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=2, max_length=120)
    dress_type_id: str | None = Field(default=None, min_length=2, max_length=80)
    purchase_date: str | None = None
    status: str = Field(min_length=2, max_length=40)
    description: str | None = Field(default=None)
    image_path: str | None = Field(default=None, max_length=255)


class DressUpdateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=2, max_length=120)
    dress_type_id: str | None = Field(default=None, min_length=2, max_length=80)
    purchase_date: str | None = None
    status: str = Field(min_length=2, max_length=40)
    description: str | None = Field(default=None)
    image_path: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class DressArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
