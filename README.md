# g1-python-crud-api

[![Tests](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge-v2.json)](https://github.com/astral-sh/ruff)

**GymFlow V1:** API REST con FastAPI y MySQL para clientes, entrenadores,
clases, reservas y pagos. Sigue [CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md),
el [PRD](docs/PRD.md) y el [modelo de datos](docs/DATABASE_SPEC.md).
La especificación V2 de gestión de usuarios no se aplica a esta entrega.

Requisitos: [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), Docker.

## Ejecutar

Para preparar dependencias, MySQL, tablas y datos ficticios, y ejecutar los tests:

```bash
task demo
task dev
```

O paso a paso:

```bash
task install          # instala dependencias
cp .env.example .env  # solo si todavía no tienes .env
task db:up            # levanta MySQL (docker compose)
task migrate          # crea las cinco tablas y actualiza la versión de esquema
task seed             # añade datos ficticios para probar el CRUD
task dev              # servidor con recarga en http://127.0.0.1:8000
```

`task seed` crea tres clientes (activo, inactivo y suspendido), un entrenador,
una clase, un pago y una reserva. Repetirlo conserva los registros existentes:
identifica clientes por sus emails `*.demo@example.com` y entrenador/clase por
los nombres `Laura Demo` / `Yoga Demo`. Ejecutarlo con la demo detenida; si se
cambian esos identificadores, se crearán de nuevo los registros ausentes.

Si el puerto HTTP 8000 está ocupado, usa
`uv run uvicorn main:app --reload --port 8001` y abre `/docs` en ese puerto.

## Configuración del equipo

Cada persona mantiene su propio `.env`, sin subirlo a Git. Las cinco variables
necesarias están en `.env.example`: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD` y `MYSQL_DATABASE`. Los valores del ejemplo corresponden al
MySQL local de Compose. Si 3306 está ocupado, cambia `MYSQL_PORT=3307` antes de
`task db:up`; Compose publica el mismo puerto. Las credenciales/base de un
volumen ya inicializado deben corresponder a las configuradas en MySQL.

`.env.example` incluye también `ADMIN_PASSWORD`, una variable sensible
reservada: es opcional y ningún endpoint la usa todavía. Se lee como `SecretStr`
para que no aparezca en logs ni en `repr()`. Pon tu propio valor en `.env`; el
de `.env.example` es solo un marcador.

Esta V1 no necesita `SECRET_KEY`, JWT, login ni cuentas de administrador.
Si habías preparado la V2, usa una base nueva para V1 y ajusta `MYSQL_DATABASE`:
su migración `0002` de usuarios no pertenece a esta cadena de migraciones.
Conserva la base anterior; no es necesario borrarla para trabajar en V1.

## Swagger

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Healthchecks: `GET /health` · `GET /health/db`

Los schemas, campos obligatorios, valores permitidos y respuestas se pueden
consultar y probar en Swagger. Postman puede importar `/openapi.json`.

## CRUD de las cinco entidades

Cada recurso ofrece cinco operaciones: **25 endpoints de negocio** en total.

| Recurso | Colección | Identificador |
|---|---|---|
| Clientes | `/v1/clientes` | `id_cliente` |
| Entrenadores | `/v1/entrenadores` | `id_entrenador` |
| Clases | `/v1/clases` | `id_clase` |
| Reservas | `/v1/reservas` | `id_reserva` |
| Pagos | `/v1/pagos` | `id_pago` |

| Operación | Método y ruta | Respuesta |
|---|---|---|
| Listar | `GET /v1/{recurso}?offset=0&limit=100` | 200, lista ordenada por ID |
| Consultar | `GET /v1/{recurso}/{id}` | 200, registro |
| Crear | `POST /v1/{recurso}` | 201, registro con ID generado |
| Actualizar | `PUT /v1/{recurso}/{id}` | 200, registro actualizado |
| Eliminar | `DELETE /v1/{recurso}/{id}` | 204, sin cuerpo |

`PUT` sustituye todos los campos editables. Los opcionales omitidos quedan en
`null`; `asistio` toma `false` si se omite. No se admiten IDs ni campos extra en
el cuerpo. La fecha de reserva se genera al crear y se conserva al actualizar.
Los listados admiten `offset >= 0` y `limit` entre 1 y 100.

Errores: **404** registro o relación inexistente; **409** duplicado, borrado con
dependencias o regla de negocio; **422** datos inválidos; **503** MySQL no
disponible. Los errores de negocio responden `{"detail": "mensaje"}`; los de
validación incluyen una lista de detalles de FastAPI.

## Probar una reserva desde Swagger

Ejecuta los `POST` en este orden y reutiliza los IDs devueltos (los valores 1
de estos ejemplos son ilustrativos):

1. `/v1/clientes`:
   ```json
   {"nombre":"Ana","email":"ana@example.com","estado_membresia":"Activo","fecha_inscripcion":"2026-10-06"}
   ```
2. `/v1/entrenadores`:
   ```json
   {"nombre":"Luis","especialidad":"Yoga","telefono":null}
   ```
3. `/v1/clases`, con el ID del entrenador:
   ```json
   {"nombre_clase":"Yoga","horario":"2026-11-01T10:00:00","capacidad_max":10,"id_entrenador":1}
   ```
4. `/v1/pagos`, con el ID del cliente:
   ```json
   {"id_cliente":1,"monto":"35.00","fecha_pago":"2026-10-06","metodo_pago":"Tarjeta"}
   ```
5. `/v1/reservas`, con los IDs del cliente y la clase:
   ```json
   {"id_cliente":1,"id_clase":1,"asistio":false}
   ```

Registra asistencia con `PUT /v1/reservas/{id_reserva}`, enviando ambos IDs y
`"asistio": true`. Cancela con `DELETE` para liberar una plaza.

Reglas del modelo:

- Membresía: `Activo`, `Inactivo` o `Suspendido`. Solo un cliente activo con
  al menos un pago puede crear o trasladar una reserva.
- El modelo no define vencimiento de pagos; se comprueba su existencia.
- No se puede reservar dos veces la misma clase ni superar su capacidad,
  incluso ante peticiones concurrentes. Reducir aforo por debajo de la
  ocupación devuelve 409.
- Una reserva histórica permite actualizar asistencia aunque el cliente
  haya pasado a inactivo o suspendido.
- Las FK bloquean borrar clientes con pagos/reservas, entrenadores con clases
  o clases con reservas. Elimina primero las dependencias cuando corresponda.
- `fecha_inscripcion`, `telefono` y `metodo_pago` son opcionales. Métodos:
  `Tarjeta`, `Transferencia`, `Efectivo`. Los importes son positivos y admiten
  dos decimales; se devuelven como cadenas para conservar precisión.
- Fechas/hora `DATETIME` en UTC sin sufijo de zona. La asistencia se registra
  mediante `asistio`; el modelo aprobado no incluye un timestamp de llegada.

## Tests

```bash
task db:up
task migrate
task lint
task test
```

La suite cubre las cinco operaciones de cada entidad, validaciones y reglas
de reserva. La integración arranca un servidor HTTP real y verifica persistencia
en MySQL, rollback, claves únicas, FK, aforo concurrente y repetición del seed.
Los tests limpian sus propios registros; no vacían las tablas del equipo.
Si MySQL no está disponible, los tests que lo necesitan se saltan con un
mensaje. Para validar toda la entrega, debe estar arrancado y migrado.

## Comandos

| Comando | Descripción |
|---|---|
| `task demo` | Prepara deps, `.env`, MySQL, migraciones, datos demo y tests |
| `task install` | Instala dependencias (`uv sync`) |
| `task test` | Ejecuta la suite de tests (`pytest`) |
| `task lint` | Comprueba PEP 8 (`ruff check`) |
| `task fmt` | Formatea el código (`ruff format`) |
| `task dev` | Servidor con recarga (`uvicorn --reload`) |
| `task start` | Servidor sin recarga |
| `task db:up` | Levanta MySQL (`docker compose up -d --wait`) |
| `task db:down` | Detiene MySQL |
| `task migrate` | Aplica migraciones (`alembic upgrade head`) |
| `task seed` | Añade datos ficticios de las cinco tablas sin duplicar los existentes |

## Enlaces

- [AGENTS.md](AGENTS.md) — convenciones y decisiones del proyecto
- [docs/client/CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md) — especificación del cliente
- [docs/DATABASE_SPEC.md](docs/DATABASE_SPEC.md) — campos, relaciones y decisiones de #10
- [docs/EDR_DIAGRAM.md](docs/EDR_DIAGRAM.md) — diagrama ER
