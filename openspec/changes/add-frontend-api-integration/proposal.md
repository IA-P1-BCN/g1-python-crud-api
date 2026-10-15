## Why
La interfaz Angular usaba datos mock para autenticación, clases y reservas. La API
(/v1/auth, /v1/users, /v1/clientes, /v1/entrenadores, /v1/clases, /v1/reservas,
/v1/pagos, /v1/export) ya está en main, así que la interfaz debe consumirla.

## What Changes
- Capa HTTP compartida: `provideHttpClient`, interceptor de Bearer, traducción de
  errores (status 0 → NetworkError, resto → ApiError con el `detail` del servidor) y
  paginación por offset/limit.
- Implementaciones HTTP de `AuthService`, `ClaseService` y `ReservaService`
  registradas en `app.config.ts`; los mocks quedan para tests.
- Clientes de recurso CRUD para clientes, entrenadores, clases, reservas, pagos,
  cuentas y export CSV, sin pantallas asociadas.
- El token JWT se guarda en sessionStorage; un 401 de una petición protegida cierra
  la sesión local.

## Capabilities
### New Capabilities
- `frontend-api-integration`: consumo HTTP de la API desde la interfaz.
### Modified Capabilities
Ninguna.

## Impact
`frontend/src/app/core/http/`, `core/auth/` (HttpAuthService, token), `services/`
(implementaciones y clientes `api/`), `app.config.ts`, `angular.json` (aviso de
presupuesto a 600 kB) y tests unitarios con HttpTestingController. Sin cambios en
el backend.
