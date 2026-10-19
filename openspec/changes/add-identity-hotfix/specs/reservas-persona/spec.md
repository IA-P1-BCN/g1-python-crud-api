## ADDED Requirements

### Requirement: Identidad de quien reserva
Las respuestas de reservas SHALL incluir `id_user`, `nombre` y `email` de la
Cuenta vinculada al cliente de la reserva, resueltos por el servidor; si el
cliente no tiene Cuenta, los tres campos SHALL ser null.

#### Scenario: Reserva con persona
- **WHEN** se lista o consulta una reserva cuyo cliente tiene Cuenta
- **THEN** la respuesta incluye id_user, nombre y email de esa Cuenta

#### Scenario: Cliente sin cuenta
- **WHEN** la reserva pertenece a un cliente sin Cuenta vinculada
- **THEN** id_user, nombre y email son null y el resto de campos no cambia
