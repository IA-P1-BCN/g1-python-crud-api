## Why
Continuación de #118/#29: la demo desplegada necesita acceso admin con
credenciales públicas en README sin publicar la clave del admin privado.

## What Changes
- El seed añade una Cuenta admin demo activa e independiente.
- README publica sus credenciales ficticias; no se alteran Cuentas existentes.
- El entrypoint existente ejecuta el mismo seed al arrancar en Render.

## Capabilities
### New Capabilities
- `admin-demo`: Cuenta administradora pública para la demostración.

## Impact
Scripts de seed, pruebas MySQL/login y documentación. Sin migración ni nuevos servicios.
