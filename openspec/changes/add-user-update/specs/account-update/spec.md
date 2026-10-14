## ADDED Requirements

### Requirement: Actualización protegida
PUT/PATCH /v1/users/{id} SHALL exigir Cuenta activa autenticada, actualizar
solo nombre, email y password y devolver CuentaResponse sin credenciales.
PUT SHALL exigir nombre y email; password omitida SHALL conservar el hash.
PATCH SHALL conservar campos omitidos. Password enviada SHALL guardarse con hash.

#### Scenario: Edición completa o parcial
- **WHEN** se envían campos válidos
- **THEN** se confirman y la fecha de creación, rol, activo y vínculo se conservan

#### Scenario: Contraseña renovada
- **WHEN** se envía password válida
- **THEN** el nuevo hash verifica esa contraseña y la anterior deja de funcionar

### Requirement: Errores sin cambios parciales
La operación SHALL responder 404 para id inexistente, 409 para email duplicado y
422 para datos inválidos, campos protegidos, null explícito o PATCH vacío.

#### Scenario: Email duplicado
- **WHEN** el email pertenece a otra Cuenta
- **THEN** responde 409 conservando todos los campos y el hash anterior

#### Scenario: Entrada inválida
- **WHEN** se envía rol/activo/id_cliente, password corta, null o PATCH vacío
- **THEN** responde 422 sin reflejar la contraseña
