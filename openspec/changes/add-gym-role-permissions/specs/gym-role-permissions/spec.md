## ADDED Requirements

### Requirement: Alcance por rol
El admin SHALL conservar todas las operaciones. El cliente SHALL consultar
solo su Cliente, Pagos y Reservas, y crear/trasladar/cancelar solo sus Reservas.
Staff SHALL gestionar solo Clases de su Entrenador y Reservas de esas Clases.
Las operaciones no permitidas SHALL responder 403; un ID ajeno a un recurso
permitido SHALL responder 404 sin devolver datos.

#### Scenario: Cliente consulta o filtra datos ajenos
- **WHEN** solicita el detalle de una Reserva/Pago/Cliente ajeno o filtra otro ID
- **THEN** obtiene 404 en detalle y una lista vacía al filtrar, nunca datos ajenos

#### Scenario: Paginación aislada
- **WHEN** pagina un listado con datos de varios propietarios
- **THEN** el alcance se aplica en SQL antes de offset/limit y junto a los filtros

#### Scenario: Reserva propia
- **WHEN** crea o traslada una Reserva con su id_cliente y sin alterar asistencia
- **THEN** se mantienen membresía activa, pago, unicidad, aforo y bloqueo transaccional

#### Scenario: Mutación de propietario o asistencia
- **WHEN** un cliente reserva para otra persona o altera su propia asistencia
- **THEN** recibe 403 sin cambios; tampoco puede crear pagos o activarse la membresía

#### Scenario: Staff de otro entrenador
- **WHEN** staff consulta, cambia, borra o mueve datos hacia Clases de otro Entrenador
- **THEN** los detalles ajenos son 404 y las asignaciones ajenas se rechazan con 403

#### Scenario: Cuenta sin vínculo
- **WHEN** cliente o staff no tiene su vínculo de negocio
- **THEN** los listados propios están vacíos y no puede crear recursos propios

### Requirement: Vínculo explícito de staff
Cuenta SHALL tener id_entrenador opcional, UNIQUE y FK RESTRICT. Solo admin SHALL
poder vincular/desvincular una Cuenta staff mediante PUT /v1/users/{id}/entrenador.
Registro, edición propia y edición general SHALL rechazar ese campo.

#### Scenario: Vinculación administrativa
- **WHEN** admin vincula una Cuenta staff a un Entrenador existente y libre
- **THEN** la siguiente petición del staff usa ese vínculo sin emitir otro token

#### Scenario: Vínculo inválido
- **WHEN** se intenta vincular un entrenador inexistente, ocupado o una Cuenta no staff
- **THEN** devuelve 404 o 409 y mantiene el vínculo anterior

### Requirement: Catálogo y cupo sin exposición de reservas
El cliente SHALL poder leer Clases y el catálogo de Entrenadores. GET
/v1/clases/{id_clase}/cupo SHALL devolver solo capacidad, reservas contadas y
plazas disponibles. La interfaz SHALL usar ese agregado para calcular plazas.
La exportación CSV SHALL estar reservada al admin.

#### Scenario: Cupo real con reservas ajenas
- **WHEN** un cliente consulta una clase que otras personas han reservado
- **THEN** ve el cupo real sin recibir identidades ni filas de reservas ajenas

#### Scenario: Exportación denegada
- **WHEN** staff o cliente intenta exportar cualquier tabla
- **THEN** recibe 403 sin CSV ni acceso masivo a registros
