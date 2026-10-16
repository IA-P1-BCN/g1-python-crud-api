# 2026-10-15 — #83 — Pantalla de login (frontend Angular)

- **STORY:** #42 (portal web del socio). Tarea: #83. Bloqueada en GitHub por #55
  (login real); se avanza con mock.
- **Herramienta/modelo:** OpenCode (agente), modelo `claude-haiku-5-5`.
- **Spec previa:** [add-frontend-login](../../openspec/changes/add-frontend-login/proposal.md).
  Escrita y validada con `openspec validate --strict` antes de crear `frontend/`.
- **Decisiones:**
  - `frontend/` dentro del repo, con npm (no pnpm) y su propio lockfile.
  - `AuthService` como clase abstracta; `MockAuthService` seleccionado en
    `app.config.ts`. Los componentes no conocen la implementación.
  - Errores tipados (`InvalidCredentialsError`, `NetworkError`) traducidos en el
    componente; no se comparan cadenas.
  - Proxy de Angular para `/v1`; sin cambios de CORS en el backend.
  - Sin Dockerfile ni servicio en compose: se coordina con la persona de deploy.
  - Sin Tailwind ni Spartan en esta entrega: se añaden en una tarea posterior.
- **Qué salió bien:** scaffolding de Angular 22 sin archivos de IA ni SSR; build
  correcto; tests de mock y de la pantalla cubren los escenarios de la spec.
- **Errores y correcciones:**
  - El test de «botón deshabilitado» fallaba porque comprobaba el estado antes de
    que terminara la promesa; se ajustó el test, no el componente.
  - `docker start gym-mysql`: el contenedor llevaba parado días; se arrancó sin
    borrar datos.
  - La API cargaba el puerto 3306 desde `.env` aunque el `.env` local apuntaba al
    3307; se arrancó con `MYSQL_PORT=3307` como variable de entorno. El `.env` no se
    modificó en esta sesión.
- **Validación (resultados reales):**
  - `openspec validate --all --strict --no-interactive`: 3 cambios válidos.
  - `ruff check .`: correcto. `pytest` con MySQL 8.4 en 3307: **122 passed, 0 skipped**.
  - `ruff format --check .`: 5 ficheros ya sin formatear en `main` (no tocados en esta
    PR: `config/logging_config.py` y 4 tests/CSV). Pendiente de tarea aparte.
  - `frontend/`: `npm test` 12/12 y `npm run build` correcto.
  - Proxy comprobado de extremo a extremo: `GET 127.0.0.1:4200/v1/clases` → 200 con
    datos de la BD.
- **Pendiente:** revisión humana; Tailwind y Spartan; Dockerfile y compose (persona
  de deploy); implementación HTTP de `AuthService` cuando #55 esté en `main`.
