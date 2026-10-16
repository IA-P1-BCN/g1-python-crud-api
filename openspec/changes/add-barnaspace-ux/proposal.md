# add-barnaspace-ux

## Why

STORY #42 (Portal web del socio) pide una web del gimnasio; las issues #124, #125
y #126 concretan el rediseño. El frontend actual es un portal funcional pero
plano (inicio con dos tarjetas, gestión colgando del menú sin guardas y sin
panel propio del staff). La usuaria ha fijado como referencia la UX de su
proyecto BarnaSpace (marketplace de espacios con roles client/host/admin) y ha
decidido replicarla en GymFlow con el mapeo: espacio→clase, reservar
espacio→reservar clase, host→staff, admin→admin.

La API ya lo permite todo desde las PRs #112–#119: JWT en todo `/v1`, permisos
por rol y propietario (GymScope), `users.id_entrenador`, cupo agregado en
`GET /v1/clases/{id}/cupo`, filtro `id_entrenador` en clases y seed con
`staff@gymflow.com`. Las issues #122 y #123 se cerraron al detectar este solape.

## What Changes

- **Rutas y guards**: `/marketplace` (catálogo, detalle, mis reservas),
  `/auth` (login/registro), `/staff` (panel del staff) y `/admin` (dashboard y
  gestión). Guards `authGuard`/`staffGuard`/`adminGuard` resolviendo la sesión
  con `GET /v1/users/me`; `/` redirige a `/marketplace`; las rutas antiguas
  redirigen a las nuevas.
- **Marketplace**: home con hero y buscador (`q` sobre `nombre_clase`), grid de
  resultados con filtros de horario, detalle de clase con plazas disponibles
  (`GET /v1/clases/{id}/cupo`) y reserva (`POST /v1/reservas`), lista
  «Mis reservas» con cancelación (`DELETE /v1/reservas/{id}`).
- **Panel staff** (`/staff`): «Mis clases» y «Reservas de mis clases»
  consumiendo el alcance de servidor (el staff solo recibe lo suyo); cancelar
  reserva y marcar asistencia (`PUT /v1/reservas/{id}` con `asistio`).
- **Admin** (`/admin`): dashboard con gráficas ng2-charts alimentadas con los
  listados reales (reservas por mes, asistidas vs canceladas, clientes vs
  entrenadores, clases por entrenador) y las pantallas de gestión reubicadas.
- **Menú**: por rol — cliente (catálogo, mis reservas, perfil), staff (+ panel),
  admin (todo); sin sesión, solo login/registro.
- **Consumo real**: todos los flujos hablan con `/v1`; los mocks solo existen en
  specs de Vitest.

## Alcance excluido

- Imágenes de clase, categorías, mapas, favoritos, Stripe y Cloudinary
  (sin API ni negocio equivalente).
- Estados de reserva «pendiente/aprobada»: la reserva es inmediata (PRD), el
  staff cancela o marca asistencia.
- Wizard «hazte staff» y aprobación de publicaciones (no hay flujo de solicitudes).
- Endpoint de métricas nuevo: las gráficas se calculan del lado cliente con los
  listados (limitación de 100 por página documentada).
- Angular Material: se replica la estructura y flujos, manteniendo Spartan/Tailwind.

## Capabilities

### New Capabilities
- `portal-marketplace`: marketplace de clases, panel staff y dashboard admin de
  la interfaz.

### Modified Capabilities
- `frontend-gestion`: la navegación de gestión pasa a `/admin` con
  `adminGuard` (sustituye la decisión de dejar las guardas desactivadas en el
  alcance anterior).

## Impact

Frontend: `app.routes.ts`, guards nuevos en `core/auth/`, menú, nuevas features
`marketplace`, `staff`, `admin/dashboard`, servicios existentes reutilizados sin
mocks en `src/`. Backend: sin cambios. Dependencias: #124, #125, #126 ·
STORY #42.
