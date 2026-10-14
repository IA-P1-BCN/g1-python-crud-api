"""Contrato HTTP de filtros, validación y documentación OpenAPI."""

import pytest


@pytest.mark.parametrize(
    "resource,params",
    [
        ("clientes", {"estado_membresia": "Desconocido"}),
        ("clientes", {"nombre": "   "}),
        ("clientes", {"q": ""}),
        ("clientes", {"email": "x" * 151}),
        ("clientes", {"fecha_inscripcion_desde": "no-es-fecha"}),
        ("clientes", {"campo_inventado": "x"}),
        ("clases", {"id_entrenador": -1}),
        ("clases", {"horario_desde": "2026-11-01T10:00:00Z"}),
        ("reservas", {"asistio": "talvez"}),
        ("reservas", {"id_clase": 0}),
        ("pagos", {"metodo_pago": "Desconocido"}),
        ("pagos", {"id_cliente": 2147483648}),
        ("pagos", {"limit": 101}),
    ],
)
def test_rechaza_filtros_invalidos(client, resource, params):
    response = client.get(f"/v1/{resource}", params=params)
    assert response.status_code == 422, response.text


@pytest.mark.parametrize(
    "resource,field,start,end",
    [
        ("clientes", "fecha_inscripcion", "2026-10-02", "2026-10-01"),
        ("clases", "horario", "2026-10-02T10:00:00", "2026-10-01T10:00:00"),
        ("reservas", "fecha_reserva", "2026-10-02T10:00:00", "2026-10-01T10:00:00"),
        ("pagos", "fecha_pago", "2026-10-02", "2026-10-01"),
    ],
)
def test_intervalo_invertido_es_400_sin_consultar_repo(
    client, repository, monkeypatch, resource, field, start, end
):
    def unexpected(*args, **kwargs):
        pytest.fail("No debe ejecutar un listado con intervalo invertido")

    monkeypatch.setattr(repository, "list", unexpected)
    response = client.get(
        f"/v1/{resource}",
        params={
            f"{field}_desde": start,
            f"{field}_hasta": end,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "El inicio del intervalo no puede superar el final"
    }


def test_openapi_documenta_filtros_y_errores(client):
    paths = client.get("/openapi.json").json()["paths"]
    expected = {
        "clientes": {
            "nombre",
            "email",
            "estado_membresia",
            "q",
            "fecha_inscripcion_desde",
            "fecha_inscripcion_hasta",
        },
        "entrenadores": {"nombre", "especialidad", "telefono", "q"},
        "clases": {
            "nombre_clase",
            "id_entrenador",
            "horario_desde",
            "horario_hasta",
            "q",
        },
        "reservas": {
            "id_cliente",
            "id_clase",
            "asistio",
            "fecha_reserva_desde",
            "fecha_reserva_hasta",
        },
        "pagos": {"id_cliente", "metodo_pago", "fecha_pago_desde", "fecha_pago_hasta"},
    }
    for resource, fields in expected.items():
        operation = paths[f"/v1/{resource}"]["get"]
        assert "requestBody" not in operation
        assert {param["name"] for param in operation["parameters"]} == fields | {
            "offset",
            "limit",
        }
        assert all(param["in"] == "query" for param in operation["parameters"])
        assert {"200", "400", "422"} <= operation["responses"].keys()
