# Despliegue en Render — 2026-10-15

- OpenCode (mimo-v2.6-flash-free), petición directa de la usuaria: "ejecuta
  Phase 1" del plan de despliegue en Render (API + MySQL + Frontend).
- Prompt clave: desplegar varias imágenes Docker (API, MySQL, Frontend) en
  Render con redeploys automáticos al hacer push a `main`; aclarado después
  que la plan gratuita no admite MySQL con disco y que no hacen falta
  secretos de GitHub si se usa la integración Git de Render.
- Decisiones: MySQL externo en Aiven (gratuito, TLS obligatorio) en vez de
  contenedor en Render; API con `Dockerfile` multi-stage de uv; frontend
  futuro como sitio estático gratuito; `render.yaml` con
  `autoDeployTrigger: commit` y secretos `sync: false` en el Dashboard.
- Aceptado: `MYSQL_SSL` activa un `SSLContext` compartido por engine y
  Alembic; CORS con `ALLOWED_ORIGINS` vacío por defecto (sin cruce de
  dominios hasta que exista frontend); entrypoint que migra antes de servir.
- Rechazado: docker-compose para Render (no lo usa la plataforma), API key
  de Render en secretos de GitHub (acceso de cuenta completo, innecesario con
  integración Git), migración a PostgreSQL por pérdida del contrato MySQL.
- Correcciones: verificación del `render.yaml` contra el JSON Schema público
  de Render (la CLI no estaba autenticada en la sesión); el proceso sin
  privilegios no podía crear `logs/` porque WORKDIR dejaba `/app` como root
  (`chown` en la imagen); el `.venv` local apuntaba a una ruta antigua y el
  nuevo Python 3.15 del equipo forzaba un build de `httptools` sin
  compilador, así que se fija `.python-version` en 3.14 (igual que el
  Dockerfile).
- Tests: `ruff check` sin errores; 205 tests aprobados (0 saltados) tras
  `task migrate` local; imagen Docker construida y probada con el MySQL local
  (`/health` 200 y `/health/db` 200 con esquema 0.3; el entrypoint aplicó
  alembic antes de arrancar uvicorn). No se comprobó un deploy real de
  Render en esta fase (pendiente: Aiven + Dashboard, fase 2).
- Pendiente: revisión humana; creación del frontend y su Blueprint (fase 3).
