## ADDED Requirements

### Requirement: Autenticación del gimnasio
Todos los métodos de /v1/clientes, /v1/entrenadores, /v1/clases,
/v1/reservas, /v1/pagos y /v1/export SHALL exigir una Cuenta activa con JWT válido.

#### Scenario: Credenciales ausentes o inválidas
- **WHEN** falta el token, es inválido o expirado, o la Cuenta fue borrada
- **THEN** responde 401 con WWW-Authenticate Bearer sin ejecutar el negocio

#### Scenario: Cuenta desactivada
- **WHEN** una Cuenta se desactiva después del login
- **THEN** el siguiente acceso responde 403

#### Scenario: Operación autenticada
- **WHEN** una Cuenta activa presenta un token válido
- **THEN** se aplican los contratos CRUD existentes, incluidos aforo y transacciones

### Requirement: Contrato público de autenticación
OpenAPI SHALL declarar OAuth2 en todas las operaciones protegidas y documentar
401/403. Registro, login, healthchecks y páginas de documentación SHALL ser públicos.

#### Scenario: Descubrir y usar la API
- **WHEN** se consulta OpenAPI sin iniciar sesión
- **THEN** los recursos de negocio muestran seguridad OAuth2 y las rutas públicas no
