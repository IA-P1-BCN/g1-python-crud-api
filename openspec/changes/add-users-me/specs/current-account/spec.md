## ADDED Requirements

### Requirement: Cuenta actual
GET /v1/users/me SHALL exigir Bearer JWT válido, resolver la Cuenta persistida
y responder con schema público sin credenciales.

#### Scenario: Perfil propio
- **WHEN** llega token válido de Cuenta activa
- **THEN** responde 200 con esa Cuenta

#### Scenario: Identidad no acreditada
- **WHEN** falta token, es inválido/expirado o la Cuenta fue borrada
- **THEN** responde 401 con WWW-Authenticate Bearer

#### Scenario: Cuenta desactivada tras login
- **WHEN** el JWT es válido pero la Cuenta ya está inactiva
- **THEN** responde 403 sin devolver datos del perfil
