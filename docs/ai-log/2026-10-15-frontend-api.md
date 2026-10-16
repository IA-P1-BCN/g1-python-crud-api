# 2026-10-15 — Integración frontend con la API

- **Herramienta/modelo:** OpenCode (claude-haiku-5-5).
- **Alcance:** `openspec/changes/add-frontend-api-integration/`.

## Prompts clave
- Comprobar si la interfaz puede integrarse con los endpoints de la API.
- Integrar todo el backend en la interfaz; alta de usuario demo por la UI; spec al final.

## Hallazgos
- Los cambios de Spartan (package.json, tsconfig, styles.css, auth.service) estaban en un
  `git stash` y se recuperaron con `git stash pop` sin conflictos. Antes de recuperarlos
  tsc fallaba con ~90 errores.
- Las reservas exigen ficha Activa y al menos un pago. Una cuenta registrada por la UI
  sale Inactiva y sin pagos, así que el demo necesita activación y pago por API.
- La API rechaza `@gym.test` como dominio reservado; el demo usa `demo@example.com`.

## Decisiones
- Implementaciones HTTP como providers por defecto; mocks solo en tests.
- Token JWT en sessionStorage, adjunto con un interceptor funcional.
- Un 401 de una petición protegida cierra la sesión; el 401 del login no.
- CRUD completo por recurso en `services/api/`, sin pantallas para clientes, pagos,
  cuentas ni export (pedido explícito).
- Aviso de presupuesto del bundle subido de 500 kB a 600 kB (Spartan y HttpClient).

## Verificación
- `npm test`: 75/75. `npm run build`: compila (aviso de presupuesto dentro de 600 kB).
- `task lint`: sin errores. `task test`: 208 passed. `task spec:validate`: 13/13.
- Smoke contra la API real a través del proxy de `ng serve`: login, `/users/me` con
  Bearer, listados con filtros, reserva, duplicado 409 y token inválido 401.

## No comprobado
- No se probó la interfaz en un navegador: el flujo visual de login, reserva y
  cancelación está validado por tests unitarios y por la API, no por clic en la UI.
- Los endpoints V1 siguen públicos hasta #38; el interceptor ya envía el token.
- Sin CORS en producción: el build depende del proxy de desarrollo.
- `cargarClasesConCupo` hace una petición de reservas por clase; con muchas clases
  conviene una sola consulta.
