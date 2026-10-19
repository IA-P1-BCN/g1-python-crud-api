## ADDED Requirements

### Requirement: Datos demo completos
`task seed` SHALL crear, de forma idempotente: 3 entrenadores con sus clases
(Boxeo, Yoga, Spinning), una cuenta staff por entrenador con la contraseña
demo común, y 22 usuarios demo `socio01..socio22@gymflow.com` activos y con
Cliente vinculado. El README SHALL documentar exactamente una cuenta demo
por rol (cliente, staff, admin) con su contraseña.

#### Scenario: Recuento exacto
- **WHEN** termina el seed
- **THEN** hay 3 entrenadores con clase y cuenta staff, y 22 socios demo

#### Scenario: Idempotencia
- **WHEN** se repite el seed
- **THEN** no duplica filas ni restablece credenciales existentes

#### Scenario: README sin .env
- **WHEN** se consulta la sección de cuentas demo del README
- **THEN** solo aparecen demo@gymflow.com, staff@gymflow.com y
  admin.demo@gymflow.com con contraseñas fijas
