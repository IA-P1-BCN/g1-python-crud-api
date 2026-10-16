## Why
#106 impide acceder a datos ajenos después de autenticar. La usuaria confirmó
que staff gestiona solo sus clases/reservas y requiere un vínculo Cuenta–Entrenador.
## What Changes
Vínculo opcional único id_entrenador, asignado solo por admin. Autorización por
recurso y propietario, filtros de alcance antes de paginar, CSV solo admin.
El catálogo de clases/entrenadores sigue disponible al cliente. Un endpoint
de cupo agregado evita exponer reservas ajenas para calcular plazas en el frontend.
## Capabilities
### New Capabilities
- `gym-role-permissions`: permisos del gimnasio y vínculo explícito del staff.
### Modified Capabilities
Ninguna.
## Impact
Migración, Cuenta, puertos/repositorios, casos de uso y wiring; rutas/controllers,
catálogo frontend, documentación y tests de aislamiento real en MySQL.
