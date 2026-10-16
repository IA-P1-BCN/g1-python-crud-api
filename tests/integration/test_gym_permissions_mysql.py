"""Aislamiento por propietario y vínculo staff con HTTP, JWT y MySQL reales."""

from uuid import uuid4

import pytest
from sqlalchemy import delete

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import (
    ClaseRecord,
    ClienteRecord,
    CuentaRecord,
    EntrenadorRecord,
    PagoRecord,
    ReservaRecord,
)


@pytest.fixture
def role_gym(accounts_api, gym_admin_headers):
    http, emails = accounts_api
    admin = gym_admin_headers
    clients, trainers = [], []

    def post(path, data):
        response = http.post(f"/v1/{path}", json=data, headers=admin)
        assert response.status_code == 201, response.text
        return response.json()

    def account(role):
        email = f"{uuid4().hex}@example.com"
        emails.append(email)
        data = post(
            "auth/register",
            {
                "nombre": role,
                "email": email,
                "password": "clave de pruebas",
                "crear_cliente": role == "cliente",
            },
        )
        if data["id_cliente"] is not None:
            clients.append(data["id_cliente"])
        with SessionLocal.begin() as session:
            session.get(CuentaRecord, data["id"]).rol = role
        login = http.post(
            "/v1/auth/login", data={"username": email, "password": "clave de pruebas"}
        )
        assert login.status_code == 200, login.text
        data["headers"] = {"Authorization": f"Bearer {login.json()['access_token']}"}
        return data

    try:
        member, other = account("cliente"), account("cliente")
        staff, other_staff = account("staff"), account("staff")
        for member_data in (member, other):
            response = http.put(
                f"/v1/clientes/{member_data['id_cliente']}",
                headers=admin,
                json={"nombre": "Socio", "estado_membresia": "Activo"},
            )
            assert response.status_code == 200, response.text
            post(
                "pagos",
                {
                    "id_cliente": member_data["id_cliente"],
                    "monto": "25.00",
                    "fecha_pago": "2026-10-16",
                },
            )
        for name in ("Entrenador A", "Entrenador B", "Sin clases"):
            trainers.append(post("entrenadores", {"nombre": name})["id_entrenador"])
        for data, trainer in zip((staff, other_staff), trainers, strict=False):
            response = http.put(
                f"/v1/users/{data['id']}/entrenador",
                headers=admin,
                json={"id_entrenador": trainer},
            )
            assert response.status_code == 200, response.text
        classes = [
            post(
                "clases",
                {
                    "nombre_clase": "Clase de prueba",
                    "horario": "2026-11-01T10:00:00",
                    "capacidad_max": 10,
                    "id_entrenador": trainer,
                },
            )["id_clase"]
            for trainer in (trainers[0], trainers[1], trainers[0])
        ]
        reservations = [
            post("reservas", {"id_cliente": clients[c], "id_clase": classes[k]})
            for c, k in ((0, 0), (1, 1), (1, 0), (0, 2))
        ]
        yield (
            http,
            admin,
            member,
            other,
            staff,
            other_staff,
            trainers,
            classes,
            reservations,
        )
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(CuentaRecord).where(CuentaRecord.email.in_(emails)))
            session.execute(
                delete(ReservaRecord).where(ReservaRecord.id_cliente.in_(clients))
            )
            session.execute(
                delete(PagoRecord).where(PagoRecord.id_cliente.in_(clients))
            )
            session.execute(
                delete(ClaseRecord).where(ClaseRecord.id_entrenador.in_(trainers))
            )
            session.execute(
                delete(ClienteRecord).where(ClienteRecord.id_cliente.in_(clients))
            )
            session.execute(
                delete(EntrenadorRecord).where(
                    EntrenadorRecord.id_entrenador.in_(trainers)
                )
            )


def test_sql_scope_precedes_pagination_and_combines_filters(role_gym):
    http, _, member, other, staff, _, trainers, classes, reservations = role_gym
    for actor, expected in ((member, 3), (staff, 2)):
        response = http.get("/v1/reservas?offset=1&limit=1", headers=actor["headers"])
        assert response.status_code == 200
        assert [row["id_reserva"] for row in response.json()] == [
            reservations[expected]["id_reserva"]
        ]
    assert (
        http.get(
            f"/v1/reservas?id_cliente={other['id_cliente']}", headers=member["headers"]
        ).json()
        == []
    )
    assert (
        http.get(
            f"/v1/clases?id_entrenador={trainers[1]}", headers=staff["headers"]
        ).json()
        == []
    )
    assert (
        http.get(f"/v1/reservas?id_clase={classes[1]}", headers=staff["headers"]).json()
        == []
    )
    for resource in ("clientes", "pagos"):
        rows = http.get(f"/v1/{resource}", headers=member["headers"]).json()
        assert rows and all(r["id_cliente"] == member["id_cliente"] for r in rows)
    own = http.get(
        f"/v1/reservas?id_clase={classes[0]}", headers=member["headers"]
    ).json()
    cupo = http.get(f"/v1/clases/{classes[0]}/cupo", headers=member["headers"])
    assert len(own) == 1
    assert cupo.json() == {
        "id_clase": classes[0],
        "capacidad_max": 10,
        "reservas": 2,
        "plazas_disponibles": 8,
    }


