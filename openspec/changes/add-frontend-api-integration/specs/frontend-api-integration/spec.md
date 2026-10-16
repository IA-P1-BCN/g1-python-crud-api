## ADDED Requirements

### Requirement: Autenticación contra la API
La aplicación SHALL autenticar con `POST /v1/auth/login` (formulario OAuth2 con
`username` = correo) y obtener el perfil con `GET /v1/users/me`. El token MUST
guardarse en sessionStorage y MUST adjuntarse como `Authorization: Bearer` a las
peticiones de `/v1`.

#### Scenario: Credenciales válidas
- **WHEN** el usuario envía un correo y contraseña válidos
- **THEN** la aplicación guarda el token, obtiene el perfil y inicia la sesión con id, nombre, rol e id_cliente

#### Scenario: Credenciales incorrectas o cuenta inactiva
- **WHEN** la API responde 401 al login
- **THEN** `AuthService` lanza `InvalidCredentialsError` y no se guarda ningún token

#### Scenario: Token caducado
- **WHEN** una petición protegida recibe 401 con un token guardado
- **THEN** se borra el token, se cierra la sesión local y no se modifica la sesión de un login fallido

### Requirement: Registro público
La aplicación SHALL crear cuentas con `POST /v1/auth/register` enviando nombre, correo,
contraseña y `crear_cliente`.

#### Scenario: Correo duplicado
- **WHEN** la API responde 409 al registro
- **THEN** `AuthService` lanza `EmailDuplicadoError`

### Requirement: Clases y reservas reales
La aplicación SHALL leer clases y entrenadores de la API y SHALL gestionar reservas con
`/v1/reservas`, filtrando por `id_clase` o `id_cliente`.

#### Scenario: Reserva con plaza libre
- **WHEN** el socio reserva una clase con plazas libres
- **THEN** se crea la reserva con `asistio = false` y la respuesta devuelve su id

#### Scenario: Conflictos de negocio
- **WHEN** la API responde 409 al crear una reserva
- **THEN** el detalle "La clase no tiene plazas disponibles" produce `SinPlazasError`, "ya tiene una reserva" produce `YaReservadaError` y cualquier otro conflicto produce `ReservaRechazadaError` con el mensaje del servidor

### Requirement: Errores de conexión y del servidor
La aplicación SHALL distinguir fallo de red (estado 0) de errores de la API. Un fallo
de red MUST producir `NetworkError`; cualquier otro error MUST producir `ApiError` con
el código HTTP y el texto del `detail`, sin trazas técnicas.

#### Scenario: Servidor inaccesible
- **WHEN** la petición no obtiene respuesta
- **THEN** se lanza `NetworkError`

#### Scenario: Detalle no textual
- **WHEN** la API devuelve un 422 con lista de errores de validación
- **THEN** `ApiError` expone un mensaje genérico en lugar de la lista

### Requirement: Listados completos
Los listados SHALL pedir páginas de 100 elementos con offset/limit hasta recibir una
página incompleta.

#### Scenario: Más de una página
- **WHEN** un recurso tiene más de 100 elementos
- **THEN** la aplicación pide las páginas sucesivas y devuelve todos los elementos en orden

### Requirement: Cliente CRUD para todo el backend
La aplicación SHALL disponer de servicios para listar, obtener, reemplazar (PUT) y
eliminar clientes, entrenadores, clases, reservas, pagos y cuentas, y de exportar tablas
a CSV, aunque no tengan pantalla asociada.

#### Scenario: Exportación CSV
- **WHEN** se pide la exportación de una tabla válida
- **THEN** se devuelve el texto CSV de `GET /v1/export/csv?tablas=<tabla>`
