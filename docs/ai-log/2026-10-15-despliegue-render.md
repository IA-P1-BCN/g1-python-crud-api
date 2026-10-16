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

### Ampliación (mismo día): tarjeta en Render sin servicios de pago

- Petición de la usuaria: usar la tarjeta añadida a Render para poder desplegar,
  pero **sin ningún servicio de pago**. Primero se había propuesto meter el
  MySQL en `render.yaml` (pserv + disco); se descartó porque todo lo que
  persiste en Render es de pago (pserv desde 7 $/mes + disco), y la
  alternativa sin coste es el MySQL externo gratuito.
- Decisión: `render.yaml` vuelve a definir solo la API gratuita; MySQL sigue
  fuera (Aiven gratuito, TLS). `MYSQL_PORT` pasa a `sync: false` porque Aiven
  asigna un puerto distinto de 3306, y se retira `branch: main` para poder
  probar el Blueprint desde la rama de la PR.
- Nuevo entrypoint: reintentos de `alembic upgrade head` (40 × 5 s) y
  `python -m scripts.seed_gym` antes de uvicorn: cada arranque del contenedor
  hace lo de `task demo` y luego lo de `task dev`, sin pasos manuales.
- Corrección: se descartó el esquema de costes de Render con pserv/disco
  (7 $/mes + 1,25 $/mes) por falta de presupuesto de pago; queda anotado en
  README/AGENTS que la tarjeta no se factura.
- Tests de esta ampliación: ver abajo en el resumen de validación.

### Validación de la ampliación (Fase 0)

- `task lint` (ruff) sin errores; `task test`: **205 tests aprobados, 0
  saltados**, contra el MySQL local de Docker.
- `render.yaml` validado contra el JSON Schema público de Render.
- Imagen Docker reconstruida y probada con el entrypoint nuevo. El 3306 local
  lo ocupaba un MySQL nativo del equipo, así que el `.env` local (no se
  commitea) pasó a `MYSQL_PORT=3307`, la escapatoria que ya documenta
  `.env.example`. En los logs del contenedor se ve `alembic upgrade head` →
  seed (`Datos demo de GymFlow disponibles...`, `Cuentas: 16 creadas;
  0 omitidas`) → uvicorn; `GET /health`, `/health/db` (versión 0.3),
  `/docs` y `/v1/clientes` responden 200 con datos demo.
- Pendiente de Fase 2: deploy real en Render con Aiven y su evidencia.
### Corrección (2026-10-16): CA de Aiven
- El primer deploy falló con CERTIFICATE_VERIFY_FAILED: Aiven firma con una CA
  propia que `ssl.create_default_context()` no reconoce.
- Decisión: nueva variable `MYSQL_SSL_CA` (contenido PEM o ruta) en
  `config/settings.py`, con tests; se rellena en el Dashboard de Render.
- Error posterior: la variable no existía en Render y el usuario/contraseña
  de Aiven no coincidían; corregido en el Dashboard.
- Verificado: `/health/db` responde ok (esquema 0.3) en Render.