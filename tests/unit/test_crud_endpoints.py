"""Contratos de todos los endpoints CRUD, sin depender de la base de datos."""

import pytest

from src.domain.errors import ConflictError, RepositoryUnavailableError

CASES = [
    (
        "clientes",
        "id_cliente",
        {
            "nombre": "Lucía",
            "email": "lucia@example.com",
            "estado_membresia": "Activo",
            "fecha_inscripcion": "2026-10-01",
        },
        {
            "nombre": "Lucía García",
            "email": None,
            "estado_membresia": "Suspendido",
            "fecha_inscripcion": "2026-10-02",
        },
    ),
    (
        "entrenadores",
        "id_entrenador",
        {
            "nombre": "Carlos",
            "especialidad": "Yoga",
            "telefono": "+34 600 000 000",
        },
        {"especialidad": "Pilates", "telefono": None},
    ),
    (
        "clases",
        "id_clase",
        {
            "nombre_clase": "Pilates",
            "horario": "2026-11-01T12:00:00",
            "capacidad_max": 5,
            "id_entrenador": 1,
        },
        {"capacidad_max": 8},
    ),
    (
        "pagos",
        "id_pago",
        {
            "id_cliente": 1,
            "monto": "39.90",
            "fecha_pago": "2026-10-06",
            "metodo_pago": "Tarjeta",
        },
        {"monto": "49.90", "metodo_pago": "Transferencia"},
    ),
    (
        "reservas",
        "id_reserva",
        {
            "id_cliente": 1,
            "id_clase": 1,
            "asistio": False,
        },
        {"asistio": True},
    ),
]


@pytest.mark.parametrize("resource,id_field,payload,changes", CASES)
def test_crud_completo(client, resource, id_field, payload, changes):
    path = f"/v1/{resource}"
    created = client.post(path, json=payload)
    assert created.status_code == 201, created.text
    entity = created.json()
    assert isinstance(entity[id_field], int)
    for key, value in payload.items():
        assert entity[key] == value
    detail = f"{path}/{entity[id_field]}"
    assert client.get(detail).json() == entity
    listed = client.get(path)
    assert listed.status_code == 200
    assert entity in listed.json()
    updated = client.put(detail, json=payload | changes)
    assert updated.status_code == 200, updated.text
    assert updated.json()[id_field] == entity[id_field]
    for key, value in changes.items():
        assert updated.json()[key] == value
    if resource == "reservas":
        assert updated.json()["fecha_reserva"] == entity["fecha_reserva"]
    assert client.get(detail).json() == updated.json()
    deleted = client.delete(detail)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(detail).status_code == 404
    assert client.delete(detail).status_code == 404


@pytest.mark.parametrize("resource,id_field,payload,changes", CASES)
@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_id_inexistente(client, resource, id_field, payload, changes, method):
    kwargs = {"json": payload} if method == "put" else {}
    response = client.request(method, f"/v1/{resource}/999", **kwargs)
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]


@pytest.mark.parametrize("resource,id_field,payload,changes", CASES)
def test_valida_cuerpo_y_parametros(client, resource, id_field, payload, changes):
    path = f"/v1/{resource}"
    assert client.post(path, json={}).status_code == 422
    assert client.put(f"{path}/1", json={}).status_code == 422
    assert client.post(path, json=payload | {id_field: 8}).status_code == 422
    assert client.get(f"{path}/0").status_code == 422
    assert client.get(f"{path}/abc").status_code == 422
    assert client.get(path, params={"offset": -1}).status_code == 422
    assert client.get(path, params={"limit": 101}).status_code == 422


