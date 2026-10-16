# g1-python-crud-api

[![Tests](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/IA-P1-BCN/g1-python-crud-api/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge-v2.json)](https://github.com/astral-sh/ruff)

**GymFlow:** API REST con FastAPI y MySQL para clientes, entrenadores,
clases, reservas y pagos. Sigue [CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md),
el [PRD](docs/PRD.md) y el [modelo de datos](docs/DATABASE_SPEC.md).
Incluye [V2](docs/client/CLIENT_SPECS_V2_USER_MNG.md): Cuentas separadas de
Clientes, registro, login JWT, CRUD de Cuentas protegido y filtros. El flujo de
desarrollo usa OpenSpec, bitácora y revisión humana. La política granular por
roles y las funciones avanzadas de seguridad siguen en las tareas del equipo.

Requisitos: [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), Docker.

## Ejecutar

En local, con recarga de la API y el servidor de desarrollo de Angular:

```bash
task up
```

`task up` prepara dependencias, `.env`, MySQL, migraciones y datos demo, e
instala el frontend si falta `node_modules`. Después arranca la API
(`http://127.0.0.1:8000/docs`) y Angular (`http://127.0.0.1:4200`). `Ctrl+C`
detiene ambos. MySQL sigue en Docker.

Para el mismo arranque, con API, frontend y datos demo dentro de Docker:

```bash
task docker:up
```

`task docker:up` prepara `.env`, construye las imágenes y levanta MySQL, la API
y el frontend. La API aplica las migraciones al arrancar y después se ejecuta
el seed dentro del contenedor. Queda en segundo plano: la API en
`http://127.0.0.1:8000/docs` y el frontend en `http://127.0.0.1:4200`.
`task db:down` detiene los contenedores. `task compose` levanta los servicios
sin sembrar. `task db:up` sigue levantando solo MySQL, para no ocupar el puerto
8000 durante el desarrollo ni los tests.

Para solo preparar el entorno y ejecutar tests, sin servidores:

```bash
task demo
task dev
```

O paso a paso:

```bash
task install          # instala dependencias
test -f .env || cp .env.example .env
# Edita .env: SECRET_KEY propia, ADMIN_EMAIL y ADMIN_PASSWORD propia
task db:up            # levanta MySQL (docker compose)
task migrate          # crea tablas y registra la versión de esquema 0.3
task seed             # datos demo y Cuentas iniciales, sin sobrescribir
task dev              # servidor con recarga en http://127.0.0.1:8000
```

`task seed` crea tres clientes (activo, inactivo y suspendido), un entrenador,
una clase, un pago y una reserva. Repetirlo conserva los registros existentes:
identifica clientes por sus emails `*.demo@example.com` y entrenador/clase por
los nombres `Laura Demo` / `Yoga Demo`. Ejecutarlo con la demo detenida; si se
cambian esos identificadores, se crearán de nuevo los registros ausentes.

Si el puerto HTTP 8000 está ocupado, usa
`uv run uvicorn main:app --reload --port 8001` y abre `/docs` en ese puerto.

## Docker Compose

`docker-compose.yml` define tres servicios: `mysql` (`gym-mysql`), `api`
(`gym-api`) y `frontend` (`gym-frontend`). Los puertos se publican solo en
`127.0.0.1`: MySQL en `${MYSQL_PORT:-3306}`, la API en `8000` y el frontend en
`4200`.

Dentro de la red de Compose la API usa `MYSQL_HOST=mysql` y el puerto interno
`3306`, aunque el host publique otro. `SECRET_KEY` y el resto de variables
llegan de `.env` (prepara uno con `task env`); el fichero no se copia a la
imagen. El frontend es la build de Angular servida por nginx, que reenvía
`/v1` a `api:8000`.

`task db:down` detiene todos los servicios de Compose.

## Cuenta demo

La migración `ca6c9ed6b7e8` crea, si no existe, la cuenta
`demo@gymflow.com` con contraseña `Demo56789012`. Es rol `cliente`, está activa
y queda vinculada a un Cliente `Activo` con un pago, para poder iniciar sesión
y reservar. En la base solo se guarda el hash Argon2id. El admin del seed es
otra cuenta y sigue usando `ADMIN_EMAIL` / `ADMIN_PASSWORD`.

## Configuración del equipo

Cada persona mantiene su propio `.env`, sin subirlo a Git. La conexión MySQL
usa las variables de `.env.example`: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD` y `MYSQL_DATABASE`. Los valores del ejemplo corresponden al
MySQL local de Compose. Si 3306 está ocupado, cambia `MYSQL_PORT=3307` antes de
`task db:up`; Compose publica el mismo puerto. Las credenciales/base de un
volumen ya inicializado deben corresponder a las configuradas en MySQL.

`SECRET_KEY` es obligatoria, con al menos 32 caracteres aleatorios y sin valor
por defecto. Genera una clave propia y guárdala solo en `.env`:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

`ADMIN_PASSWORD` es obligatoria para `task seed`/`task demo`: 12–128 caracteres
y un valor propio, nunca el marcador. `ADMIN_EMAIL` identifica el admin inicial.
El seed crea cuentas **inactivas** para clientes con email válido, con secretos
aleatorios individuales; no inventa emails, no activa esas cuentas ni cambia
contraseñas existentes. El admin se crea activo y sin perfil Cliente.

Los secretos se cargan como `SecretStr`; no se publican ni se incluyen en errores
de configuración. Los tests y la CI tienen claves exclusivas de prueba.
Las migraciones de este repositorio incorporan Cuentas sin recrear la base V1;
no uses migraciones de otros repositorios.

## Swagger

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Healthchecks: `GET /health` · `GET /health/db`

Los schemas, campos obligatorios, valores permitidos y respuestas se pueden
consultar y probar en Swagger. Postman puede importar `/openapi.json`.

## CRUD de las cinco entidades

Cada recurso V1 ofrece cinco operaciones: **25 endpoints del gimnasio**, además
de la exportación CSV y los endpoints de Cuentas V2.

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
dependencias o regla de negocio; **422** datos inválidos; **500** error interno
inesperado; **503** MySQL no disponible. Los errores responden
`{"detail": "mensaje"}`; los de validación incluyen una lista de detalles de
FastAPI. El 500 devuelve siempre `Error interno del servidor`: el detalle y la
traza se escriben solo en el log, nunca en la respuesta.

## Filtrar y buscar en los listados (#22)

Los filtros se combinan con AND, se ordenan los resultados por ID y después
se aplica `offset`/`limit` (máximo 100). Sin filtros se conserva el listado
completo paginado; sin coincidencias se devuelve `200 []`.

| Listado | Filtros disponibles |
|---|---|
| `/v1/clientes` | `nombre`, `email`, `estado_membresia`, `fecha_inscripcion_desde`, `fecha_inscripcion_hasta`, `q` |
| `/v1/entrenadores` | `nombre`, `especialidad`, `telefono`, `q` |
| `/v1/clases` | `nombre_clase`, `id_entrenador`, `horario_desde`, `horario_hasta`, `q` |
| `/v1/reservas` | `id_cliente`, `id_clase`, `asistio`, `fecha_reserva_desde`, `fecha_reserva_hasta` |
| `/v1/pagos` | `id_cliente`, `metodo_pago`, `fecha_pago_desde`, `fecha_pago_hasta` |

Los campos de texto buscan fragmentos literales sin distinguir mayúsculas;
`%` y `_` no son comodines. `q` busca en nombre/email de clientes,
nombre/especialidad/teléfono de entrenadores, o nombre de clase. Los demás
filtros siguen aplicándose aunque se use `q`.

Los intervalos incluyen ambos extremos. Fechas: `YYYY-MM-DD`; horarios y fechas
de reserva: UTC sin sufijo de zona. Un campo null no coincide con un filtro
sobre ese campo. Los filtros opcionales se omiten cuando no se necesitan;
enviar texto vacío, parámetros desconocidos, tipos o valores inválidos devuelve
422. Un intervalo válido por tipo pero invertido devuelve 400 con `detail`.

Ejemplos (también disponibles como parámetros en Swagger):

```text
GET /v1/clientes?estado_membresia=Activo&q=ana&limit=10
GET /v1/clases?id_entrenador=1&horario_desde=2026-11-01T00:00:00
GET /v1/reservas?id_cliente=1&asistio=false
GET /v1/pagos?id_cliente=1&fecha_pago_desde=2026-10-01&fecha_pago_hasta=2026-10-31
```

`GET /v1/export/csv?tablas=clientes` mantiene el contrato de #18: exporta la
tabla completa, sin aplicar los filtros ni la paginación de estos GET.
Los filtros de `/v1/users` se describen en la sección de Cuentas y requieren token.

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

Para definir funcionalidades antes de implementarlas, consulta el
[flujo OpenSpec](docs/SPEC_WORKFLOW.md). Requiere Node.js >=20.19.0:

```bash
task spec:install
task spec:validate
task spec -- list
```

Las dependencias de la API siguen gestionándose con uv. La especificación de
cada cambio y su entrada en [la bitácora de IA](docs/ai-log.md) acompañan a la PR.

| Comando | Descripción |
|---|---|
| `task demo` | Prepara deps, `.env`, MySQL, migraciones, datos demo y tests |
| `task install` | Instala dependencias (`uv sync`) |
| `task test` | Ejecuta la suite de tests (`pytest`) |
| `task lint` | Comprueba PEP 8 (`ruff check`) |
| `task fmt` | Formatea el código (`ruff format`) |
| `task up` | Inicializa (sin tests) y arranca MySQL, API y frontend en el host |
| `task docker:up` | Igual que `up`, con API, frontend y seed en Docker |
| `task compose` | Levanta MySQL, API y frontend en Docker, sin seed |
| `task dev` | Servidor con recarga (`uvicorn --reload`) |
| `task start` | Servidor sin recarga |
| `task frontend` | Angular en `http://127.0.0.1:4200` |
| `task db:up` | Levanta solo MySQL (`docker compose up -d --wait mysql`) |
| `task db:down` | Detiene los servicios de Compose |
| `task migrate` | Aplica migraciones (`alembic upgrade head`) |
| `task seed` | Añade datos del gimnasio y Cuentas iniciales sin sobrescribir existentes |

## Enlaces

- [AGENTS.md](AGENTS.md) — convenciones y decisiones del proyecto
- [docs/client/CLIENT_SPECS.md](docs/client/CLIENT_SPECS.md) — especificación del cliente
- [docs/DATABASE_SPEC.md](docs/DATABASE_SPEC.md) — campos, relaciones y decisiones de #10
- [docs/EDR_DIAGRAM.md](docs/EDR_DIAGRAM.md) — diagrama ER

## Cuentas y autenticación V2

Cuenta es la identidad de acceso, Cliente es el socio del gimnasio. `activo`
de Cuenta y `estado_membresia` de Cliente son independientes. Un Cliente puede
tener una Cuenta vinculada; admin/staff no necesitan ser socios.

| Método y ruta | Acceso y resultado |
|---|---|
| `POST /v1/auth/register` | Público; 201 con Cuenta de rol cliente |
| `POST /v1/auth/login` | Público; formulario OAuth2, 200 con JWT |
| `GET /v1/users/me` | Token; perfil de la Cuenta actual |
| `PATCH /v1/users/me` | Token; perfil propio, contraseña nueva exige la actual |
| `GET /v1/users` | Admin; listado, filtros y paginación |
| `GET /v1/users/{id}` | Admin o propietario; detalle o 404 |
| `PUT /v1/users/{id}` | Admin; nombre/email obligatorios, contraseña opcional |
| `PATCH /v1/users/{id}` | Admin; solo cambia campos enviados |
| `DELETE /v1/users/{id}` | Admin; 204, borrado físico que conserva Cliente |

El registro recibe `nombre`, `email`, `password` (12–128 caracteres) y
`crear_cliente=false` por defecto. Con true crea un Cliente Inactivo nuevo en
la misma transacción; no se apropia de clientes existentes por email.

El login recibe `application/x-www-form-urlencoded`, con `username=<email>`
y `password=<contraseña>`. Devuelve `access_token` y `token_type=bearer`.
En Swagger pulsa **Authorize**, usa el email en username y después consulta
`/v1/users/me`. El token caduca a los 30 minutos.

PUT/PATCH solo aceptan nombre, email y password. La contraseña se conserva
literal, se guarda con Argon2 y nunca se devuelve. Si se omite, conserva el
hash anterior. No se aceptan null explícitos, PATCH vacío ni campos rol,
activo, id_cliente o fecha_creacion. La Cuenta conserva su fecha y vínculo.

Los endpoints de Cuentas exigen una Cuenta activa autenticada. El listado,
la edición por ID y el borrado exigen admin. Consultar por ID exige admin o
propietario; staff y cliente editan su perfil mediante `/v1/users/me`.
Los recursos del gimnasio y la exportación
CSV también exigen JWT (#105).
Registro, login, healthchecks y documentación siguen públicos.

### Filtros de Cuentas

`GET /v1/users` admite `nombre`, `email`, `q`, `activo`, `rol`, `id_cliente`,
`fecha_creacion_desde`, `fecha_creacion_hasta`, `offset` y `limit` (1–100).
Texto literal sin distinguir mayúsculas; criterios con AND antes de paginar y
rangos inclusivos UTC sin zona. `q` busca nombre/email con OR.
Ejemplo: `/v1/users?rol=staff&activo=true&limit=10`.

### Errores de auth y Cuentas

| Código | Significado observable |
|---|---|
| 400 | Rango de fechas invertido en el listado |
| 401 | Login incorrecto/inactivo, token ausente/inválido/expirado o Cuenta borrada; incluye `WWW-Authenticate: Bearer` |
| 403 | Cuenta desactivada o sin permisos; sin reto Bearer |
| 404 | Cuenta solicitada inexistente |
| 409 | Email o vínculo duplicado, o conflicto concurrente |
| 422 | Datos, campos o parámetros inválidos; omite valores sensibles |
| 500 | Error interno genérico |
| 503 | MySQL no disponible |

Swagger y ReDoc muestran ejemplos JSON, schemas y cabecera de autenticación
para los errores que corresponden a cada operación. Registro/login permanecen
públicos; no se documentan 400/403 artificiales en esas operaciones.

### Editar la Cuenta propia (#66)

`PATCH /v1/users/me` acepta nombre/email y, para cambiar la contraseña,
`password` junto a `current_password`. La actual incorrecta devuelve 403 y
ningún cambio se guarda; email duplicado devuelve 409. Omitir campos los conserva.
Null, cuerpo vacío y campos protegidos devuelven 422 sin reflejar credenciales.
La edición por ID queda reservada al admin; no permite saltarse este flujo.
