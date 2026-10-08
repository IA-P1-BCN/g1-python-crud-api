"""Tests de integración para verificar logging en archivo."""

import time
from pathlib import Path

import httpx
import pytest

LOG_FILE = Path("logs/app.log")


@pytest.fixture(scope="module", autouse=True)
def ensure_log_file():
    """Asegura que el archivo de log existe antes de los tests."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()
    yield
    # No borramos el log para inspección manual


def _esperar_log(mensaje_esperado: str, timeout: float = 2.0) -> bool:
    """Espera a que aparezca un mensaje en el log."""
    inicio = time.monotonic()
    while time.monotonic() - inicio < timeout:
        if LOG_FILE.exists():
            contenido = LOG_FILE.read_text(encoding="utf-8")
            if mensaje_esperado in contenido:
                return True
        time.sleep(0.1)
    return False


def test_log_crear_cliente(base_url):
    """Verifica que crear un cliente genera log en archivo."""
    # Limpiar log previo para test aislado
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Crear cliente (acción crítica)
    payload = {
        "nombre": "Test Log Cliente",
        "email": "test.log.cliente@example.com",
        "estado_membresia": "Activo",
        "fecha_inscripcion": "2026-10-01",
    }
    response = httpx.post(f"{base_url}/v1/clientes", json=payload, timeout=10)
    assert response.status_code == 201
    cliente_id = response.json()["id_cliente"]

    # Verificar log en archivo
    assert _esperar_log(f"Cliente creado: id={cliente_id}"), "No se encontró log de creación de cliente"

    # Cleanup
    httpx.delete(f"{base_url}/v1/clientes/{cliente_id}", timeout=10)


def test_log_eliminar_cliente(base_url):
    """Verifica que eliminar un cliente genera log en archivo."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Crear cliente primero
    payload = {
        "nombre": "Test Log Delete",
        "email": "test.log.delete@example.com",
        "estado_membresia": "Activo",
        "fecha_inscripcion": "2026-10-01",
    }
    response = httpx.post(f"{base_url}/v1/clientes", json=payload, timeout=10)
    assert response.status_code == 201
    cliente_id = response.json()["id_cliente"]

    # Eliminar cliente (acción crítica)
    response = httpx.delete(f"{base_url}/v1/clientes/{cliente_id}", timeout=10)
    assert response.status_code == 204

    # Verificar log en archivo
    assert _esperar_log(f"Cliente eliminado: id={cliente_id}"), "No se encontró log de eliminación de cliente"


def test_log_error_404(base_url):
    """Verifica que error 404 genera log de warning."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Provocar 404
    response = httpx.get(f"{base_url}/v1/clientes/999999", timeout=10)
    assert response.status_code == 404

    # Verificar log de warning
    assert _esperar_log("Recurso no encontrado"), "No se encontró log de warning para 404"
    assert _esperar_log("/v1/clientes/999999"), "No se encontró path en log de 404"


def test_log_error_409_duplicado(base_url):
    """Verifica que error 409 (duplicado) genera log de warning."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Crear cliente
    payload = {
        "nombre": "Test Log 409",
        "email": "test.log.409@example.com",
        "estado_membresia": "Activo",
        "fecha_inscripcion": "2026-10-01",
    }
    response = httpx.post(f"{base_url}/v1/clientes", json=payload, timeout=10)
    assert response.status_code == 201
    cliente_id = response.json()["id_cliente"]

    # Intentar crear duplicado (mismo email)
    response = httpx.post(f"{base_url}/v1/clientes", json=payload, timeout=10)
    assert response.status_code == 409

    # Verificar log de warning
    assert _esperar_log("Conflicto de datos"), "No se encontró log de warning para 409"
    assert _esperar_log("POST /v1/clientes"), "No se encontró path en log de 409"

    # Cleanup
    httpx.delete(f"{base_url}/v1/clientes/{cliente_id}", timeout=10)


