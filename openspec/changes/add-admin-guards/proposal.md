## Why
#65 limita la administración de Cuentas al rol admin; #64 está integrada.
## What Changes
Dependencia requires_admin en GET /v1/users y DELETE /v1/users/{id}.
## Capabilities
### New Capabilities
- `admin-guards`: autorización administrativa de Cuentas.
### Modified Capabilities
Ninguna.
## Impact
Dependencia HTTP, rutas, Swagger, documentación y tests por rol.
