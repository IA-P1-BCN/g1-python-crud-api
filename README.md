# g1-python-crud-api

[![Tests](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge-v2.json)](https://github.com/astral-sh/ruff)

API de gestión de usuarios con FastAPI, MySQL y JWT, conforme a la
[especificación V2](docs/client/CLIENT_SPECS_V2_USER_MNG.md).
La V2 sustituye el alcance del gimnasio; sus documentos se conservan como
referencia. El contrato implementado está en [specs/10-usuarios-crud.md](specs/10-usuarios-crud.md).

Requisitos: [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), Docker.

## Ejecutar

```bash
task install          # instala dependencias
task env              # prepara .env con una SECRET_KEY aleatoria
task db:up            # levanta MySQL (docker compose)
task migrate          # aplica migraciones (alembic)
task seed             # crea dos usuarios demo; credenciales en .env.demo
task dev              # servidor con recarga en http://127.0.0.1:8000
```

`task demo` ejecuta la preparación completa, datos de demostración y tests.
Si el puerto 3306 está ocupado, configura `MYSQL_PORT=3307` en `.env` antes
de `task db:up`. Docker y la API usan ese mismo puerto. La base conserva el
nombre `gym_db` para no romper el entorno existente.

`SECRET_KEY` debe tener al menos 32 caracteres. `task env` genera una clave
segura y conserva tus ajustes existentes. `ACCESS_TOKEN_EXPIRE_MINUTES`
controla la duración del JWT (30 minutos por defecto).

`task seed` crea `admin.demo@example.com` y `user.demo@example.com` con
contraseñas aleatorias distintas. Consúltalas en el archivo local `.env.demo`,
ignorado por Git y con permisos restringidos. Repetir el comando no cambia
usuarios ni contraseñas existentes. Estas cuentas sirven para la demo local.

## Swagger

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Healthchecks: `GET /health` · `GET /health/db`

En Swagger, pulsa **Authorize**, introduce el email en `username` y la
contraseña en `password`. Usa la cuenta demo admin para probar todo el CRUD.

## Endpoints

| Método | Ruta | Acceso |
|---|---|---|
| POST | `/v1/auth/register` | Público; registra usuario activo con rol user |
| POST | `/v1/auth/login` | Público; formulario OAuth2, devuelve JWT |
| GET | `/v1/users/me` | Usuario autenticado |
| POST | `/v1/users` | Admin; crea usuario con rol user |
| GET | `/v1/users?offset=0&limit=100` | Admin; lista ordenada por ID |
| GET | `/v1/users/{user_id}` | Propietario o admin |
| PUT | `/v1/users/{user_id}` | Propietario o admin |
| DELETE | `/v1/users/{user_id}` | Propietario o admin; 204 sin cuerpo |

Registro y creación reciben este JSON (usa tu propia contraseña):

```json
{
  "name": "Ana García",
  "email": "ana@example.com",
  "password": "ejemplo-local-de-12-caracteres"
}
```

PUT sustituye `name`, `email` e `is_active`. Puede incluir `password` para
cambiar la contraseña; omitirla conserva el hash. El email se normaliza a
minúsculas. No se pueden cambiar roles por HTTP. Las respuestas incluyen
`id`, `name`, `email`, `created_at` (UTC), `is_active` y `role`.

Las contraseñas se guardan con Argon2 y no se devuelven. Los tokens requieren
firma válida y expiración; borrar/desactivar la cuenta o cambiar su contraseña
invalida el acceso anterior. Reactivar una cuenta exige un nuevo login.
Errores: 401 credenciales, 403 permisos, 404 inexistente, 409 email duplicado,
422 validación y 503 MySQL no disponible.

Importa [la colección Postman](docs/postman/users.postman_collection.json),
configura `admin_email` y `admin_password` desde `.env.demo` y ejecuta Login.
El token y el ID creado se guardan en variables de la colección. No exportes
colecciones con credenciales o tokens reales.

## Tests

```bash
task db:up && task migrate && task test
```

Los tests unitarios cubren los endpoints y permisos sin MySQL. Los de
integración levantan uvicorn en un puerto efímero y hacen peticiones HTTP
reales; solo omiten MySQL cuando no está disponible. Los tests limpian
exclusivamente los registros que crean. También se verifica el registro
concurrente con el mismo email.

## Comandos

| Comando | Descripción |
|---|---|
| `task demo` | Monta dependencias, `.env`, MySQL, migraciones, demo y tests |
| `task install` | Instala dependencias (`uv sync`) |
| `task env` | Prepara `.env` y una clave JWT aleatoria |
| `task seed` | Crea cuentas demo de forma repetible |
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
- [docs/client/CLIENT_SPECS_V2_USER_MNG.md](docs/client/CLIENT_SPECS_V2_USER_MNG.md) — especificación vigente
- [specs/10-usuarios-crud.md](specs/10-usuarios-crud.md) — alcance y criterios de aceptación
- [docs/ai-log.md](docs/ai-log.md) — prompts y decisiones de desarrollo
