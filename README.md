# GymFlow

[![Tests](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge-v2.json)](https://github.com/astral-sh/ruff)

API REST **FastAPI + MySQL** para un gimnasio: clientes, entrenadores,
clases, reservas y pagos — más [V2](docs/client/CLIENT_SPECS_V2_USER_MNG.md):
Cuentas con JWT, roles y permisos por propietario.

> **Modelo de identidad:** la identidad (nombre, email) vive **solo en
> `users`**; `clientes` guarda el perfil del socio (ADR 0002). Las respuestas
> de clientes y reservas resuelven la persona desde la Cuenta vinculada.

Requisitos: [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), Docker.

---

## Arranque rápido

```bash
task up          # API + frontend + MySQL en local (recarga)
```

| Comando | Qué hace |
|---|---|
| `task up` | Prepara deps, `.env`, MySQL, migraciones y seed; arranca API (8000) y Angular (4200) |
| `task docker:up` | Lo mismo, todo en Docker |
| `task demo` | Prepara entorno y ejecuta los tests, sin servidores |
| `task env` | Prepara `.env` solo: rellena `SECRET_KEY`/`ADMIN_PASSWORD` y elige puerto MySQL libre |

`task env` es idempotente: nunca pisa valores ya configurados.

<details>
<summary>Paso a paso y detalles de Docker</summary>

```bash
task install     # dependencias
task env         # .env listo (secretos y puerto)
task db:up       # MySQL (docker compose)
task migrate     # tablas + versión de esquema 0.5
task seed        # datos demo y cuentas, sin sobrescribir
task dev         # API con recarga en http://127.0.0.1:8000
```

Si el puerto 8000 está ocupado: `uv run uvicorn main:app --reload --port 8001`.

`docker-compose.yml` define `mysql` (`gym-mysql`), `api` (`gym-api`) y
`frontend` (`gym-frontend`), publicados solo en `127.0.0.1` (3306/8000/4200).
Dentro de la red de Compose la API usa `MYSQL_HOST=mysql` y el puerto interno
3306 aunque el host publique otro. `task db:down` detiene los servicios;
`task compose` levanta sin sembrar.

</details>

---

## Cuentas demo

Tres cuentas, una por rol, listas para el login y `/docs` (hash Argon2id en
base, nunca texto plano):

| Email | Rol | Contraseña | Para probar |
|---|---|---|---|
| `demo@gymflow.com` | cliente | `Demo56789012` | Marketplace, reservar clases |
| `staff@gymflow.com` | staff (Yoga) | `Demo56789012` | Panel de entrenador y sus reservas |
| `admin.demo@gymflow.com` | admin | `AdminDemo56789012` | Dashboard, gestión completa |

También existen `boxeo@gymflow.com` y `spinning@gymflow.com` (staff de sus
entrenadores) y 22 socios `socio01..socio22@gymflow.com` (contraseña
`Demo56789012`) creados por el seed.

**En Render:** <https://g1-gymflow-api.onrender.com/login> con
`admin.demo@gymflow.com / AdminDemo56789012` (contraseña pública
deliberadamente; el seed guarda solo su hash).

<details>
<summary>Notas de seguridad y repetición del seed</summary>

- Repetir `task seed` conserva credenciales, roles, estados y vínculos; si un
  email ya existe, se omite sin modificar nada.
- El admin privado del entorno (`ADMIN_EMAIL`/`ADMIN_PASSWORD` de `.env`) se
  crea internamente, pero no es la credenciale documentada de la demo.
- Reserva `admin.demo@gymflow.com` para la demo; usa otro `ADMIN_EMAIL`.

</details>

---

## Datos demo

Tras `task seed` hay exactamente:

- **3 entrenadores** con su clase y su cuenta staff: Laura Demo (Yoga),
  Oscar Rivas (Boxeo) y Nora Prieto (Spinning).
- **22 socios demo** activos con Cliente vinculado (mayoría `Activo`,
  algunos `Inactivo`/`Suspendido`).
- Los registros históricos V1 (Ana/Bruno/Carla, pago y reserva de ejemplo).

---

## Swagger

- **Swagger UI:** <http://127.0.0.1:8000/docs> · **ReDoc:** `/redoc` ·
  **OpenAPI:** `/openapi.json`
- **Healthchecks:** `GET /health` · `GET /health/db`
- Postman puede importar `/openapi.json`.

---

## La API en dos tablas

**Gimnasio (V1, JWT obligatorio):** `/v1/clientes`, `/v1/entrenadores`,
`/v1/clases`, `/v1/reservas`, `/v1/pagos` y `/v1/export/csv?tablas=<tabla>`.

| Operación | Método y ruta | Respuesta |
|---|---|---|
| Listar | `GET /v1/{recurso}?offset=0&limit=100` | 200, lista por ID |
| Consultar | `GET /v1/{recurso}/{id}` | 200, registro |
| Crear | `POST /v1/{recurso}` | 201, registro con ID |
| Actualizar | `PUT /v1/{recurso}/{id}` | 200, registro |
| Eliminar | `DELETE /v1/{recurso}/{id}` | 204 |

**Cuentas (V2):**

| Método y ruta | Acceso |
|---|---|
| `POST /v1/auth/register` · `POST /v1/auth/login` | Público |
| `GET /v1/users/me` · `PATCH /v1/users/me` | Token (propio) |
| `GET /v1/users` · `PUT/PATCH/DELETE /v1/users/{id}` | Admin |
| `PUT /v1/users/{id}/entrenador` | Admin (vínculo staff) |

<details>
<summary>Identidad en clientes y reservas (ADR 0002)</summary>

- `/v1/clientes` acepta y devuelve solo el perfil (`estado_membresia`,
  `fecha_inscripcion`); la respuesta **añade** `id_user`, `nombre` y `email`
  resueltos de la Cuenta vinculada (`null` si no hay).
- `/v1/reservas` incluye `id_user`, `nombre` y `email` de quien reserva.
- Buscar personas por nombre/email se hace en `GET /v1/users`, no en clientes.

</details>

<details>
<summary>Filtros de los listados</summary>

Se combinan con AND, orden por ID y después `offset`/`limit` (máx. 100).

| Listado | Filtros |
|---|---|
| `/v1/clientes` | `estado_membresia`, `fecha_inscripcion_desde/hasta` |
| `/v1/entrenadores` | `nombre`, `especialidad`, `telefono`, `q` |
| `/v1/clases` | `nombre_clase`, `id_entrenador`, `horario_desde/hasta`, `q` |
| `/v1/reservas` | `id_cliente`, `id_clase`, `asistio`, `fecha_reserva_desde/hasta` |
| `/v1/pagos` | `id_cliente`, `metodo_pago`, `fecha_pago_desde/hasta` |
| `/v1/users` | `nombre`, `email`, `q`, `activo`, `rol`, `id_cliente`, `fecha_creacion_desde/hasta` |

Texto literal sin mayúsculas; `%`/`_` no son comodines. Rangos inclusivos;
invertidos → 400; parámetros desconocidos → 422.

</details>

<details>
<summary>Permisos por rol</summary>

| Recurso | Admin | Staff | Cliente |
|---|---|---|---|
| Clientes | CRUD | — | Consulta el suyo |
| Entrenadores | CRUD | Consulta el suyo | Catálogo |
| Clases | CRUD | CRUD de las suyas | Catálogo |
| Reservas | CRUD | CRUD de las de sus clases | CRUD de las propias |
| Pagos | CRUD | — | Consulta los suyos |
| Export CSV | ✓ | ✗ | ✗ |

Un ID ajeno devuelve 404; una operación no permitida por rol, 403. El staff
necesita vínculo con Entrenador (`PUT /v1/users/{id}/entrenador` como admin).
`GET /v1/clases/{id}/cupo` expone disponibilidad sin datos personales.

</details>

<details>
<summary>Reglas de reserva</summary>

- Solo cliente `Activo` con al menos un pago puede reservar o trasladar.
- Sin duplicados (`UNIQUE` cliente+clase) y sin superar aforo, también bajo
  concurrencia; reducir aforo por debajo de la ocupación → 409.
- La reserva histórica conserva la asistencia aunque el socio pase a
  inactivo/suspendido.
- FK `RESTRICT`: no se borra un registro con dependencias (409).
- `PUT` sustituye editables; `fecha_reserva` la fija el servidor. Fechas UTC
  sin zona. Importes positivos con dos decimales (como cadena).

</details>

<details>
<summary>Probar una reserva desde Swagger</summary>

1. `POST /v1/clientes` → `{"estado_membresia":"Activo","fecha_inscripcion":"2026-10-06"}`
2. `POST /v1/entrenadores` → `{"nombre":"Luis","especialidad":"Yoga"}`
3. `POST /v1/clases` → `{"nombre_clase":"Yoga","horario":"2026-11-01T10:00:00","capacidad_max":10,"id_entrenador":1}`
4. `POST /v1/pagos` → `{"id_cliente":1,"monto":"35.00","fecha_pago":"2026-10-06","metodo_pago":"Tarjeta"}`
5. `POST /v1/reservas` → `{"id_cliente":1,"id_clase":1,"asistio":false}`

Asistencia con `PUT` (`"asistio": true`); cancelar con `DELETE` libera plaza.

</details>

---

## Tests

```bash
task db:up && task migrate && task lint && task test
```

La suite cubre CRUD, validaciones, reglas de reserva, permisos, identidad
resuelta, rutas del portal y el seed (recuento exacto). La integración usa un
servidor HTTP real contra MySQL. Sin MySQL, esos tests se saltan con aviso.

---

## Comandos

| Comando | Descripción |
|---|---|
| `task demo` | Prepara todo y ejecuta los tests |
| `task install` / `task env` | Dependencias / `.env` listo |
| `task up` / `task docker:up` | Arranque local / todo en Docker |
| `task dev` / `task start` / `task frontend` | Servidores |
| `task db:up` / `task db:down` | MySQL |
| `task migrate` / `task seed` | Esquema 0.5 / datos demo |
| `task test` / `task lint` / `task fmt` | Calidad |
| `task spec:install` / `task spec:validate` | [OpenSpec](docs/SPEC_WORKFLOW.md) |

La spec de cada cambio y su entrada en la [bitácora de IA](docs/ai-log.md)
acompañan a la PR.

---

## Enlaces

- [AGENTS.md](AGENTS.md) — convenciones y decisiones
- [CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md) · [CLIENT_SPECS_V2](docs/client/CLIENT_SPECS_V2_USER_MNG.md)
- [PRD](docs/PRD.md) · [Modelo de datos](docs/DATABASE_SPEC.md) · [Diagrama ER](docs/EDR_DIAGRAM.md)
- [ADRs](docs/adr/) — Cuenta ≠ Cliente (0001), identidad solo en users (0002)

---

<details>
<summary>Despliegue en Render</summary>

API y frontend se despliegan juntos con el Blueprint
[`render.yaml`](render.yaml) y [`Dockerfile`](Dockerfile): Angular se
construye y FastAPI lo sirve en `/` del mismo servicio
<https://g1-gymflow-api.onrender.com>. Cada push a `main` redespliega solo.

Pasos: crea el MySQL gestionado (p. ej. [Aiven](https://aiven.io) gratuito, 1
GB, TLS), aplica el Blueprint en Render y rellena los valores `sync: false`
(`MYSQL_*`, `MYSQL_SSL_CA` con el `ca.pem`, `SECRET_KEY`, `ADMIN_PASSWORD`,
`ALLOWED_ORIGINS` si hace falta). Las migraciones y el seed se ejecutan solos
en cada arranque (`scripts/docker-entrypoint.sh`).

El portal puede refrescarse en cualquier ruta (`/marketplace/...`,
`/staff/...`, `/admin/...`); `/v1`, `/docs` y `/health` conservan su función
y los errores de API siguen siendo JSON.

Plan Free: se duerme tras 15 min sin tráfico; Aiven también puede apagarse
por inactividad. Revisa cuotas en Billing.

</details>

<details>
<summary>Configuración del equipo (.env)</summary>

Cada persona mantiene su `.env` (fuera de Git). `task env` lo prepara:
`SECRET_KEY` (≥32, obligatoria), `ADMIN_PASSWORD` (12–128, obligatoria para
el seed), y `MYSQL_PORT` alternativo si 3306 está ocupado (Compose publica el
mismo valor). Conexión: `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` según
`.env.example`. `ACCESS_TOKEN_EXPIRE_MINUTES` controla la vida del JWT
(por defecto 30); reinicia la API al cambiarlo.

Los secretos se cargan como `SecretStr` y no aparecen en errores ni logs.
Tests y CI usan claves exclusivas de prueba.

</details>
