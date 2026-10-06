"""La configuración y las credenciales locales se crean sin perder ajustes."""

import stat

from dotenv import dotenv_values

from scripts.ensure_env import ensure_env
from scripts.seed_users import demo_credentials


def test_env_genera_clave_y_preserva_ajustes(tmp_path):
    path = tmp_path / ".env"
    path.write_text("MYSQL_PORT=3307\nMYSQL_PASSWORD=custom-local-test\nSECRET_KEY=\n")
    ensure_env(path)
    first = path.read_text()
    values = dotenv_values(path)
    assert len(values["SECRET_KEY"]) >= 32
    assert values["MYSQL_PASSWORD"] == "custom-local-test"
    assert values["MYSQL_PORT"] == "3307"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    ensure_env(path)
    assert path.read_text() == first


def test_credenciales_demo_no_se_regeneran(tmp_path):
    path = tmp_path / ".env.demo"
    first = demo_credentials(path)
    assert len(first["DEMO_ADMIN_PASSWORD"]) >= 12
    assert first["DEMO_ADMIN_PASSWORD"] != first["DEMO_USER_PASSWORD"]
    assert demo_credentials(path) == first
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
