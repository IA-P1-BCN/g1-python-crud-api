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

## Alcance vigente: V1 + V2 (GymFlow con gestión de usuarios)

- El alcance es la **suma** de `docs/client/CLIENT_SPECS.md` (V1, entregada)
  y `docs/client/CLIENT_SPECS_V2_USER_MNG.md` (V2, integrada el 2026-10-14),
  junto con `docs/PRD.md`, `docs/DATABASE_SPEC.md` y `docs/EDR_DIAGRAM.md`.
- El plan V2 se migró del proyecto `g1_user_management_api` (su repo y código
  NO son referencia; solo se migró el plan de su Projects) y se repartió por
  niveles: V2-Esencial → milestone #2 (Nivel medio), V2-Medio+Avanzado →
  milestone #3 (Nivel Avanzado), V2-Experto → milestone #4 (Nivel Experto).
- **Cuenta ≠ Cliente** (ADR `docs/adr/0001-cuenta-separada-de-cliente.md`,
  glosario en `CONTEXT.md`): tabla `users` (email único, `password_hash`,
  `activo`, Rol) separada de `clientes`, con vínculo 1:1 opcional. Roles:
  `admin`, `staff`, `cliente`. Los endpoints V2 son literales a la spec:
  `/v1/auth/register`, `/v1/auth/login`, `/v1/users/me`, `/v1/users`;
  `/v1/clientes` sigue siendo el CRUD de perfil del gimnasio.
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
- Los endpoints V1 entregados son públicos por ahora; los nuevos endpoints de
  V2 `/v1/users*` exigen token desde su primer PR. Registro y login son públicos; la
  protección del resto de `/v1` llega con la STORY #38 (milestone #3).
  `SECRET_KEY` pasa a variable obligatoria cuando se integre el JWT
  (`SecretStr`, solo en `.env`/`.env.example`).

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
- Exportación a CSV: un único endpoint `GET /v1/export/csv?tablas=<tabla>`
  (issue #18), con `tablas` como enum de las tablas (`ExportTable`) para que
  FastAPI valide y devuelva 422 si no existe. Ignora la paginación (`list_all`
  en puerto, repositorio y caso de uso), ordena por ID y devuelve `text/csv`
  con BOM UTF-8 y `Content-Disposition: attachment`. El nombre de tabla →
  entidad vive en `src/interfaces/http/csv_exports.py` (`TABLES`) y las
  columnas en `CSV_FIELDS`, con el ID primero. El endpoint usa
  `response_class=Response` y documenta el 200 como `text/csv` (no tiene
  `response_model` JSON).
- No se exportan datos a formato distinto de CSV; para añadir otro formato se
  crearía un helper análogo a `csv_exports.py`.

## Listados filtrados (#22)

- Los cinco GET de listado aceptan filtros tipados en
  `src/interfaces/http/schemas/list_query.py`. Los controladores los convierten
  a `ListFilters` (dataclass de dominio); SQLAlchemy los aplica antes de paginar.
- Texto: fragmentos literales, sin distinguir mayúsculas; escapar `%`, `_` y el
  carácter de escape en LIKE. `q` agrupa campos de texto con OR; los filtros
  distintos se combinan con AND. Mantener orden por ID y `limit <= 100`.
- Rangos inclusivos; DATE y DATETIME UTC sin zona, según el campo. Los valores
  null no coinciden con un filtro explícito sobre ese campo.
- Tipos/valores/parámetros desconocidos inválidos → 422. El caso de uso rechaza
  un intervalo invertido con `InvalidQueryError` → 400; `LIST_ERRORS` lo documenta.
- La exportación CSV sigue usando `list_all`, sin filtros ni paginación. Los
  filtros de cuentas (#61) usan el mismo contrato con protección JWT (#56).

## Manejo de errores

- Las capas internas lanzan errores de dominio (`src/domain/errors.py`:
  `NotFoundError`, `ConflictError`, `RepositoryUnavailableError`); solo la capa
  `interfaces` decide el código HTTP (`src/interfaces/http/errors.py`).
- Correspondencia: `InvalidQueryError` → 400, `AuthenticationError` → 401,
  `ForbiddenError` → 403, `NotFoundError` → 404, `ConflictError` → 409, validación de
  FastAPI → 422, `RepositoryUnavailableError` → 503 y cualquier otra excepción
  → 500.
- 401 incluye `WWW-Authenticate: Bearer`; 403 no pide reautenticación.
  403 actual significa Cuenta autenticada inactiva; permisos por rol son #65.
- Settings oculta valores de entrada al representar errores de configuración.
  Validación de auth/users omite input/ctx para no reflejar credenciales.
- Todo error responde `{"detail": "mensaje"}` (los 422 llevan una lista, formato
  FastAPI). El 500 devuelve siempre `Error interno del servidor`: ni trazas ni
  detalles internos salen al cliente.
- Se registran en el log (nivel ERROR, con traza) solo los 500 y los 503. Los
  errores del cliente (404, 409, 422) no se registran como error.
- `CRUD_ERRORS` documenta 404, 409, 500 y 503 en Swagger; FastAPI añade el 422.
- Un error de dominio nuevo se declara en `src/domain/errors.py`, se traduce en
  `register_crud_error_handlers` y se prueba en `tests/unit/test_errores.py`.

## Errores documentados de auth/Cuentas (#60)

- `LOGIN_ERRORS`: 401 genérico con ejemplo y cabecera WWW-Authenticate.
  `PROTECTED_ERRORS`: 401/403 con ejemplos y semántica actual.
  `LIST_ERRORS`: 400 para rango invertido, también en listado de Cuentas.
- No inventar errores no observables: registro/login públicos no reciben
  401 por token ni 403 por desactivación posterior. Swagger y ReDoc leen la
  misma especificación, comprobada por HTTP en la suite.

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

## Filtros de Cuentas (#61)

- GET `/v1/users` acepta nombre/email por fragmento, q con OR entre ambos,
  activo/rol/id_cliente exactos y fecha_creacion_desde/hasta inclusivas UTC sin zona.
- Combinar con AND antes de paginar; conservar false, escapar comodines literales.
  `CuentaQuery` → `ListFilters`; constructor SQL compartido con V1.
- Parámetros inválidos/desconocidos → 422, rango invertido → 400.

## Baja de Cuentas (#59)

- DELETE `/v1/users/{id}` requiere Cuenta activa autenticada, borra físicamente
  y responde 204 sin cuerpo. Inexistente → 404. Conserva Cliente e historial.
- Los tokens de una Cuenta borrada devuelven 401 al resolver su identidad.
- Soft delete y restricción admin-only siguen en #73 y #65 respectivamente.

## Edición de Cuentas (#58)

- PUT/PATCH `/v1/users/{id}` exigen Cuenta activa autenticada. Solo nombre,
  email y password son editables; rol, activo y vínculo siguen fuera del contrato.
- PUT exige nombre/email; password omitida conserva hash (excepción explícita
  al reemplazo de campos del CRUD V1, según #58). PATCH conserva los omitidos.
- Null explícito, PATCH vacío o campo protegido → 422; duplicado → 409,
  inexistente → 404. La edición bloquea la fila y conserva fecha de creación.
- Contraseña nueva siempre Argon2 y literal. #66 sigue cubriendo el flujo propio
  con verificación de la contraseña actual.

## Consulta de Cuentas (#57)

- GET `/v1/users` y `/v1/users/{id}` exigen Cuenta activa autenticada.
  Listado por id, offset >= 0, limit 1–100. Id inexistente → 404.
- Respuesta CuentaResponse sin credenciales; parámetros desconocidos → 422.
- Restricción de listado a admin sigue siendo el alcance independiente de #65.

## Perfil autenticado (#56)

- `get_current_user` verifica JWT y vuelve a leer Cuenta: sin identidad válida
  (incluida Cuenta borrada) → 401 Bearer; Cuenta inactiva tras login → 403.
- GET `/v1/users/me` usa CuentaResponse sin credenciales. Se registra antes
  de `/{id}`. La dependencia finaliza su transacción antes del CRUD protegido.
- La autorización granular por roles permanece en #64/#65.

## Autenticación (#55)

- POST `/v1/auth/login` usa formulario OAuth2: `username` es el email y
  `password` se conserva literal. Registro y login son públicos.
- Cuenta inexistente, contraseña incorrecta o Cuenta inactiva → mismo 401
  con `WWW-Authenticate: Bearer`. Se verifica un hash ficticio para email inexistente.
- JWT HS256, sub=id string, iat, exp de 30 minutos, iss=gymflow y aud=gymflow-api.
  Validación exige firma, algoritmo fijo y todas las claims; expiración configurable
  queda en #67. SECRET_KEY obligatoria sin valor por defecto.
- Swagger declara OAuth2 password flow con tokenUrl `v1/auth/login`.
- `tests/conftest.py` y CI configuran secretos exclusivos de prueba; nunca usar
  esos valores para desplegar.

## Registro (#54)

- POST `/v1/auth/register`: nombre, email y password (12–128 caracteres);
  `crear_cliente=false` por defecto. True crea Cliente Inactivo nuevo en la
  misma transacción; nunca vincula uno existente por email. Duplicados → 409.
- Rol cliente y activo=true se fijan en servidor. Entrada rechaza rol, activo
  e id_cliente. Salida sin password ni hash, incluso en errores 422.
- Email normalizado en minúsculas; contraseña literal, sin recortar espacios.

## Cuentas (#53)

- `Cuenta` vive en dominio y `CuentaRecord` en la tabla `users`;
  `id_cliente` es nullable, UNIQUE y FK RESTRICT. Borrar Cuenta conserva Cliente.
- Contraseñas Argon2id mediante `PasswordHasher` (Protocol) y pwdlib en infraestructura.
  Los hashes no aparecen en repr de Cuenta ni en respuestas HTTP.
- El seed crea admin y cuentas inactivas para clientes con email válido; no inventa
  emails ni comparte contraseñas. Omite conflictos sin vincular identidades ajenas.
- El rol mínimo permite el admin del seed; la política completa de roles sigue
  en #64/#65. `SECRET_KEY` es SecretStr obligatoria (mínimo 32 caracteres) desde JWT (#55).

## Configuración y entorno

- Variables en `.env` (ver `.env.example`), leídas con pydantic-settings:
  `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`,
  `MYSQL_SSL` (TLS para MySQL gestionados, p. ej. Aiven), `ALLOWED_ORIGINS`
  (orígenes CORS del frontend, separados por comas) y `ADMIN_PASSWORD` (#6).
- `ADMIN_PASSWORD` es opcional (`SecretStr | None`, sin valor por defecto en el
  código) para arrancar la API, pero **obligatoria para `task seed`**: se valida
  antes de escribir (12–128 caracteres, sin marcadores). `ADMIN_EMAIL` identifica
  al administrador inicial; repetir el seed no restablece sus credenciales.
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

## Skills del equipo (#79)

- Se versionan dos skills en `.opencode/skills/`: `gymflow-verify` comprueba
  una entrega y su evidencia; `gymflow-review` revisa el diff contra la spec,
  las capas y las reglas de negocio.
- OpenCode las descubre automáticamente. Sus comandos son `/gymflow-verify`
  y `/gymflow-review`, definidos en `.opencode/commands/`; aceptan el alcance
  de la revisión como texto. Usan el agente/modelo ya configurado por la persona.
- Otros agentes pueden leer directamente el `SKILL.md` correspondiente y
  seguirlo; no se instala configuración global ni se presupone autodetección
  fuera de OpenCode.
- Ejemplo: `/gymflow-review cambios de la issue #22 frente a origin/main`.
  Para verificar una entrega, `/gymflow-verify rama actual`.
- Registrar su uso real en `docs/ai-log.md`. Estas skills no autorizan publicar,
  aprobar ni mergear; la revisión humana continúa siendo obligatoria.

## Tooling

- **uv** gestiona dependencias y entorno virtual (`pyproject.toml` + `uv.lock`).
  No se usa pip ni requirements.txt.
- **Taskfile** expone las tareas: `demo`, `install`, `test`, `lint`, `fmt`,
  `dev`, `start`, `db:up`, `db:down`, `migrate`, `seed`. `task demo` monta el
  proyecto desde cero (dependencias, `.env`, MySQL, migraciones, demo y tests).

## Despliegue (Render)

- La API se despliega en Render con el Blueprint `render.yaml` (plan gratuito,
  `runtime: docker`) y el `Dockerfile` de la raíz. Cada push a `main` la
  redespliega solo (`autoDeployTrigger: commit`); no se usan Actions de GitHub
  ni secretos en el repositorio para el despliegue.
- `docker-compose.yml` es solo el MySQL de desarrollo local; Render no lo lee.
- El MySQL de producción es externo (plan gratuito de Aiven, con TLS
  obligatorio): `MYSQL_SSL=true` activa un `SSLContext` en
  `Settings.sqlalchemy_connect_args()`, usado por el engine de la aplicación y
  por `migrations/env.py`. Local se queda en `false`.
- El entrypoint del contenedor (`scripts/docker-entrypoint.sh`) ejecuta
  `alembic upgrade head` antes de arrancar uvicorn en `$PORT` (10000).
- Secretos del despliegue (`MYSQL_*`, `SECRET_KEY`, `ADMIN_PASSWORD`,
  `ALLOWED_ORIGINS`) se rellenan en el Dashboard de Render como `sync: false`;
  nunca en `render.yaml`. La imagen de producción excluye `.env`, tests y docs
  (`.dockerignore`).
- El frontend (cuando exista) se despliega como sitio estático gratuito en su
  propio repositorio con su `render.yaml`; su URL se añade a `ALLOWED_ORIGINS`.

## Especificación antes del código (OpenSpec, #62)

- CLI local fijada en `package.json` + `package-lock.json`: Node.js >=20.19.0
  y `task spec:install`. npm solo gestiona esta herramienta; Python sigue con uv.
- La carpeta `specs/` de V2 es `openspec/specs/` en este repositorio. No crear
  una segunda carpeta raíz ni presentar funcionalidades pendientes como entregadas.
- Estructura: `openspec/config.yaml` (contexto/reglas),
  `openspec/specs/<capacidad>/spec.md` (contratos vigentes),
  `openspec/changes/<cambio>/` (proposal, specs, design y tasks del trabajo activo),
  y `openspec/changes/archive/` (histórico tras revisión).
- Una funcionalidad empieza por su issue y sus dependencias. Leer `CONTEXT.md`
  y estas convenciones; crear el cambio con `task spec -- new change <cambio>`.
  Escribir propuesta, requisitos y escenarios de aceptación **antes del código**.
- Flujo del agente: `openspec-new-change` (si está habilitado) →
  `openspec-propose` → `openspec-apply-change`. `new` es opcional si `propose`
  crea el cambio. El perfil `core` de OpenSpec incluye propose/apply, pero `new`
  requiere el perfil ampliado; los comandos de terminal funcionan sin skills.
- Cada persona puede generar su integración: `task spec -- init --tools opencode`
  (u otro ID soportado). La instalación base usa `--tools none` y no modifica
  la configuración global del agente. Reiniciar el agente si no detecta skills.
- Validar con `task spec:validate`. La CLI comprueba estructura, no que la
  implementación satisfaga los requisitos: revisar escenarios y ejecutar tests.
- Antes de abrir PR: `task spec:validate`, `task lint`, `task test`, entrada en
  `docs/ai-log.md` y enlaces a issue/spec. La validación automática en CI es #75.
- Después de la revisión, archivar con `task spec -- archive <cambio> --yes`
  y volver a validar; el archivo consolida los deltas en `openspec/specs/`.
- Guía y ejemplo: [docs/SPEC_WORKFLOW.md](docs/SPEC_WORKFLOW.md).

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

## Bitácora de IA y revisión de PR (#63)

- Cada funcionalidad principal registra en `docs/ai-log.md` herramienta/modelo,
  prompts clave, errores/correcciones y decisiones aceptadas o rechazadas.
  Indicar lo que no se pudo comprobar y los tests saltados; no inventar evidencia.
- Cada autor mantiene la entrada de su trabajo y la enlaza desde la PR junto
  con la issue y la spec. La responsable de #63 revisa que el registro continúe
  durante las entregas; no tiene que reconstruir las sesiones de otras personas.
- Usar `.github/pull_request_template.md` como checklist de revisión. Verificar
  la bitácora forma parte del DoD de cada PR de funcionalidad; la revisión
  humana sigue siendo obligatoria antes del merge.
- Nunca incluir secretos, tokens, contenido de `.env` ni datos personales.

## Planificación (issues, milestones, prioridad y bloqueos)

- Los milestones equivalen a los niveles de entrega: #2 Nivel medio,
  #3 Nivel Avanzado, #4 Nivel Experto. La prioridad de trabajo es el
  milestone más bajo primero.
- Estructura: épico #4 → STORYs (label `story`) → tareas (label `task`) como
  sub-issues de su STORY. Toda tarea nueva nace con STORY, milestone y AC.
- **Prioridad** en cada tarea: label `prioridad:P1` (bloquea a otras o núcleo
  del milestone), `prioridad:P2` (tarea del milestone sin dependientes),
  `prioridad:P3` (deseable), y campo Priority del Projects de GitHub.
- **Bloqueos** en el cuerpo de cada tarea: `⛔ Bloqueado por: #N, ...` y
  `⏫ Bloquea: #N, ...` con referencias reales; label `bloqueado` mientras la
  dependencia siga abierta. La persona responsable va en Assignees.
- Lo previsto por V2 que este repo ya cubre (uv/Taskfile, `/health`, capas,
  Alembic, Swagger base) quedó anotado como omitido en las STORYs, no se
  duplica en tareas.

## Pendiente por issue

- Milestone #1 (Nivel Esencial, cerrado): #1 tema gimnasio, #2/#3 modelos y
  diagrama ER, #7 logging en `logs/`, #8 manejo de excepciones, #10 CRUD bajo
  `/v1`, #6 variables sensibles (`ADMIN_PASSWORD`), #9 documentación Swagger
  (parcial: tags/summary/response_model y `CRUD_ERRORS`).
- Milestones #2–#4: plan V1 (STORYs #36–#42) + plan V2 migrado el
  2026-10-14 (ver «Alcance vigente»). Las STORYs #37, #38, #40 y #42
  ampliaron sus AC con V2; el resto del plan V2 está en las STORYs nuevas de
  cada milestone.
