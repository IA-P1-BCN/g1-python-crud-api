"""Traducción entre los contratos HTTP y los casos de uso de Cuenta."""

from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.domain.entities.cuenta import Cuenta
from src.interfaces.http.schemas.cuenta_schema import CuentaRegister, CuentaResponse


class CuentaController:
    def __init__(self, use_cases: CuentaUseCases) -> None:
        self._use_cases = use_cases

    @staticmethod
    def me(cuenta: Cuenta) -> CuentaResponse:
        return CuentaResponse.model_validate(cuenta)

    def register(self, data: CuentaRegister) -> CuentaResponse:
        cuenta = self._use_cases.register(
            data.nombre,
            str(data.email),
            data.password.get_secret_value(),
            data.crear_cliente,
        )
        return CuentaResponse.model_validate(cuenta)
