## ADDED Requirements

### Requirement: Registro público
POST /v1/auth/register SHALL crear una Cuenta activa de rol cliente y responder
201 con id, nombre, email, activo, rol, fecha_creacion e id_cliente, sin password
ni password_hash. SHALL validar nombre, email y contraseña de 12–128 caracteres.

#### Scenario: Cuenta sin perfil de gimnasio
- **WHEN** se registra nombre, email válido y contraseña
- **THEN** se crea la Cuenta con email normalizado y hash Argon2, sin Cliente

#### Scenario: Nuevo socio
- **WHEN** crear_cliente es true
- **THEN** se crea un Cliente Inactivo vinculado en la misma transacción
- **AND** no se vincula ningún Cliente preexistente por email o id

### Requirement: Rechazo seguro
El registro SHALL rechazar email duplicado con 409 y entradas inválidas o
campos de privilegios con 422, sin devolver la contraseña tampoco en errores.

#### Scenario: Email duplicado
- **WHEN** el email ya identifica una Cuenta o entra en conflicto al crear Cliente
- **THEN** se devuelve 409 y la transacción no deja registros parciales

#### Scenario: Entrada inválida
- **WHEN** la contraseña es corta o se envían rol, activo o id_cliente
- **THEN** se devuelve 422 sin reflejar el secreto
