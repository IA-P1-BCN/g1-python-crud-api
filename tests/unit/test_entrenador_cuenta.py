"""Alta conjunta de Entrenador y Cuenta staff desde el panel de admin (#134)."""

from contextlib import contextmanager

from main import app
from src.application.use_cases.cuenta_use_cases import CuentaUseCases
from src.domain.entities.cuenta import Cuenta
from src.domain.entities.gym import IdentidadEntrenador
from src.interfaces.http.dependencies import get_cuenta_use_cases, get_current_user


class FakeHasher:
    def hash(self, password: str) -> str:
        return f"hash:{password}"

    def verify(self, password: str, hashed: str) -> bool:
        return hashed == f"hash:{password}"


class FakeCuentaRepository:
    def __init__(self) -> None:
        self.cuentas: list[Cuenta] = []

    @contextmanager
    def transaction(self):
        yield

    def get_by_email(self, email: str) -> Cuenta | None:
        return next((c for c in self.cuentas if c.email == email), None)

    def create_entrenador(self, nombre, especialidad, telefono, email, password_hash):
        cuenta = Cuenta(
            id=len(self.cuentas) + 50,
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol="staff",
            activo=True,
            id_entrenador=len(self.cuentas) + 100,
        )
        self.cuentas.append(cuenta)
        return cuenta


def _override_cuentas(client_fixture) -> FakeCuentaRepository:
    repositorio = FakeCuentaRepository()
    app.dependency_overrides[get_cuenta_use_cases] = lambda: CuentaUseCases(
        repositorio, FakeHasher()
    )
    return repositorio


def test_crear_entrenador_con_email_crea_cuenta_staff(client):
    cuentas = _override_cuentas(client)
    try:
        respuesta = client.post(
            "/v1/entrenadores",
            json={
                "nombre": "Nora Prieto",
                "especialidad": "Spinning",
                "email": "nueva@gymflow.com",
            },
        )
        assert respuesta.status_code == 201, respuesta.text
        cuerpo = respuesta.json()
        assert cuerpo["id_user"] is not None
        assert cuerpo["email"] == "nueva@gymflow.com"
        cuenta = cuentas.cuentas[0]
        assert cuenta.rol == "staff" and cuenta.activo
        assert cuenta.password_hash == "hash:Demo56789012"
        assert cuenta.id_entrenador == cuerpo["id_entrenador"]
    finally:
        app.dependency_overrides.pop(get_cuenta_use_cases, None)


def test_email_duplicado_devuelve_409(client):
    cuentas = _override_cuentas(client)
    cuentas.cuentas.append(
        Cuenta(
            id=1, nombre="X", email="repetida@gymflow.com", password_hash="h"
        )
    )
    try:
        respuesta = client.post(
            "/v1/entrenadores",
            json={"nombre": "Otro", "email": "repetida@gymflow.com"},
        )
        assert respuesta.status_code == 409
        assert len(cuentas.cuentas) == 1
    finally:
        app.dependency_overrides.pop(get_cuenta_use_cases, None)


def test_email_invalido_es_422(client):
    respuesta = client.post(
        "/v1/entrenadores", json={"nombre": "X", "email": "no-es-email"}
    )
    assert respuesta.status_code == 422


def test_sin_email_crea_solo_el_entrenador(client):
    cuentas = _override_cuentas(client)
    try:
        respuesta = client.post(
            "/v1/entrenadores", json={"nombre": "Histórico", "especialidad": None}
        )
        assert respuesta.status_code == 201
        cuerpo = respuesta.json()
        assert cuerpo["id_user"] is None and cuerpo["email"] is None
        assert cuentas.cuentas == []
    finally:
        app.dependency_overrides.pop(get_cuenta_use_cases, None)


def test_put_rechaza_el_campo_email(client):
    respuesta = client.put(
        "/v1/entrenadores/1",
        json={"nombre": "Laura", "especialidad": "Yoga", "email": "x@gymflow.com"},
    )
    assert respuesta.status_code == 422


def test_get_resuelve_cuenta_vinculada(client, repository):
    repository.staff_accounts[1] = IdentidadEntrenador(
        id_entrenador=1, id_user=7, email="staff@gymflow.com"
    )
    detalle = client.get("/v1/entrenadores/1").json()
    assert detalle["id_user"] == 7
    assert detalle["email"] == "staff@gymflow.com"


def test_cliente_no_puede_crear_entrenadores(client):
    cuentas = _override_cuentas(client)
    app.dependency_overrides[get_current_user] = lambda: Cuenta(
        id=2, nombre="Socio", email="socio@example.com", password_hash="t",
        rol="cliente", id_cliente=1,
    )
    try:
        respuesta = client.post(
            "/v1/entrenadores",
            json={"nombre": "Sin permiso", "email": "x@gymflow.com"},
        )
        assert respuesta.status_code == 403
        assert cuentas.cuentas == []
    finally:
        app.dependency_overrides.pop(get_cuenta_use_cases, None)
        app.dependency_overrides.pop(get_current_user, None)
