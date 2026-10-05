# AGENTS.md — Decisiones del proyecto

Decisiones acordadas para `g1-python-crud-api`. Cualquier cambio de estas
convenciones debe actualizarse aquí en el mismo PR.

## Arquitectura por capas (src/)

```
src/
├── domain/           # entidades y puertos (Protocol). Sin dependencias externas.
├── application/      # casos de uso. Depende solo del dominio.
├── infrastructure/   # adaptadores (SQLAlchemy, repositorios). Implementa puertos.
└── interfaces/       # entrada HTTP: routes/, controllers/, schemas/.
```

- Dirección de dependencias: `interfaces → application → domain`;
  `infrastructure` implementa los puertos del dominio y **nunca** es importada
  por domain/application. El único punto donde interfaces toca infrastructure
  es el wiring de dependencias (Depends).
- Pydantic (schemas de la API) vive solo en `src/interfaces/http/schemas/`.
  El dominio usa dataclasses y `Protocol`.
- Flujo de una petición: route → controller → use case → entidad de dominio,
  y de vuelta al schema de respuesta.
- Carpetas raíz: `config/` (settings), `logs/` (salida de logs), `tests/`
  (suite de tests), `migrations/` (Alembic).

## Endpoints

- Healthchecks en la raíz: `GET /health` (app) y `GET /health/db` (MySQL +
  versión de esquema; 503 si no hay conexión).
- Los endpoints de negocio van bajo el prefijo `/v1` al incluir sus routers.
- Todo endpoint declara `tags`, `summary` y `response_model` para que la
  documentación Swagger quede completa.

## Documentación (Swagger / OpenAPI)

- Swagger UI: `http://127.0.0.1:8000/docs` · ReDoc: `/redoc` ·
  spec OpenAPI: `/openapi.json`.
- El título, versión y descripción de la app se configuran en `main.py`.

## Base de datos (MySQL + SQLAlchemy + Alembic)

- Motor: MySQL 8.4, levantado con `task db:up` (docker-compose.yml).
- ORM: SQLAlchemy 2.x. Modelos en `src/infrastructure/database/models.py`.
- Migraciones: Alembic (`migrations/`); `env.py` toma la URL de
  `config/settings.py`, no de alembic.ini.
- La tabla `versions` se crea y se **siembra por migración** (versión inicial
  `0.1`). `GET /health/db` lee la última versión de esa tabla: la versión no
  se hardcodea en el código.
- Nueva migración: `uv run alembic revision -m "descripcion"` y editar el
  fichero generado en `migrations/versions/`.

## Configuración y entorno

- Variables en `.env` (ver `.env.example`), leídas con pydantic-settings:
  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.
- `.env` nunca se commitea (está en .gitignore); commitea solo `.env.example`.

## Tooling

- **uv** gestiona dependencias y entorno virtual (`pyproject.toml` + `uv.lock`).
  No se usa pip ni requirements.txt.
- **Taskfile** expone las tareas: `demo`, `install`, `test`, `lint`, `fmt`,
  `dev`, `start`, `db:up`, `db:down`, `migrate`. `task demo` monta el proyecto
  desde cero (dependencias, `.env`, MySQL, migraciones y tests).

## Estilo (PEP 8)

- Se aplica y verifica con **ruff** (`task lint`, `task fmt`), line-length 88.
- Un cambio no se considera terminado si `task lint` o `task test` fallan.

## Tests

- Suite en `tests/`; los de integración en `tests/integration/`.
- Integración real: fixture que arranca uvicorn in-process (127.0.0.1, puerto
  efímero) y hace peticiones HTTP con httpx contra el servidor vivo.
- Los tests que necesitan MySQL se saltan con un mensaje claro si la base de
  datos no está disponible (`task db:up && task migrate`).
- Flujo completo local: `task db:up && task migrate && task test`.

## Git

- Ramas: `feature/<tema>` en minúsculas, sin tildes ni espacios
  (p. ej. `feature/estructura-fastapi-health`).
- **Conventional Commits**: `type(scope)?: descripcion` — tipos `feat`, `fix`,
  `docs`, `test`, `refactor`, `chore`, `build`; descripción en español,
  minúsculas e imperativo; `!` para cambios rompientes
  (p. ej. `feat(health): añade healthcheck de base de datos`).
- Flujo: issue → rama → commit → PR a `main` con `Closes #N` → review → merge.

## Pendiente por issue

- #1 tema gimnasio (nombre de la app), #2/#3 modelos y diagrama ER,
  #7 logging en `logs/` (con reglas de ignore), #8 manejo de excepciones,
  #10 CRUD bajo `/v1`. #6 (variables sensibles) y #9 (documentación Swagger)
  quedaron parcialmente cubiertos por esta estructura.
