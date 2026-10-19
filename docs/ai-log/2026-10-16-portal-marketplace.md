# 2026-10-16 — Rediseño del portal: marketplace Barnaspace (spec add-barnaspace-ux)

- **Alcance**: cambio OpenSpec `add-barnaspace-ux` (spec creada el
  2026-10-15, commit `4344b5c`). Solo frontend Angular; el backend no cambia.
- **Herramienta / modelo**: OpenCode con mimo-v2.6-flash-free, en la rama
  `feature/portal-redesign` rebasada sobre `main` (PRs #112–#119).
- **Rutas nuevas**: `/marketplace` (catálogo con buscador, detalle de clase
  con cupo y reserva), `/auth` (login y registro fuera del shell, sin menú),
  `/staff` (mis clases y reservas de mis clases) y `/admin` (dashboard con
  gráficas de barras y la gestión previa de clientes, entrenadores, clases,
  reservas, pagos, cuentas y exportación CSV). Guard `authGuard` en rutas
  privadas con `returnUrl`; redirecciones de las rutas antiguas (`/`,
  `/login`, `/registro`, `/clientes`, …) a las nuevas.
- **Menú por rol** (`menu.component`): público ofrece iniciar sesión /
  crear cuenta; cliente ve catálogo y mis reservas; staff añade su panel;
  admin añade el panel de gestión completo. «Mi perfil» siempre con sesión.
- **Servicios**: `ClaseService.obtener(cupo)` expuesto en el servicio
  (mock y http); home y detalle usan el cupo real de
  `GET /v1/clases/{id}/cupo`; «Mis reservas» cancela con
  `DELETE /v1/reservas/{id}` liberando plaza.
- **Tests**: specs adaptados (login, registro, menú, rutas, mis-reservas) y
  nuevos (home marketplace, dashboard admin). Verificación completa:
  `task spec:validate` (24/24), `task lint`, `task test` (376 passed,
  tras `task migrate` para la migración `7a0f6a730e04` pendiente en local),
  `npm test` (117 passed, 26 ficheros) y `npm run build` (bundle ok).
- **Decisiones**: el frontend conserva los mocks como fallback (sin backend
  responde datos ficticios); el logo de login/registro apunta a
  `/marketplace` (el guard vuelve a login si no hay sesión).
- **No comprobado en navegador manual**: smoke visual de las páginas nuevas
  con la API real; se deja para la revisión humana previa al merge.
- Issue enlazada desde la PR del cambio.
- **Ampliación posterior (2026-10-19)**, petición de la usuaria en revisión:
  el menú del admin pasa a ser exclusivo de administración (solo «Mi perfil»,
  bloque Admin y «Cerrar sesión», sin catálogo, mis reservas ni bloque staff)
  y el login de admin sin `returnUrl` aterriza en `/admin` (dashboard).
  Specs del cambio y tests de menú/login actualizados; `npm test` 119 passed,
  `task spec:validate` 24/24 y frontend reconstruido en Docker.
- **Ampliación 2026-10-19 (2)**: el login de staff sin `returnUrl` aterriza
  en `/staff` (su panel). Spec «Destino tras el login» y tests actualizados;
  `npm test` 120 passed, `task spec:validate` 24/24, frontend reconstruido.
- **Ampliación 2026-10-19 (3)**: la cabecera del shell pasa a ser reactiva
  por rol (antes tenía Catálogo/Mis reservas/Mi perfil hardcodeados para
  todos): cliente ve catálogo y mis reservas; staff, Mi panel y Mis clases;
  admin, Dashboard/Clientes/Entrenadores/Clases; sin sesión, solo el logo.
  El resto sigue en el menú desplegable. Spec «Cabecera por rol» y test
  nuevo del shell; `npm test` 125 passed, `task spec:validate` 24/24.
