# Cuenta separada del Cliente (#53)

## Why
V2 necesita credenciales sin mezclar identidad y membresía. Este cambio desbloquea
el registro de #54 y respeta el ADR 0001.

## What Changes
- Entidad Cuenta, tabla users, vínculo opcional 1:1 y hash Argon2.
- Migración reversible y seed idempotente de administrador y clientes con email.
- Secretos tipados; no se publican contraseñas ni se alteran clientes existentes.

## Capabilities
### New Capabilities
- `accounts-model`: persistencia e inicialización de cuentas.

### Modified Capabilities
Ninguna.

## Impact
Dominio, infraestructura, migraciones, configuración, seed, documentación y tests.
