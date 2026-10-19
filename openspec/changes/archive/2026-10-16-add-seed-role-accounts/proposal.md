## Why
#118 (subtarea de la STORY #38): la demo de roles necesita un admin y un staff
con email `@gymflow.com` y contraseña común, porque el rol no es editable por la
API (PUT/PATCH `/v1/users` solo acepta nombre/email/password) y sin una cuenta
staff creada por seed no se puede mostrar el lane de entrenador en `/docs`.
Hoy `task seed` solo crea el admin de `ADMIN_EMAIL` (por defecto
`admin@example.com`) y clientes inactivos con hash aleatorio; en la base local
solo existe `demo@gymflow.com`.

## What Changes
- `scripts/seed_accounts.py` gana `seed_staff`, invocada por `task seed`
  (`seed_gym.main`), que crea la Cuenta `staff@gymflow.com` (rol `staff`,
  activa) vinculada a un Entrenador libre; idempotente y sin restablecer
  credenciales.
- El email por defecto del admin pasa a `admin@gymflow.com` (settings y
  `.env.example`), conservando `ADMIN_EMAIL` si ya está configurado.
- Ambas cuentas nuevas usan la contraseña demo `Demo56789012`; la del admin
  sigue mandando `ADMIN_PASSWORD` cuando está definida.
- Documentación en README y tests de idempotencia y login.

## Capabilities
### New Capabilities
- `seed-role-accounts`: cuentas demo de admin y staff creadas por `task seed`.

### Modified Capabilities
Ninguna.

## Impact
- `scripts/seed_accounts.py`, `scripts/seed_gym.py` (salida), `config/settings.py`,
  `.env.example`, `README.md`.
- Tests: `tests/integration/test_seed_role_accounts_mysql.py` (nuevo).
- No toca contratos HTTP, migraciones ni el dominio.