@pytest.mark.parametrize(
    "resource,payload",
    [
        ("clientes", {"nombre": "  ", "estado_membresia": "Activo"}),
        ("clientes", {"nombre": "Ana", "estado_membresia": "Otro"}),
        (
            "clientes",
            {"nombre": "Ana", "estado_membresia": "Activo", "email": "sin-email"},
        ),
        ("clientes", {"nombre": "a" * 101, "estado_membresia": "Activo"}),
        ("entrenadores", {"nombre": "Ana", "especialidad": "a" * 101}),
        ("entrenadores", {"nombre": "Ana", "telefono": "1" * 21}),
        (
            "clientes",
            {
                "nombre": "Ana",
                "estado_membresia": "Activo",
                "fecha_inscripcion": "ayer",
            },
        ),
        (
            "clases",
            {
                "nombre_clase": "Yoga",
                "horario": "fecha incorrecta",
                "capacidad_max": 1,
                "id_entrenador": 1,
            },
        ),
        (
            "clases",
            {
                "nombre_clase": "Yoga",
                "horario": "2026-11-01T12:00:00",
                "capacidad_max": 0,
                "id_entrenador": 1,
            },
        ),
        (
            "clases",
            {
                "nombre_clase": "Yoga",
                "horario": "2026-11-01T12:00:00Z",
                "capacidad_max": 1,
                "id_entrenador": 1,
            },
        ),
        ("pagos", {"id_cliente": 1, "monto": "-1", "fecha_pago": "2026-10-06"}),
        ("pagos", {"id_cliente": 1, "monto": "1.001", "fecha_pago": "2026-10-06"}),
        (
            "pagos",
            {"id_cliente": 1, "monto": "100000000.00", "fecha_pago": "2026-10-06"},
        ),
        (
            "pagos",
            {
                "id_cliente": 1,
                "monto": "10",
                "fecha_pago": "2026-10-06",
                "metodo_pago": "Otro",
            },
        ),
        ("reservas", {"id_cliente": 0, "id_clase": 1}),
    ],
)
def test_rechaza_datos_invalidos(client, resource, payload):
    assert client.post(f"/v1/{resource}", json=payload).status_code == 422


@pytest.mark.parametrize(
    "resource,payload",
    [
        (
            "clases",
            {
                "nombre_clase": "Yoga",
                "horario": "2026-11-01T12:00:00",
                "capacidad_max": 1,
                "id_entrenador": 999,
            },
        ),
        ("pagos", {"id_cliente": 999, "monto": "10", "fecha_pago": "2026-10-06"}),
        ("reservas", {"id_cliente": 999, "id_clase": 1}),
        ("reservas", {"id_cliente": 1, "id_clase": 999}),
    ],
)
def test_referencia_inexistente(client, resource, payload):
    assert client.post(f"/v1/{resource}", json=payload).status_code == 404


def test_paginacion_estable(client):
    for name in ["B", "C"]:
        client.post("/v1/clientes", json={"nombre": name, "estado_membresia": "Activo"})
    response = client.get("/v1/clientes", params={"offset": 1, "limit": 1})
    assert response.status_code == 200
    assert [row["nombre"] for row in response.json()] == ["B"]


@pytest.mark.parametrize(
    "error,status",
    [
        (ConflictError("Registro duplicado"), 409),
        (RepositoryUnavailableError("Base de datos no disponible"), 503),
    ],
)
def test_traduce_errores(client, repository, monkeypatch, error, status):
    def fail(*args):
        raise error

    monkeypatch.setattr(repository, "list", fail)
    response = client.get("/v1/clientes")
    assert response.status_code == status
    assert response.json() == {"detail": str(error)}


def test_openapi_documenta_todos_los_endpoints(client):
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/users" not in paths
    assert "/v1/auth/login" not in paths
    assert not spec["components"].get("securitySchemes")
    for resource, id_field, _, _ in CASES:
        for path, methods in [
            (f"/v1/{resource}", ["get", "post"]),
            (f"/v1/{resource}/{{{id_field}}}", ["get", "put", "delete"]),
        ]:
            for method in methods:
                operation = paths[path][method]
                assert operation["summary"]
                assert operation["tags"] == [resource]
                code = {"post": "201", "delete": "204"}.get(method, "200")
                success = operation["responses"][code]
                if code == "204":
                    assert "content" not in success
                else:
                    assert success["content"]["application/json"]["schema"]
                assert {"404", "409", "422", "503"} <= operation["responses"].keys()
