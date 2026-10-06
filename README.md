# g1-python-crud-api

[![Tests](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge-v2.json)](https://github.com/astral-sh/ruff)

API CRUD con FastAPI (proyecto 2, tema gimnasio).

Requisitos: [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), Docker.

## Ejecutar

```bash
task install          # instala dependencias
cp .env.example .env  # variables de entorno (MySQL)
task db:up            # levanta MySQL (docker compose)
task migrate          # aplica migraciones (alembic)
task dev              # servidor con recarga en http://127.0.0.1:8000
```

## Swagger

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Healthchecks: `GET /health` · `GET /health/db`

## Tests

```bash
task db:up && task migrate && task test
```

(los tests que necesitan MySQL se saltan si no está disponible)

## Comandos

| Comando | Descripción |
|---|---|
| `task demo` | Monta todo desde cero (deps, `.env`, MySQL, migraciones y tests) |
| `task install` | Instala dependencias (`uv sync`) |
| `task test` | Ejecuta la suite de tests (`pytest`) |
| `task lint` | Comprueba PEP 8 (`ruff check`) |
| `task fmt` | Formatea el código (`ruff format`) |
| `task dev` | Servidor con recarga (`uvicorn --reload`) |
| `task start` | Servidor sin recarga |
| `task db:up` | Levanta MySQL (`docker compose up -d --wait`) |
| `task db:down` | Detiene MySQL |
| `task migrate` | Aplica migraciones (`alembic upgrade head`) |

## Enlaces

- [AGENTS.md](AGENTS.md) — convenciones y decisiones del proyecto
- [docs/client/CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md) — especificación del cliente
