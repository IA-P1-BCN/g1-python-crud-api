# AGENTS.md — Decisiones del proyecto

Decisiones acordadas para `g1-python-crud-api`. Cualquier cambio de estas
convenciones debe actualizarse aquí en el mismo PR.

## Contexto del equipo y asignación

- El proyecto se realiza en un grupo de **5 personas**.
- El **6 de octubre de 2026**, según lo indicado por la usuaria, se le asignó
  la [issue #10 — API REST con operaciones CRUD básicas](https://github.com/IA-P1-BCN/g1-python-crud-api/issues/10).
  En GitHub figura asignada a **Fabiana Leonardo (`fabileoruf`)**.
- La descripción de la issue #10 indica que depende de que estén completas
  las tareas **#1 y #2**.

## Alcance vigente: V1 (GymFlow)

- La usuaria confirmó que se debe usar `docs/client/CLIENT_SPECS.md` (V1),
  junto con `docs/PRD.md`, `docs/DATABASE_SPEC.md` y `docs/EDR_DIAGRAM.md`.
  `CLIENT_SPECS_V2_USER_MNG.md` no define el alcance de esta entrega.
- #10 implementa CRUD de clientes, entrenadores, clases, reservas y pagos,
  las migraciones correspondientes y datos ficticios con `task seed`.
- Se incluyen los campos opcionales `fecha_inscripcion`, `telefono` y
  `metodo_pago`, y los estados `Activo`, `Inactivo` y `Suspendido`, según la
  confirmación de la usuaria.
- Las reservas nuevas o trasladadas requieren un cliente activo, al menos
  un pago y una plaza disponible. No se calcula caducidad de pagos porque
  el modelo no define periodos de membresía.
- `UNIQUE (id_cliente, id_clase)` impide reservas duplicadas; un bloqueo de
  la clase dentro de la transacción protege el aforo. Las FK usan `RESTRICT`
  para impedir el borrado de registros con dependencias (HTTP 409).
- `PUT` sustituye todos los campos editables; los opcionales omitidos quedan
  en `null` y `asistio` vuelve a `false` si se omite. La fecha de reserva se
  genera en el servidor y se conserva al actualizar. Fechas/hora: UTC sin zona
  en los campos MySQL `DATETIME`. `DELETE /v1/reservas/{id_reserva}` libera cupo.
- Los endpoints V1 son públicos; JWT, roles y `SECRET_KEY` no son requisitos
  de #10. La entrega CRUD no cierra las tareas independientes del equipo.

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
- Carpetas raíz: `core/` (utilidades transversales, p. ej. logging),
  `config/` (settings), `logs/` (salida de logs), `tests/` (suite de
  tests), `migrations/` (Alembic), `docs/` (documentación, incluida
  la del cliente en `docs/client/`).

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
- ORM: SQLAlchemy 2.x. Modelos en `src/infrastructure/database/models/`,
  un archivo por entidad: `cliente.py`, `entrenador.py`, `clase.py`,
  `reserva.py`, `pago.py` y `version.py`. Todos usan la misma `Base` de
  `base.py`; `__init__.py` los exporta y registra sus tablas para Alembic.
- Migraciones: Alembic (`migrations/`); `env.py` toma la URL de
  `config/settings.py`, no de alembic.ini.
- La tabla `versions` se crea y se **siembra por migración** (versión inicial
  `0.1`). `GET /health/db` lee la última versión de esa tabla: la versión no
  se hardcodea en el código.
- Nueva migración: `uv run alembic revision -m "descripcion"` y editar el
  fichero generado en `migrations/versions/`.

## Configuración y entorno

- Variables en `.env` (ver `.env.example`), leídas con pydantic-settings:
  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
  y `ADMIN_PASSWORD` (#6).
- `ADMIN_PASSWORD` es opcional (`SecretStr | None`, sin valor por defecto en el
  código): V1 no tiene endpoints que la usen. Cuando una funcionalidad la
  requiera, debe pasar a obligatoria para que la app falle al arrancar si falta.
- Los secretos se declaran como `SecretStr` y se leen con
  `get_secret_value()` solo en el punto donde se usan.
  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`,
  `LOG_LEVEL`, `LOG_FILE`.
- `.env` nunca se commitea (está en .gitignore); commitea solo `.env.example`.

## Logging

- Configuración en `core/logging.py` (`setup_logging`), llamada al arrancar
  desde `main.py` con `LOG_LEVEL` y `LOG_FILE` (por defecto `INFO` y
  `logs/app.log`).
- Dos handlers: **consola** (stdout) y **fichero rotativo** en `logs/`
  (1 MB, 3 backups, utf-8). Formato:
  `2026-10-06 10:00:00 | INFO     | logger | mensaje`.
- `setup_logging` es **idempotente**: repetirla (recarga de uvicorn, tests)
  no duplica handlers; un `LOG_LEVEL` desconocido cae a `INFO`.
- `sqlalchemy.engine` y `uvicorn.access` se dejan en `WARNING` para que la
  salida sea limpia.
- `logs/` está ignorado salvo `.gitkeep` (`.gitignore`: `logs/*`, `*.log`).
- Dónde se loguea: arranque y cierre de la app (`main.py`, con `lifespan`).
- Tests: `tests/unit/test_logging.py` (fichero de salida en `tmp_path`, nivel
  e idempotencia).

## Tooling

- **uv** gestiona dependencias y entorno virtual (`pyproject.toml` + `uv.lock`).
  No se usa pip ni requirements.txt.
- **Taskfile** expone las tareas: `demo`, `install`, `test`, `lint`, `fmt`,
  `dev`, `start`, `db:up`, `db:down`, `migrate`, `seed`. `task demo` monta el
  proyecto desde cero (dependencias, `.env`, MySQL, migraciones, demo y tests).

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
- `main` está protegida: los cambios entran solo vía PR con 1 approval.

## Pendiente por issue

- #1 tema gimnasio (nombre de la app), #2/#3 modelos y diagrama ER,
  #7 logging en `logs/` (con reglas de ignore), #8 manejo de excepciones,
  #10 CRUD bajo `/v1`. #9 (documentación Swagger) quedó parcialmente cubierto
  por esta estructura. #6 (variables sensibles) queda resuelta con
  `ADMIN_PASSWORD` en `.env.example` y `config/settings.py`.
  #8 manejo de excepciones, #10 CRUD bajo `/v1`. #6 (variables sensibles)
  y #9 (documentación Swagger) quedaron parcialmente cubiertos por esta
  estructura; #7 (logging) queda cubierto por `core/logging.py`.
