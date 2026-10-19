# seed-role-accounts Specification

## Purpose
Define las Cuentas demo de admin y staff que `task seed` crea para mostrar los
tres roles de GymFlow (`admin`, `staff`, `cliente`) en `/docs`, con una
contraseña común documentada y sin sobrescribir credenciales existentes.

## Requirements

### Requirement: Cuentas demo de roles en el seed
`task seed` SHALL crear, si no existe, la Cuenta `staff@gymflow.com` con rol
`staff`, activa y vinculada a un Entrenador sin Cuenta, además del admin de
`ADMIN_EMAIL`. La creación SHALL ser idempotente: una segunda ejecución no
duplica Cuentas ni modifica hashes existentes.

#### Scenario: Seed inicial
- **WHEN** se ejecuta `task seed` con `ADMIN_EMAIL=admin@gymflow.com` y sin
  Cuentas demo previas
- **THEN** existen `admin@gymflow.com` (rol `admin`, activa),
  `staff@gymflow.com` (rol `staff`, activa, con `id_entrenador` distinto de
  null) y las cuentas de clientes, todo con hash Argon2id

#### Scenario: Seed repetido
- **WHEN** `task seed` se ejecuta una segunda vez
- **THEN** el número de Cuentas no cambia, los `password_hash` existentes se
  conservan y el vínculo del staff no se reasigna

#### Scenario: Sin Entrenador disponible
- **WHEN** no existe ningún Entrenador sin Cuenta vinculada
- **THEN** el seed omite la Cuenta staff, informa la omisión en la salida y
  termina sin error, sin crear un staff sin vínculo

#### Scenario: Email ocupado
- **WHEN** `staff@gymflow.com` ya pertenece a otra Cuenta
- **THEN** el seed conserva la Cuenta existente sin modificarla ni vincularla
  a un Entrenador ajeno

### Requirement: Credenciales demo comunes
La Cuenta staff nueva SHALL usar la contraseña demo `Demo56789012` y la del
admin SHALL seguir viniendo de `ADMIN_PASSWORD` cuando esté definida. El email
por defecto del admin SHALL ser `admin@gymflow.com` en `Settings` y en
`.env.example`, sin sobrescribir un `ADMIN_EMAIL` ya configurado.

#### Scenario: Login con las tres cuentas
- **WHEN** se inicia sesión con `admin@gymflow.com` y `ADMIN_PASSWORD`, con
  `staff@gymflow.com` y con `demo@gymflow.com`, usando `Demo56789012` en las
  dos últimas
- **THEN** los tres inicios devuelven 200 con un JWT

#### Scenario: ADMIN_EMAIL preconfigurado
- **WHEN** `.env` ya define `ADMIN_EMAIL` con otro valor
- **THEN** `task env` y `task seed` conservan ese email como cuenta admin
