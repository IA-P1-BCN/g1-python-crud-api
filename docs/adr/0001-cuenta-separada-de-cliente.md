# 0001: Cuenta (User) separada de Cliente con perfil vinculado

Status: accepted (2026-10-14)

La especificación V2 (`docs/client/CLIENT_SPECS_V2_USER_MNG.md`) exige un
modelo `User` (email único, contraseña hasheada, `activo`) con CRUD y
autenticación JWT, mientras el dominio del gimnasio ya tiene `Cliente` con
Estado de Membresía tri-estado y campos de negocio (teléfono, método de pago,
fecha de inscripción). Decidimos crear una entidad **Cuenta** (tabla `users`)
separada y vincular opcionalmente cada Cliente a su Cuenta (1:1), en lugar de
extender Cliente con credenciales o renombrar Cliente a User.

Razones: admin y staff necesitan Cuenta sin ser socios (una fila en Clientes
con Estado de Membresía sería un socio falso); el Estado de Membresía (negocio:
puede reservar) y el `activo` de la Cuenta (acceso: puede iniciar sesión) son
conceptos distintos que conviven mal en un solo campo; y los endpoints de V2
(`/v1/auth/*`, `/v1/users*`) deben existir literalmente para cumplir la spec
sin romper el CRUD `/v1/clientes` ya entregado.

Consecuencias: una tabla y una migración más; el seed debe crear Cuentas para
los Clientes existentes; las reglas de negocio (reservas, pagos) leen el
perfil Cliente y el control de acceso lee la Cuenta. Vocabulario completo en
`CONTEXT.md`.
