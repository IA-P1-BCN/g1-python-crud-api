"""Entrada y salida independientes: nunca serializar credenciales."""

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, EmailStr, Field, SecretStr, field_validator

from src.interfaces.http.schemas.gym_schema import ApiSchema


class CuentaRegister(ApiSchema):
    # Una contraseña es literal: no hereda el recorte de texto del CRUD.
    model_config = ConfigDict(str_strip_whitespace=False)

    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    password: SecretStr = Field(min_length=12, max_length=128)
    crear_cliente: bool = False

    @field_validator("nombre", mode="before")
    @classmethod
    def strip_nombre(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class CuentaResponse(ApiSchema):
    id: int
    nombre: str
    email: EmailStr
    activo: bool
    rol: Literal["admin", "staff", "cliente"]
    fecha_creacion: datetime
    id_cliente: int | None