def test_log_crear_y_eliminar_entrenador(base_url):
    """Verifica logs para entrenador (crear + eliminar)."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Crear
    payload = {"nombre": "Test Log Entrenador", "especialidad": "Test"}
    response = httpx.post(f"{base_url}/v1/entrenadores", json=payload, timeout=10)
    assert response.status_code == 201
    entrenador_id = response.json()["id_entrenador"]

    assert _esperar_log(f"Entrenador creado: id={entrenador_id}")

    # Eliminar
    response = httpx.delete(f"{base_url}/v1/entrenadores/{entrenador_id}", timeout=10)
    assert response.status_code == 204

    assert _esperar_log(f"Entrenador eliminado: id={entrenador_id}")


def test_log_crear_y_eliminar_clase(base_url):
    """Verifica logs para clase (crear + eliminar)."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Necesita un entrenador
    entrenador = httpx.post(f"{base_url}/v1/entrenadores", json={"nombre": "Entr Log", "especialidad": "Test"}, timeout=10).json()
    entrenador_id = entrenador["id_entrenador"]

    payload = {
        "nombre_clase": "Test Log Clase",
        "horario": "2026-12-01T10:00:00",
        "capacidad_max": 5,
        "id_entrenador": entrenador_id,
    }
    response = httpx.post(f"{base_url}/v1/clases", json=payload, timeout=10)
    assert response.status_code == 201
    clase_id = response.json()["id_clase"]

    assert _esperar_log(f"Clase creada: id={clase_id}")

    # Eliminar
    response = httpx.delete(f"{base_url}/v1/clases/{clase_id}", timeout=10)
    assert response.status_code == 204

    assert _esperar_log(f"Clase eliminada: id={clase_id}")

    # Cleanup entrenador
    httpx.delete(f"{base_url}/v1/entrenadores/{entrenador_id}", timeout=10)


def test_log_crear_y_eliminar_pago(base_url):
    """Verifica logs para pago (crear + eliminar)."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    # Necesita un cliente
    cliente = httpx.post(f"{base_url}/v1/clientes", json={
        "nombre": "Test Log Pago", "email": "test.log.pago@example.com",
        "estado_membresia": "Activo", "fecha_inscripcion": "2026-10-01"
    }, timeout=10).json()
    cliente_id = cliente["id_cliente"]

    payload = {
        "id_cliente": cliente_id,
        "monto": "25.00",
        "fecha_pago": "2026-10-06",
        "metodo_pago": "Efectivo",
    }
    response = httpx.post(f"{base_url}/v1/pagos", json=payload, timeout=10)
    assert response.status_code == 201
    pago_id = response.json()["id_pago"]

    assert _esperar_log(f"Pago creado: id={pago_id}")

    # Eliminar
    response = httpx.delete(f"{base_url}/v1/pagos/{pago_id}", timeout=10)
    assert response.status_code == 204

    assert _esperar_log(f"Pago eliminado: id={pago_id}")

    # Cleanup cliente
    httpx.delete(f"{base_url}/v1/clientes/{cliente_id}", timeout=10)


def test_log_crear_y_eliminar_reserva(base_url):
    """Verifica logs para reserva (crear + eliminar)."""
    if LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    import uuid
    unique = uuid.uuid4().hex[:8]

    # Necesita cliente activo con pago y clase
    cliente = httpx.post(f"{base_url}/v1/clientes", json={
        "nombre": f"Test Log Reserva {unique}", "email": f"test.log.reserva.{unique}@example.com",
        "estado_membresia": "Activo", "fecha_inscripcion": "2026-10-01"
    }, timeout=10).json()
    cliente_id = cliente["id_cliente"]

    httpx.post(f"{base_url}/v1/pagos", json={
        "id_cliente": cliente_id, "monto": "30.00",
        "fecha_pago": "2026-10-06", "metodo_pago": "Tarjeta"
    }, timeout=10)

    entrenador = httpx.post(f"{base_url}/v1/entrenadores", json={"nombre": f"Entr Reserva {unique}", "especialidad": "Test"}, timeout=10).json()
    entrenador_id = entrenador["id_entrenador"]

    clase = httpx.post(f"{base_url}/v1/clases", json={
        "nombre_clase": f"Test Log Reserva Clase {unique}", "horario": "2026-12-01T10:00:00",
        "capacidad_max": 5, "id_entrenador": entrenador_id
    }, timeout=10).json()
    clase_id = clase["id_clase"]

    # Crear reserva
    payload = {"id_cliente": cliente_id, "id_clase": clase_id}
    response = httpx.post(f"{base_url}/v1/reservas", json=payload, timeout=10)
    assert response.status_code == 201
    reserva_id = response.json()["id_reserva"]

    assert _esperar_log(f"Reserva creada: id={reserva_id}")

    # Eliminar reserva
    response = httpx.delete(f"{base_url}/v1/reservas/{reserva_id}", timeout=10)
    assert response.status_code == 204

    assert _esperar_log(f"Reserva eliminada: id={reserva_id}")

    # Cleanup
    httpx.delete(f"{base_url}/v1/clases/{clase_id}", timeout=10)
    httpx.delete(f"{base_url}/v1/entrenadores/{entrenador_id}", timeout=10)
    httpx.delete(f"{base_url}/v1/clientes/{cliente_id}", timeout=10)