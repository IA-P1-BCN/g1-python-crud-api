## ADDED Requirements

### Requirement: Alta conjunta de Entrenador y Cuenta
`POST /v1/entrenadores` con `email` SHALL crear, en una sola transacción, el
Entrenador y una Cuenta staff activa vinculada (`users.id_entrenador`) con
ese email y la contraseña demo común; la respuesta SHALL incluir `id_user` y
`email`. Sin `email`, SHALL crear solo el Entrenador (datos históricos).

#### Scenario: Alta con email
- **WHEN** un admin crea un entrenador con email válido
- **THEN** se crean Entrenador y Cuenta staff activa y la respuesta incluye id_user y email

#### Scenario: Email duplicado
- **WHEN** el email ya pertenece a una Cuenta
- **THEN** se devuelve 409 y no se crea el Entrenador (rollback total)

#### Scenario: Email inválido o campo en PUT
- **WHEN** el email es inválido en el alta, o se envía en un PUT
- **THEN** se devuelve 422 sin crear nada

### Requirement: Identidad visible en el listado
Los GET de entrenadores SHALL resolver `id_user` y `email` de la Cuenta
vinculada, con null cuando no exista.

#### Scenario: Entrenador sin cuenta
- **WHEN** se lista un entrenador histórico sin Cuenta
- **THEN** id_user y email son null y el resto de campos no cambia
