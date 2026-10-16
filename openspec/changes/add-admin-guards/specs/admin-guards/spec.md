## ADDED Requirements

### Requirement: Administración de Cuentas
GET /v1/users y DELETE /v1/users/{id} SHALL exigir una Cuenta activa con rol admin.
La dependencia requires_admin SHALL poder reutilizarse en la capa interfaces.

#### Scenario: Administrador
- **WHEN** una Cuenta admin presenta un JWT válido
- **THEN** puede listar y borrar Cuentas conforme al contrato existente

#### Scenario: Otros roles
- **WHEN** una Cuenta staff o cliente intenta listar o borrar Cuentas
- **THEN** responde 403 sin revelar el listado ni borrar registros

#### Scenario: Cambio de rol
- **WHEN** un administrador pierde el rol después de emitir su token
- **THEN** su siguiente operación administrativa recibe 403

#### Scenario: Identidad inválida
- **WHEN** falta un JWT válido o la Cuenta está desactivada
- **THEN** se conserva la respuesta 401 o 403 de get_current_user
