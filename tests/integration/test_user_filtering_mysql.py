"""Combinaciones y paginación sobre resultados filtrados en MySQL."""

from datetime import UTC, datetime
from uuid import uuid4

from src.infrastructure.database.engine import SessionLocal
from src.infrastructure.database.models import CuentaRecord


def test_filtros_combinados_y_literales(accounts_api):
    client, emails = accounts_api
    marker = uuid4().hex
    rows = []
    for i, name in enumerate(["Admin", "Ana_100%/X", "AnaX100algo/X", "Socio"]):
        email = f"{marker}.{i}@example.com"
        emails.append(email)
        response = client.post(
            "/v1/auth/register",
            json={
                "nombre": f"{marker} {name}",
                "email": email,
                "password": "contraseña de prueba",
                "crear_cliente": i == 3,
            },
        )
        assert response.status_code == 201, response.text
        rows.append(response.json())
    token = client.post(
        "/v1/auth/login",
        data={"username": emails[0], "password": "contraseña de prueba"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    with SessionLocal.begin() as session:
        for i, row in enumerate(rows):
            record = session.get(CuentaRecord, row["id"])
            record.fecha_creacion = datetime(2026, 10, i + 1, 12, tzinfo=UTC).replace(
                tzinfo=None
            )
            record.activo = i != 1
            record.rol = "staff" if i in {1, 2} else "cliente"
    rows = [client.get(f"/v1/users/{r['id']}", headers=headers).json() for r in rows]

    def listed(**params):
        response = client.get("/v1/users", params=params, headers=headers)
        assert response.status_code == 200, response.text
        assert "password" not in response.text
        return response.json()

    assert listed(q=marker.upper()) == rows
    assert listed(q=marker, rol="staff", offset=1, limit=1) == [rows[2]]
    assert listed(q=marker, activo="false") == [rows[1]]
    assert listed(q=marker, nombre="_100%/X") == [rows[1]]
    assert listed(q=f"{marker}.3@") == [rows[3]]
    assert listed(q=marker, email=".2@EXAMPLE", activo="true") == [rows[2]]
    assert listed(id_cliente=rows[3]["id_cliente"]) == [rows[3]]
    assert (
        listed(
            q=marker,
            fecha_creacion_desde="2026-10-02T12:00:00",
            fecha_creacion_hasta="2026-10-03T12:00:00",
        )
        == rows[1:3]
    )
    assert listed(q=marker, fecha_creacion_hasta="2026-10-01T12:00:00") == [rows[0]]
    assert listed(q="' OR 1=1 --") == []
