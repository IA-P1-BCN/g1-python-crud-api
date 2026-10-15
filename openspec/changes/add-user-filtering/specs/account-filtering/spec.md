## ADDED Requirements

### Requirement: Listado filtrado
GET /v1/users SHALL admitir nombre/email por fragmento literal sin distinguir
mayúsculas; q SHALL buscar en ambos con OR. activo, rol e id_cliente SHALL
filtrar por igualdad. fecha_creacion_desde/hasta SHALL ser inclusivas y UTC
sin zona. Criterios distintos SHALL combinarse con AND antes de paginar.

#### Scenario: Combinación y paginación
- **WHEN** se filtran q y activo con offset/limit
- **THEN** se devuelve la página del resultado filtrado ordenado por id

#### Scenario: Comodines y cuentas inactivas
- **WHEN** se busca texto con % o _ y activo=false
- **THEN** los caracteres son literales y false no se ignora

### Requirement: Validación de consulta
Parámetros desconocidos, tipos/roles/ids/fechas inválidos SHALL devolver 422.
Un rango invertido SHALL devolver 400 sin ejecutar la consulta del listado.

#### Scenario: Rango invertido
- **WHEN** desde es posterior a hasta
- **THEN** responde 400

#### Scenario: Parámetro inválido
- **WHEN** limit supera 100, rol no existe o fecha incluye zona
- **THEN** responde 422
