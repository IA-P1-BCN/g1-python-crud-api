## Why
#66 permite gestionar la Cuenta propia y exige la contraseña actual para cambiarla.
## What Changes
PATCH /v1/users/me edita nombre/email/password; password requiere current_password.
La edición por ID queda administrativa para evitar eludir esa comprobación.
La consulta por ID permite admin o propietario, sin exponer otras Cuentas.
## Capabilities
### New Capabilities
- `self-profile`: actualización autenticada de la Cuenta propia.
### Modified Capabilities
Ninguna.
## Impact
Schemas, controlador/caso de uso, guardas, documentación y tests HTTP/MySQL.
