## Why
#134: crear un Entrenador desde el panel de admin solo da de alta la entidad
de negocio; sin Cuenta no puede iniciar sesión (ADR 0002) y hay que vincular
a mano después.

## What Changes
`POST /v1/entrenadores` acepta `email` opcional: cuando va (y quien pide es
admin), la misma transacción crea el Entrenador y su Cuenta staff activa
vinculada con la contraseña demo común. Las respuestas de entrenadores
resuelven `id_user`/`email` de la Cuenta vinculada. El formulario del admin
pide email obligatorio y muestra las credenciales; el listado muestra el
email o "sin cuenta".

## Capabilities
### New Capabilities
- `entrenador-cuenta`: alta conjunta de Entrenador y Cuenta staff.
### Modified Capabilities
Ninguna (la creación sin email sigue igual para datos históricos).

## Impact
Schemas/validación de entrenadores, repositorio y casos de uso de Cuentas,
identidad en respuestas, formulario y listado del admin, tests y README.
