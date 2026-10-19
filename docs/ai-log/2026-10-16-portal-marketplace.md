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
- **Ampliación 2026-10-19 (4)**: «Repaso Spartan completo» de UI (petición
  de la usuaria, guía `.agents/skills/spartan`). Instalados con el CLI
  `@spartan-ng/cli` los componentes que faltaban (`field`, `separator`,
  `skeleton`, `empty`, `spinner`, `sonner`) en `shared/ui/` con sus paths
  en `tsconfig.json`; `package.json`/lock sin cambios (el CLI re-fijó
  `@ng-icons`, se revirtió; no añade dependencias). `<hlm-toaster />`
  global en `app.html`. En las 15 páginas con formulario/listado:
  formularios de alta/edición a `hlmField` + `hlm-field-error` (los de
  filtro/búsqueda sin validación conservan `hlmLabel`); estados de carga
  `<p>Cargando…</p>` → `hlmSkeleton` (tabla o tarjeta según la página);
  estados vacíos → `hlmEmpty` (selectores de atributo); y avisos
  `app-toast`/signal `aviso` → `toast.success/error` de `@spartan-ng/brain/sonner`.
  Helper de test `testing/toast.ts` (`mensajesDeToast`/`limpiarToasts`
  sobre la cola global `toastState`); 8 specs adaptados (los mensajes de
  toast ya no están en el DOM de la página). Verificación: `npm test`
  125 passed (27 ficheros), `npm run build` ok, `task spec:validate` 24/24,
  `task lint`, `task test` 376 passed, frontend reconstruido en Docker y
  smoke (`/`, `/health`). **No comprobado en navegador manual**: smoke
  visual de skeleton/empty/toast con la API real; se deja a la revisión
  humana. `barras-chart` y dark mode quedan fuera de este alcance.
- **Ampliación 2026-10-19 (5)**: «iconos en las vistas» para identificar
  más rápido (petición de la usuaria). Juego de iconos lucide registrado
  **una sola vez** en `app.config.ts` con `provideIcons` global (sin
  repetirlo en cada vista). Iconos añadidos en: navegación del shell
  (cabecera + barra móvil, por rol), menú desplegable (cada opción),
  `estado-badge` (Activo/Inactivo/Suspendido), las 14 cabeceras `h1` y los
  botones de acción (Nuevo→Plus, Editar→Pencil, Borrar→Trash2,
  Cancelar→×, Marcar asistencia/Reservar/Guardar→ CircleCheck/CalendarCheck).
  El botón «Reservar» se editó una vez en `clase-card.component.ts`
  (compartido por home y resultados). Solo presentación; sin cambios de
  lógica ni backend. `npm test` 125 passed, `npm run build` ok,
  `task spec:validate` 24/24, frontend reconstruido en Docker y smoke.
