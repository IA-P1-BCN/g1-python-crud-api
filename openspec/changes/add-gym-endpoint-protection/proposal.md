## Why
#105 exige identidad acreditada antes de acceder al negocio del gimnasio.
## What Changes
Todos los métodos de clientes, entrenadores, clases, reservas, pagos y export
requieren get_current_user. Se conservan públicos login, registro y healthchecks.
## Capabilities
### New Capabilities
- `gym-endpoint-protection`: autenticación de recursos del gimnasio.
### Modified Capabilities
Ninguna.
## Impact
Wiring de routers, OpenAPI, documentación y pruebas HTTP existentes y nuevas.
