from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LanguageLiteral = Literal["ar", "en"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=120)
    language: LanguageLiteral | None = None


class SessionLanguageRequest(BaseModel):
    language: LanguageLiteral


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    full_name: str
    is_active: bool
    role_names: list[str]
    active_branch_id: str
    active_branch_name: str
    preferred_language: LanguageLiteral
    session_language: LanguageLiteral
    effective_language: LanguageLiteral


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    full_name: str
    is_active: bool
    last_login_at: datetime | None
    role_names: list[str]
    preferred_language: LanguageLiteral


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6, max_length=120)
    role_names: list[str] = Field(default_factory=lambda: ['user'])


class AdminUpdateUserRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=60)
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=120)
    role_names: list[str] | None = None
    is_active: bool | None = None


class SelfUpdateUserRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=120)
    preferred_language: LanguageLiteral | None = None
