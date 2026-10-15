"""Respuesta OAuth2 estándar."""

from typing import Literal

from src.interfaces.http.schemas.gym_schema import ApiSchema


class TokenResponse(ApiSchema):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
