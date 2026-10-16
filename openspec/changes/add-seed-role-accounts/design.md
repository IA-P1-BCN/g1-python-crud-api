## Context
`seed_accounts` recibe `admin_email`/`admin_password` desde settings y solo
garantiza el admin. El staff no puede nacer por API porque el rol no es
editable y `PUT /v1/users/{id}/entrenador` exige admin, por lo que el seed es
el único punto de creación controlado. Un staff sin `id_entrenador` ve listas
vacías (#106), así que el vínculo debe nacer con la cuenta.

## Decisions
- La cuenta staff se crea con `seed_staff` en `scripts/seed_accounts.py`,
  llamada por `seed_gym.main` después de `seed_demo` y `seed_accounts`, en la
  misma transacción: misma garantía de idempotencia (email único
  `uq_users_email`). `seed_accounts` no cambia de firma ni de comportamiento,
  para no alterar sus tests existentes.
- Vínculo: se elige el Entrenador con menor `id_entrenador` sin Cuenta vinculada
  (`uq_users_id_entrenador`). Si no hay Entrenador libre, la cuenta se omite y
  el resumen lo indica; nunca se crea un staff sin vínculo.
- Contraseña del staff: constante `DEMO_PASSWORD` (`Demo56789012`), la misma
  que la cuenta `demo@gymflow.com` de la migración `ca6c9ed6b7e8`, para que la
  demo use una única credencial documentada. La del admin sigue viniendo de
  `ADMIN_PASSWORD` (obligatoria en el seed) porque es la cuenta administrativa
  real del entorno.
- Email por defecto del admin: `admin@gymflow.com` en `Settings.admin_email`
  y en `.env.example`. `bootstrap_env` no pisa `ADMIN_EMAIL` ya configurado,
  así que los `.env` existentes conservan su valor.
- Sin migración: el esquema ya admite `staff` y `id_entrenador` (migración
  `7a0f6a730e04`); la versión de esquema no cambia.

## Risks / Trade-offs
- Contraseña demo en el repositorio: es una cuenta de datos ficticios, ya
  documentada en el README; ninguna cuenta real usa ese valor. `validate_admin_password`
  sigue rechazando marcadores para el admin.
- Si un Entrenador existente ya está vinculado a otra Cuenta staff, se omite
  en lugar de reasignar: el seed no toma identidades ajenas.

## Dependencies
- Issue #118 (STORY #38); requiere migración `ca6c9ed6b7e8` aplicada para la
  cuenta `demo@gymflow.com` y datos demo (entrenador) de `seed_demo`.
