## Why
#67 permite configurar la duración de las sesiones sin modificar código.
## What Changes
ACCESS_TOKEN_EXPIRE_MINUTES, entero de 1 a 1440, por defecto 30; el emisor JWT
recibe el ajuste. La verificación sigue exigiendo exp y devuelve 401 al caducar.
## Capabilities
### New Capabilities
- `token-expiry`: duración de acceso configurable por entorno.
### Modified Capabilities
Ninguna.
## Impact
Settings, wiring, adaptador JWT, .env.example, documentación y tests.
