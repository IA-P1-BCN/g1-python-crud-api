"""Fixtures compartidas de los tests de integración."""

import threading
import time
from uuid import uuid4

import httpx
import pytest
import uvicorn
from sqlalchemy import delete, inspect, text
from sqlalchemy.exc import OperationalError

from src.infrastructure.database.engine import SessionLocal, engine
from src.infrastructure.database.models import ClienteRecord, CuentaRecord


@pytest.fixture(scope="session")
def live_server():
    """Arranca uvicorn in-process en un hilo, con puerto efímero."""
    config = uvicorn.Config("main:app", host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    limite = time.monotonic() + 10
    while not server.started and time.monotonic() < limite:
        time.sleep(0.05)
    if not server.started:
        pytest.fail("el servidor uvicorn no llegó a arrancar")
    yield server
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def base_url(live_server):
    """URL base del servidor vivo."""
    puerto = live_server.servers[0].sockets[0].getsockname()[1]
    return f"http://127.0.0.1:{puerto}"


@pytest.fixture
def accounts_api(base_url):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("MySQL no disponible: ejecuta task db:up y task migrate")
    assert inspect(engine).has_table("users"), "Aplica task migrate"
    emails = []
    with httpx.Client(base_url=base_url, timeout=10) as client:
        try:
            yield client, emails
        finally:
            with SessionLocal.begin() as session:
                session.execute(
                    delete(CuentaRecord).where(CuentaRecord.email.in_(emails))
                )
                session.execute(
                    delete(ClienteRecord).where(ClienteRecord.email.in_(emails))
                )


@pytest.fixture
def gym_admin_headers(accounts_api):
    """Cuenta aislada: registro/login reales, rol preparado en persistencia."""
    client, emails = accounts_api
    email = f"{uuid4().hex}@example.com"
    emails.append(email)
    response = client.post(
        "/v1/auth/register",
        json={"nombre": "Admin test", "email": email, "password": "clave de pruebas"},
    )
    assert response.status_code == 201, response.text
    with SessionLocal.begin() as session:
        session.get(CuentaRecord, response.json()["id"]).rol = "admin"
    response = client.post(
        "/v1/auth/login", data={"username": email, "password": "clave de pruebas"}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_http(base_url, gym_admin_headers):
    with httpx.Client(
        base_url=base_url, headers=gym_admin_headers, timeout=10
    ) as client:
        yield client
