"""Schemas de entrada y salida separados; las respuestas omiten credenciales."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class UserInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100, examples=["Ana García"])
    email: EmailStr = Field(max_length=254, examples=["ana@example.com"])

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class UserCreate(UserInput):
    password: SecretStr = Field(min_length=12, max_length=128)


class UserReplace(UserInput):
    is_active: bool
    password: SecretStr | None = Field(default=None, min_length=12, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool
    role: Literal["user", "admin"]


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: Literal["bearer"]
    expires_in: int


class ErrorResponse(BaseModel):
    detail: str
