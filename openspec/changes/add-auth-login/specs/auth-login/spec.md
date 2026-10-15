## ADDED Requirements

### Requirement: Login OAuth2
POST /v1/auth/login SHALL aceptar formulario username (email) y password y
devolver access_token y token_type=bearer para Cuenta activa con contraseña válida.
SHALL firmar JWT HS256 con SECRET_KEY obligatoria de al menos 32 caracteres,
sub=id como string, iat, exp (30 minutos), iss y aud.

#### Scenario: Login válido
- **WHEN** las credenciales de una Cuenta activa son correctas
- **THEN** responde 200 con JWT firmado, sin password ni hash

#### Scenario: Credenciales incorrectas o Cuenta inactiva
- **WHEN** email inexistente, contraseña incorrecta o Cuenta inactiva
- **THEN** responde el mismo 401 genérico con WWW-Authenticate Bearer

### Requirement: Integración Swagger
OpenAPI SHALL declarar OAuth2 password flow con tokenUrl v1/auth/login y
permitir Authorize sin exigir token para login o registro.

#### Scenario: Autorización interactiva
- **WHEN** Swagger obtiene la especificación
- **THEN** dispone de password flow y recibe un token usando el formulario documentado

### Requirement: Verificación estricta del token
El adaptador SHALL rechazar firma inválida, algoritmo distinto, expiración,
claims obligatorias ausentes, issuer/audience ajenos o subject inválido.

#### Scenario: Token no válido
- **WHEN** falla cualquiera de estas validaciones
- **THEN** produce error de autenticación sin exponer el token
