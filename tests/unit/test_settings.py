"""Carga de las variables de entorno sensibles en `Settings`."""

import ssl

import pytest
from pydantic import ValidationError

from config.settings import Settings

SECRETO = "s3creto-de-prueba"


def test_admin_password_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", SECRETO)

    ajustes = Settings(_env_file=None)

    assert ajustes.admin_password.get_secret_value() == SECRETO


def test_admin_password_no_se_filtra_en_repr_ni_str(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", SECRETO)

    ajustes = Settings(_env_file=None)

    assert SECRETO not in repr(ajustes)
    assert SECRETO not in str(ajustes.admin_password)


def test_admin_password_es_opcional(monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    ajustes = Settings(_env_file=None)

    assert ajustes.admin_password is None


def test_error_de_configuracion_no_imprime_secretos():
    with pytest.raises(ValidationError) as error:
        Settings(
            _env_file=None,
            secret_key="clave-corta",
            admin_password="password-admin-no-publicar",
        )
    assert "clave-corta" not in str(error.value)
    assert "password-admin-no-publicar" not in str(error.value)


def test_mysql_ssl_desactivado_por_defecto(monkeypatch):
    monkeypatch.delenv("MYSQL_SSL", raising=False)

    ajustes = Settings(_env_file=None)

    assert ajustes.mysql_ssl is False
    assert ajustes.sqlalchemy_connect_args() == {}


def test_mysql_ssl_activado_por_entorno(monkeypatch):
    monkeypatch.setenv("MYSQL_SSL", "true")

    ajustes = Settings(_env_file=None)

    assert ajustes.mysql_ssl is True
    argumentos = ajustes.sqlalchemy_connect_args()
    assert isinstance(argumentos["ssl"], ssl.SSLContext)


def _generar_ca_pem(tmp_path):
    """CA autofirmada mínima, solo para probar la carga del certificado."""
    from datetime import UTC, datetime, timedelta

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID

    clave = ec.generate_private_key(ec.SECP256R1())
    nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CA de prueba")])
    ahora = datetime.now(UTC)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1))
        .not_valid_after(ahora + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(clave, hashes.SHA256())
    )
    return certificado.public_bytes(serialization.Encoding.PEM).decode()


def test_mysql_ssl_ca_acepta_contenido_pem(monkeypatch, tmp_path):
    pem = _generar_ca_pem(tmp_path)
    monkeypatch.setenv("MYSQL_SSL", "true")
    monkeypatch.setenv("MYSQL_SSL_CA", pem)

    contexto = Settings(_env_file=None).sqlalchemy_connect_args()["ssl"]

    assert contexto.cert_store_stats()["x509_ca"] == 1


def test_mysql_ssl_ca_acepta_pem_con_saltos_escapados(monkeypatch, tmp_path):
    pem = _generar_ca_pem(tmp_path).replace("\n", "\\n")
    monkeypatch.setenv("MYSQL_SSL", "true")
    monkeypatch.setenv("MYSQL_SSL_CA", pem)

    contexto = Settings(_env_file=None).sqlalchemy_connect_args()["ssl"]

    assert contexto.cert_store_stats()["x509_ca"] == 1


def test_mysql_ssl_ca_acepta_ruta_a_fichero(monkeypatch, tmp_path):
    fichero = tmp_path / "ca.pem"
    fichero.write_text(_generar_ca_pem(tmp_path))
    monkeypatch.setenv("MYSQL_SSL", "true")
    monkeypatch.setenv("MYSQL_SSL_CA", str(fichero))

    contexto = Settings(_env_file=None).sqlalchemy_connect_args()["ssl"]

    assert contexto.cert_store_stats()["x509_ca"] == 1


def test_cors_origins_vacio_por_defecto(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    ajustes = Settings(_env_file=None)

    assert ajustes.cors_origins == []


def test_cors_origins_se_separa_por_comas(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_ORIGINS", "https://gimnasio.onrender.com, http://localhost:5173"
    )

    ajustes = Settings(_env_file=None)

    assert ajustes.cors_origins == [
        "https://gimnasio.onrender.com",
        "http://localhost:5173",
    ]
