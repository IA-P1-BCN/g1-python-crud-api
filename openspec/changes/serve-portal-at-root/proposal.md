## Why
La raíz del servicio actual de Render devuelve 404 y el portal no está servido.
Continuación de #29: el usuario solicita el contenido de /portal directamente en /.

## What Changes
- Angular se construye en la imagen de la API y FastAPI sirve la SPA.
- El portal ocupa / y sus pantallas pierden el prefijo /portal.
- Las rutas antiguas redirigen y la API conserva su contrato.

## Capabilities
### New Capabilities
- `portal-root`: SPA en el mismo origen de la API y navegación desde la raíz.

## Impact
Dockerfile, Blueprint, entrada HTTP, rutas Angular, pruebas y documentación.
