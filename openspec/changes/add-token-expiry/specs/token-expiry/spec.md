## ADDED Requirements

### Requirement: Duración configurable
El emisor JWT SHALL usar ACCESS_TOKEN_EXPIRE_MINUTES, entero entre 1 y 1440,
con valor por defecto 30. Una configuración inválida SHALL rechazarse al iniciar.

#### Scenario: Duración elegida
- **WHEN** el entorno configura 7 minutos y se inicia sesión
- **THEN** exp menos iat equivale a 420 segundos

#### Scenario: Configuración inválida
- **WHEN** la duración es cero, negativa, fraccionaria, no numérica o supera 1440
- **THEN** settings rechaza el valor

### Requirement: Caducidad efectiva
Todo recurso protegido SHALL rechazar tokens expirados con 401 Bearer.
Cambiar la configuración SHALL afectar a tokens nuevos; los emitidos conservan exp.

#### Scenario: Token caducado
- **WHEN** pasa la duración de un token emitido por el login real
- **THEN** el recurso protegido devuelve 401 con WWW-Authenticate Bearer
