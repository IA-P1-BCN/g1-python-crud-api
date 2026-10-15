"""Deja `.env` listo para arrancar: rellena secretos y elige puerto MySQL libre.

Solo añade: nunca sobrescribe un valor ya configurado y no vacío.
"""

import re
import secrets
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

MARCADORES_ADMIN = ("change-me", "cambia-", "replace-")
PUERTOS_ALTERNATIVOS = range(3307, 3317)
CONTENEDOR_MYSQL = "gym-mysql"


def puerto_libre(puerto: int) -> bool:
    """True si 127.0.0.1:puerto está libre (sonda portable, sin lsof)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", puerto))
        except OSError:
            return False
    return True


def puertos_contenedor_propio() -> set[int]:
    """Puertos host que publica nuestro contenedor gym-mysql.

    Si el propio MySQL del proyecto ocupa el puerto, no es un conflicto:
    es la base de datos con la que hay que hablar.
    """
    try:
        salida = subprocess.run(
            ["docker", "ps", "--filter", f"name={CONTENEDOR_MYSQL}", "--format", "{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return {int(puerto) for puerto in re.findall(r":(\d+)->", salida)}


def elegir_puerto(config: dict[str, str]) -> tuple[int, bool]:
    """Devuelve (puerto, cambió) según MYSQL_PORT y los puertos libres."""
    preferido = int(config.get("MYSQL_PORT") or 3306)
    propios = puertos_contenedor_propio()
    if preferido in propios or puerto_libre(preferido):
        return preferido, False
    for candidato in PUERTOS_ALTERNATIVOS:
        if candidato not in propios and puerto_libre(candidato):
            return candidato, True
    raise SystemExit(
        f"No hay puerto libre para MySQL (probados {preferido} y "
        f"{PUERTOS_ALTERNATIVOS.start}-{PUERTOS_ALTERNATIVOS.stop - 1}); "
        "libera uno o fija MYSQL_PORT a mano en .env"
    )


def parsear(texto: str) -> dict[str, str]:
    valores: dict[str, str] = {}
    for linea in texto.splitlines():
        clave, _, valor = linea.partition("=")
        clave = clave.strip()
        if clave and not clave.startswith("#"):
            valores[clave] = valor.strip()
    return valores


def rellenar(config: dict[str, str]) -> list[str]:
    """Completa secretos vacíos o marcadores; devuelve lo rellenado."""
    cambios: list[str] = []
    if len(config.get("SECRET_KEY", "")) < 32:
        config["SECRET_KEY"] = secrets.token_urlsafe(48)
        cambios.append("SECRET_KEY generada (>= 32 caracteres)")
    password = config.get("ADMIN_PASSWORD", "")
    if (
        len(password) < 12
        or password.lower().startswith(MARCADORES_ADMIN)
    ):
        config["ADMIN_PASSWORD"] = secrets.token_urlsafe(16)
        cambios.append("ADMIN_PASSWORD generada (12-128 caracteres)")
    return cambios


def escribir(config: dict[str, str], extra: dict[str, str]) -> None:
    """Regenera .env desde la plantilla del example, claves extra al final."""
    lineas: list[str] = []
    for linea in EXAMPLE_PATH.read_text(encoding="utf-8").splitlines():
        clave, sep, _ = linea.partition("=")
        if sep and not clave.strip().startswith("#"):
            lineas.append(f"{clave.strip()}={config[clave.strip()]}")
        else:
            lineas.append(linea)
    lineas.extend(f"{clave}={valor}" for clave, valor in extra.items())
    ENV_PATH.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> int:
    actual = parsear(ENV_PATH.read_text(encoding="utf-8")) if ENV_PATH.exists() else {}
    ejemplo = parsear(EXAMPLE_PATH.read_text(encoding="utf-8"))

    # Lo ya configurado (no vacío) manda sobre la plantilla; las claves
    # propias del .env viejo que no están en la plantilla se conservan.
    config = ejemplo | {k: v for k, v in actual.items() if v}
    extra = {k: v for k, v in actual.items() if k not in ejemplo and v}

    cambios = rellenar(config)
    puerto, cambio_puerto = elegir_puerto(config)
    if cambio_puerto:
        config["MYSQL_PORT"] = str(puerto)
        cambios.append(f"MYSQL_PORT={puerto} (el preferido está ocupado)")

    escribir(config, extra)

    if cambios:
        print("`.env` preparado:")
        for cambio in cambios:
            print(f"  - {cambio}")
        if not ENV_PATH.exists():
            print("  (los valores están en .env, que no se sube a Git)")
    else:
        print("`.env` ya está completo: no se cambia nada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
