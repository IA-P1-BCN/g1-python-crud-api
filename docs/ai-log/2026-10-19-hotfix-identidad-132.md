# HOTFIX identidad única en users — #132

- Herramienta: ZCode (GLM), con tres agentes de exploración previos
  (esquema/respuestas, seed/auth, portal+rutas).
- Prompt: hotfix con spec openspec previa — quitar nombre/email de clientes
  (van en users), entrenadores como cuentas staff, arreglar los 404 de rutas
  del frontend, añadir user_id/nombre/email a reservas, seed con 3
  entrenadores (boxeo/yoga/spinning) y 22 usuarios demo; README con una
  cuenta demo por rol (sin la del .env) y reestructura visual.
- Decisión/alcance: migración 2bf39c12ed06 (backfill de cuentas inaccesibles
  con hash de secreto descartado + drop de columnas); ClienteInput/Response
  solo perfil con identidad resuelta en lectura; ReservaResponse con
  id_user/nombre/email; SPA_ROUTES + auth/marketplace/staff/admin; seed
  reescrito (3 staff por entrenador, 22 socios con contraseña demo común);
  ADR 0002. Breaking: contrato de /v1/clientes y sus filtros (commit con !).
- Errores corregidos durante la sesión: ruff detectó import sin usar y orden;
  un test propio cazó que las claves extra del .env se perdían (ya corregido
  en #107); en tests, editable() excluía "nombre" también de entrenadores.
- Verificación: `task lint`, `task spec:validate` 12/12, suite completa
  **388 tests** en verde (unidad + integración MySQL real con la migración
  aplicada), `task demo` de principio a fin, `npx tsc --noEmit` del frontend.
- Revisión: la evidencia automatizada no sustituye la revisión humana de la
  PR; vigilar el downgrade de la migración y el comportamiento en Render.
