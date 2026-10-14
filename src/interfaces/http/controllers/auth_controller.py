"""Adaptación de autenticación al contrato HTTP."""

from src.application.use_cases.auth_use_cases import AuthUseCases
from src.interfaces.http.schemas.auth_schema import TokenResponse


class AuthController:
    def __init__(self, use_cases: AuthUseCases) -> None:
        self._use_cases = use_cases

    def login(self, email: str, password: str) -> TokenResponse:
        return TokenResponse(access_token=self._use_cases.login(email, password))
