## Why
#132: la identidad duplicada (clientes con nombre/email propios y users con
los suyos) desincroniza los datos y rompe la demo; el portal da 404 JSON al
refrescar rutas nuevas; las reservas no muestran quién reservó; y faltan
datos demo (3 entrenadores, 22 usuarios).

## What Changes
- `clientes` pierde `nombre` y `email` (migración con backfill): la
  identidad vive EXCLUSIVAMENTE en `users`; `/v1/clientes` resuelve la
  identidad del user vinculado en la respuesta.
- `ReservaResponse` añade `id_user`, `nombre` y `email` (join
  reservas→clientes→users).
- `SPA_ROUTES` aprende `auth`, `marketplace`, `staff` y `admin`.
- Seed: 3 entrenadores (Boxeo/Yoga/Spinning) con cuenta staff cada uno y
  22 usuarios demo `socio01..socio22@gymflow.com`.
- README: 1 cuenta demo por tipo con contraseña (sin la del `.env`) y
  reestructura visual.

## Capabilities
### New Capabilities
- `reservas-persona`: identidad de quién reserva en la respuesta.
- `seed-demo`: datos demo completos y verificables.
### Modified Capabilities
- `clientes-perfil`: perfil sin identidad almacenada, resuelta de users.
- `portal-rutas`: rutas del portal sin 404.

## Impact
Migración (breaking), modelos, entidades, schemas, controllers, repositorios,
filtros, CSV, spa.py, frontend staff, seeds, README, tests.
