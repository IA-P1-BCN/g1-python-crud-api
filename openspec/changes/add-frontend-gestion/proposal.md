## Why
STORY #42 (Portal web del socio) tiene pendientes #31 («Interfaz de usuario básica»,
incluye «Mi rincón»: membresía y perfil) y #84 («UI: listado, edición y baja de
usuarios», con spec prevista en `openspec/changes/add-admin-ui/`). La capa de datos
ya existe desde `add-frontend-api-integration` (`services/api/`), pero no hay
pantallas de gestión: clientes, entrenadores, clases, pagos, cuentas, exportación ni
perfil propio consumen la API solo por curl.

## What Changes
- Pantallas de gestión bajo `/portal`: clientes, entrenadores, gestión de clases,
  pagos, cuentas y exportación CSV, con listado filtrado, alta, edición y baja.
- Pantalla de perfil propio (`/portal/perfil`) con los datos de `GET /v1/users/me`
  y edición de nombre, email y contraseña con `PATCH /v1/users/{id}`.
- Navegación: grupo «Gestión» en el menú de sesión (visible con rol `admin`/`staff`)
  y enlace «Mi perfil» para cualquier sesión.
- Primitiva de tabla (Spartan/HLM) y descarga de CSV en el navegador.

## Alcance excluido
- Guardas de ruta: `homeGuard`/`invitadoGuard`/`portalGuard` siguen comentados en
  `app.routes.ts` (decisión de la usuaria en esta entrega).
- Autorización por rol en el backend (#65, ⛔ bloquea a #84) y protección JWT del
  resto de `/v1` (#38/#105): la UI solo oculta enlaces de gestión por rol.
- Alta de cuentas desde la gestión (se hace con `POST /v1/auth/register`).

## Capabilities
### New Capabilities
- `frontend-gestion`: pantallas de gestión, perfil y exportación de la interfaz.
### Modified Capabilities
Ninguna.

## Impact
Frontend: nuevas features en `src/app/features/`, rutas en `app.routes.ts`,
`menu.component.ts`, primitiva `shared/ui/table`, `tsconfig.json` (paths) y specs.
Backend: sin cambios. Dependencias: #31, #84 (⛔ #65 abierto), STORY #42.
