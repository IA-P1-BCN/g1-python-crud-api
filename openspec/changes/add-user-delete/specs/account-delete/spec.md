## ADDED Requirements

### Requirement: Borrado físico autenticado
DELETE /v1/users/{id} SHALL exigir Cuenta activa autenticada, borrar la Cuenta
y responder 204 sin cuerpo. SHALL conservar Cliente y su historial.

#### Scenario: Baja confirmada
- **WHEN** se borra una Cuenta existente
- **THEN** deja de aparecer en listado y detalle, y sus tokens devuelven 401
- **AND** su Cliente vinculado se conserva

#### Scenario: Cuenta inexistente
- **WHEN** el id no existe o se repite el borrado desde otra Cuenta válida
- **THEN** responde 404

#### Scenario: Sin autenticación
- **WHEN** no hay token válido
- **THEN** responde 401 y conserva la Cuenta
