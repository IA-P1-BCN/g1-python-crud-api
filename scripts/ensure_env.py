"""Prepara .env y una clave JWT aleatoria sin sobrescribir ajustes existentes."""

import os
import re
from pathlib import Path
from secrets import token_urlsafe

from dotenv import dotenv_values


def ensure_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        contents = Path(".env.example").read_text()
        if port := os.environ.get("MYSQL_PORT"):
            contents = re.sub(
                r"(?m)^MYSQL_PORT=.*$", f"MYSQL_PORT={int(port)}", contents
            )
        with open(
            path, "x", opener=lambda name, flags: os.open(name, flags, 0o600)
        ) as file:
            file.write(contents)
    values = dotenv_values(path)
    if not values.get("SECRET_KEY"):
        contents = path.read_text()
        setting = f"SECRET_KEY={token_urlsafe(48)}"
        if re.search(r"(?m)^SECRET_KEY=.*$", contents):
            contents = re.sub(r"(?m)^SECRET_KEY=.*$", setting, contents)
        else:
            contents += f"\n{setting}\n"
        path.write_text(contents)
    path.chmod(0o600)


if __name__ == "__main__":
    ensure_env()
    print(".env preparado; SECRET_KEY no se muestra ni se guarda en Git.")
