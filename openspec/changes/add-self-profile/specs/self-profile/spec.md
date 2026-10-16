## ADDED Requirements

### Requirement: Edición propia
PATCH /v1/users/me SHALL tomar el ID del JWT y permitir solo nombre, email y
password. Una nueva password SHALL exigir current_password válida. Los campos
omitidos SHALL conservarse; null, cuerpo vacío y campos protegidos SHALL ser 422.

#### Scenario: Perfil sin cambio de contraseña
- **WHEN** una Cuenta activa envía nombre o email válidos
- **THEN** actualiza solo esos campos sin cambiar hash, rol, actividad ni vínculos

#### Scenario: Cambio de contraseña
- **WHEN** envía password de 12–128 caracteres y current_password correcta
- **THEN** guarda el hash de la nueva contraseña, sin devolver ninguna credencial

#### Scenario: Contraseña actual incorrecta
- **WHEN** current_password no coincide con el hash persistido bajo bloqueo
- **THEN** responde 403 y no cambia ningún campo

#### Scenario: Email duplicado
- **WHEN** otra Cuenta ya tiene el email solicitado
- **THEN** responde 409 sin cambios parciales

### Requirement: No eludir la verificación propia
PUT/PATCH /v1/users/{id} SHALL ser administrativos; GET /v1/users/{id} SHALL
permitir solo admin o la propia Cuenta. Los permisos se comprueban antes de leer.

#### Scenario: Acceso por ID no autorizado
- **WHEN** staff/cliente intenta editar por ID o consultar una Cuenta ajena
- **THEN** responde 403 sin modificar ni revelar datos

#### Scenario: Petición sin identidad
- **WHEN** falta un JWT válido en PATCH /v1/users/me
- **THEN** responde 401 con WWW-Authenticate Bearer
