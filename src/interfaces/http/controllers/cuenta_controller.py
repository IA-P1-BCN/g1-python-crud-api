"""Traducción entre los contratos HTTP y los casos de uso de Cuenta."""

from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.domain.entities.cuenta import Cuenta
from src.interfaces.http.schemas.cuenta_schema import (
    CuentaPatch,
    CuentaRegister,
    CuentaResponse,
    CuentaSelfPatch,
)
from src.interfaces.http.schemas.list_query import CuentaQuery


class CuentaController:
    def __init__(self, use_cases: CuentaUseCases) -> None:
        self._use_cases = use_cases

    @staticmethod
    def me(cuenta: Cuenta) -> CuentaResponse:
        return CuentaResponse.model_validate(cuenta)

    def list(self, query: CuentaQuery) -> list[CuentaResponse]:
        return [
            CuentaResponse.model_validate(cuenta)
            for cuenta in self._use_cases.list(
                query.offset, query.limit, query.to_filters()
            )
        ]

    def get(self, cuenta_id: int) -> CuentaResponse:
        return CuentaResponse.model_validate(self._use_cases.get(cuenta_id))

    def delete(self, cuenta_id: int) -> None:
        self._use_cases.delete(cuenta_id)

    def set_entrenador(
        self, cuenta_id: int, id_entrenador: int | None
    ) -> CuentaResponse:
        return CuentaResponse.model_validate(
            self._use_cases.set_entrenador(cuenta_id, id_entrenador)
        )

    def update(self, cuenta_id: int, data: CuentaPatch) -> CuentaResponse:
        password = (
            data.password.get_secret_value() if data.password is not None else None
        )
        return CuentaResponse.model_validate(
            self._use_cases.update(cuenta_id, data.nombre, data.email, password)
        )

    def update_self(self, cuenta_id: int, data: CuentaSelfPatch) -> CuentaResponse:
        return CuentaResponse.model_validate(
            self._use_cases.update_self(
                cuenta_id,
                data.nombre,
                data.email,
                data.password.get_secret_value() if data.password is not None else None,
                data.current_password.get_secret_value()
                if data.current_password is not None
                else None,
            )
        )

    def register(self, data: CuentaRegister) -> CuentaResponse:
        cuenta = self._use_cases.register(
            data.nombre,
            str(data.email),
            data.password.get_secret_value(),
            data.crear_cliente,
        )
        return CuentaResponse.model_validate(cuenta)
