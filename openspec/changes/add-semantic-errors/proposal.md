## Why
#23 necesita verificar el contrato completo de errores semánticos ahora que
400 está entregado en #22 y auth aporta 401/403 (#55/#56).
## What Changes
Consolidación del contrato y pruebas de los handlers, sin exponer secretos en
errores de configuración. Documentación detallada Swagger continúa en #60.
## Capabilities
### New Capabilities
- `semantic-errors`: correspondencia estable entre dominio y HTTP.
### Modified Capabilities
Ninguna.
## Impact
Tests de errores, settings y documentación de decisiones.
