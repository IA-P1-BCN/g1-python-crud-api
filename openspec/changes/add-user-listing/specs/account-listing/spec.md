## ADDED Requirements

### Requirement: Consultas protegidas
GET /v1/users y GET /v1/users/{id} SHALL exigir Cuenta activa con JWT válido y
responder con schemas sin credenciales. El listado SHALL ordenar por id y
paginar con offset >= 0 y limit entre 1 y 100 (por defecto 100).

#### Scenario: Listado paginado
- **WHEN** una Cuenta activa consulta offset=1 y limit=1
- **THEN** recibe solo el segundo resultado ordenado por id

#### Scenario: Detalle inexistente
- **WHEN** se consulta un id positivo que no existe
- **THEN** responde 404

#### Scenario: Consulta inválida o no autenticada
- **WHEN** hay parámetros inválidos o desconocidos
- **THEN** responde 422 para Cuenta autenticada
- **AND** sin token responde 401
