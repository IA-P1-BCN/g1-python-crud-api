"""Fixtures compartidas de los tests de integración."""

import threading
import time

import pytest
import uvicorn


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
