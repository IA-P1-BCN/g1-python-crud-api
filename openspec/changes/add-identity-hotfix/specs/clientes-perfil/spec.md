## MODIFIED Requirements

### Requirement: Perfil de cliente sin identidad almacenada
`clientes` SHALL almacenar solo perfil de negocio (`estado_membresia`,
`fecha_inscripcion`); nombre y email viven EXCLUSIVAMENTE en `users`.
GET `/v1/clientes` y `/v1/clientes/{id}` SHALL incluir en la respuesta la
identidad (`id_user`, `nombre`, `email`) resuelta del user vinculado, con
nulls si no hay vínculo. POST/PUT SHALL aceptar solo campos de perfil.

#### Scenario: Listado con identidad
- **WHEN** se pide `/v1/clientes` con un cliente vinculado a user
- **THEN** la fila incluye id_cliente, estado, fecha y el nombre/email del user

#### Scenario: Cliente sin cuenta
- **WHEN** un cliente no tiene user vinculado
- **THEN** la respuesta incluye id/estado/fecha y `id_user`, `nombre`, `email` en null

#### Scenario: Crear cliente
- **WHEN** se crea un cliente con solo estado y fecha
- **THEN** se crea el perfil; enviar nombre o email se rechaza con 422

### Requirement: Buscar personas en users
Los filtros de nombre/email de ClienteQuery SHALL eliminarse; la búsqueda de
personas por nombre/email se hace en `GET /v1/users`.

#### Scenario: Filtro inexistente
- **WHEN** se filtra `/v1/clientes?nombre=ana`
- **THEN** se rechaza con 422 (parámetro desconocido)