def test_foreign_ids_and_reservation_owner_cannot_be_changed(role_gym):
    http, admin, member, other, staff, _, _, classes, reservations = role_gym
    foreign = reservations[1]
    values = {"id_cliente": member["id_cliente"], "id_clase": classes[0]}
    for actor in (member, staff):
        url = f"/v1/reservas/{foreign['id_reserva']}"
        assert http.get(url, headers=actor["headers"]).status_code == 404
        assert http.put(url, json=values, headers=actor["headers"]).status_code == 404
        assert http.delete(url, headers=actor["headers"]).status_code == 404
    url = f"/v1/reservas/{reservations[0]['id_reserva']}"
    for changes in ({"id_cliente": other["id_cliente"]}, {"asistio": True}):
        assert (
            http.put(url, json=values | changes, headers=member["headers"]).status_code
            == 403
        )
    assert (
        http.put(
            url, json=values | {"id_clase": classes[1]}, headers=staff["headers"]
        ).status_code
        == 403
    )
    assert http.get(url, headers=admin).json() == reservations[0]
    response = http.put(url, json=values | {"asistio": True}, headers=staff["headers"])
    assert response.status_code == 200 and response.json()["asistio"] is True
    for actor in (member, staff):
        for table in ("clientes", "entrenadores", "clases", "reservas", "pagos"):
            assert (
                http.get(
                    f"/v1/export/csv?tablas={table}", headers=actor["headers"]
                ).status_code
                == 403
            )


def test_client_can_create_move_and_cancel_own_reservation(role_gym):
    http, _, member, _, _, _, _, classes, reservations = role_gym
    own = member["headers"]
    url = f"/v1/reservas/{reservations[3]['id_reserva']}"
    values = {"id_cliente": member["id_cliente"], "id_clase": classes[1]}
    moved = http.put(url, json=values, headers=own)
    assert moved.status_code == 200, moved.text
    assert moved.json()["fecha_reserva"] == reservations[3]["fecha_reserva"]
    assert http.delete(url, headers=own).status_code == 204
    created = http.post("/v1/reservas", json=values, headers=own)
    assert created.status_code == 201, created.text
    assert (
        http.delete(
            f"/v1/reservas/{created.json()['id_reserva']}", headers=own
        ).status_code
        == 204
    )
    assert (
        http.get(f"/v1/clases/{classes[1]}/cupo", headers=own).json()[
            "plazas_disponibles"
        ]
        == 9
    )


def test_binding_is_explicit_unique_and_restricts_trainer_delete(role_gym):
    http, admin, member, _, staff, other_staff, trainers, _, _ = role_gym
    url = f"/v1/users/{staff['id']}/entrenador"
    for actor in (member, staff):
        assert (
            http.put(
                url, json={"id_entrenador": trainers[2]}, headers=actor["headers"]
            ).status_code
            == 403
        )
    for body in (
        {},
        {"id_entrenador": 0},
        {"id_entrenador": trainers[2], "rol": "admin"},
    ):
        assert http.put(url, json=body, headers=admin).status_code == 422
    assert (
        http.put(url, json={"id_entrenador": 2147483647}, headers=admin).status_code
        == 404
    )
    assert (
        http.put(url, json={"id_entrenador": trainers[1]}, headers=admin).status_code
        == 409
    )
    assert (
        http.get("/v1/users/me", headers=staff["headers"]).json()["id_entrenador"]
        == trainers[0]
    )
    assert (
        http.put(
            f"/v1/users/{member['id']}/entrenador",
            json={"id_entrenador": trainers[2]},
            headers=admin,
        ).status_code
        == 409
    )
    assert (
        http.put(url, json={"id_entrenador": trainers[2]}, headers=admin).status_code
        == 200
    )
    # Entrenador sin clases: la FK de Cuenta es la única dependencia.
    assert (
        http.delete(f"/v1/entrenadores/{trainers[2]}", headers=admin).status_code == 409
    )
    assert http.put(url, json={"id_entrenador": None}, headers=admin).status_code == 200
    assert (
        http.delete(f"/v1/entrenadores/{trainers[2]}", headers=admin).status_code == 204
    )
    assert (
        http.get("/v1/users/me", headers=other_staff["headers"]).json()["id_entrenador"]
        == trainers[1]
    )


def test_same_token_uses_current_link_and_role_without_guessing(role_gym):
    http, admin, _, _, staff, _, trainers, classes, _ = role_gym
    url = f"/v1/users/{staff['id']}/entrenador"
    token = staff["headers"]
    assert http.get(f"/v1/clases/{classes[0]}", headers=token).status_code == 200
    assert http.put(url, json={"id_entrenador": None}, headers=admin).status_code == 200
    for resource in ("clases", "reservas", "entrenadores"):
        assert http.get(f"/v1/{resource}", headers=token).json() == []
    values = {
        "nombre_clase": "Nueva",
        "horario": "2026-11-01T10:00:00",
        "capacidad_max": 5,
        "id_entrenador": trainers[0],
    }
    assert http.post("/v1/clases", json=values, headers=token).status_code == 403
    assert (
        http.put(url, json={"id_entrenador": trainers[0]}, headers=admin).status_code
        == 200
    )
    assert http.post("/v1/clases", json=values, headers=token).status_code == 201
    with SessionLocal.begin() as session:
        session.get(CuentaRecord, staff["id"]).rol = "cliente"
    # El vínculo residual no da privilegios de staff a un cliente.
    assert http.post("/v1/clases", json=values, headers=token).status_code == 403
    assert http.get("/v1/reservas", headers=token).json() == []


def test_binding_cannot_be_smuggled_through_public_or_profile_input(role_gym):
    http, admin, member, _, staff, _, trainers, _, _ = role_gym
    body = {"id_entrenador": trainers[0]}
    assert (
        http.patch("/v1/users/me", json=body, headers=staff["headers"]).status_code
        == 422
    )
    assert (
        http.patch(f"/v1/users/{member['id']}", json=body, headers=admin).status_code
        == 422
    )
    response = http.post(
        "/v1/auth/register",
        json={
            "nombre": "Intruso",
            "email": f"{uuid4().hex}@example.com",
            "password": "clave de pruebas",
            **body,
        },
    )
    assert response.status_code == 422
