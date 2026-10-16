"""La SPA admite enlaces profundos sin convertir errores de API en HTML."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.interfaces.http.spa import mount_spa


def test_spa_archivos_rutas_y_prioridad_api(tmp_path):
    (tmp_path / "index.html").write_text("<app-root>portal</app-root>")
    (tmp_path / "main.js").write_text("console.log('portal')")
    app = FastAPI()

    @app.get("/v1/example")
    def example():
        return {"ok": True}

    mount_spa(app, tmp_path)
    with TestClient(app) as client:
        for path in ["/", "/clases", "/perfil", "/portal/clases"]:
            response = client.get(path)
            assert response.status_code == 200
            assert response.text == "<app-root>portal</app-root>"
            assert response.headers["content-type"].startswith("text/html")
        assert client.head("/clases").status_code == 200
        assert client.get("/main.js").text == "console.log('portal')"
        assert client.get("/v1/example").json() == {"ok": True}
        assert client.get("/docs").status_code == 200
        for path in ["/v1/no-existe", "/missing.js", "/clases/missing.js"]:
            response = client.get(path)
            assert response.status_code == 404
            assert response.headers["content-type"].startswith("application/json")
        assert client.post("/clases").status_code == 405


def test_sin_build_no_monta_spa(tmp_path):
    app = FastAPI()
    mount_spa(app, tmp_path)
    with TestClient(app) as client:
        assert client.get("/").status_code == 404
