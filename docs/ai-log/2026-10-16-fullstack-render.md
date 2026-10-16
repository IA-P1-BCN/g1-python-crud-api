# 2026-10-16 — #29: despliegue fullstack en Render

- **PR/spec:** [#109](https://github.com/IA-P1-BCN/g1-python-crud-api/pull/109),
  [deploy-fullstack-render](../../openspec/changes/deploy-fullstack-render/).
- **Herramienta/modelo:** OpenCode, OpenAI gpt-6.1-sol. Skill
  `gymflow-verify` utilizada para comprobar evidencia y escenarios.
- **Prompts clave:** integrar las PR mergeadas, desplegar frontend y API en
  Render conservando MySQL, seguir pushes a main y publicar la PR; solo Free.
- **Decisiones:** integrar #110/#111, conservar el entrypoint con migraciones
  y seed; Compose fija PORT=8000 y MYSQL_SSL=false. Nginx configurable por
  PORT/API_UPSTREAM, HTTP local y HTTPS público con Host/SNI/verificación CA
  en Render. Free no acepta tráfico privado entrante. Mantener Aiven y secretos
  fuera del repositorio. Documentar sincronización del Blueprint y alta manual
  del frontend cuando la API existente no pertenece a un Blueprint.
- **Errores y correcciones:** parche inicial fallido al editar dos veces un
  archivo; reaplicado por partes. La primera prueba Compose falló en el seed
  por ADMIN_PASSWORD local ausente/inválida; `task env` generó el valor sin
  publicarlo y el arranque posterior fue correcto. Una comprobación de merge
  usó test -d sobre MERGE_HEAD, que es un fichero; se verificó con rev-parse y
  se resolvieron los conflictos Dockerfile/.dockerignore antes de continuar.
- **Verificación:**
  - `task spec:validate`: 16 cambios válidos.
  - `task lint`: ruff limpio.
  - `task db:up && task migrate && task test`: 216 aprobados, 0 fallidos,
    0 saltados, MySQL real; aviso de deprecación Starlette/httpx.
  - Frontend `npm ci`, `npm test -- --watch=false`: 110 tests aprobados en
    23 archivos; `npm run build`: correcto. npm informa 13 vulnerabilidades
    (6 moderate, 7 high) en el árbol de dependencias existente.
  - Schema oficial Render validado con PyYAML/jsonschema. La CLI de Render
    no pudo validar por falta de login; no se presenta como ejecutada con éxito.
  - Ambas imágenes construidas. Compose: MySQL, API y frontend saludables;
    nginx -t correcto; raíz y /perfil sirven SPA; /health JSON 200;
    /v1/clientes?limit=1 JSON 200; login demo y /v1/users/me con Bearer 200;
    API /health/db 200, esquema 0.3.
  - Misma imagen frontend con PORT=10000 y API_UPSTREAM público de Render:
    /health JSON 200 y /v1/clientes?limit=1 JSON 200 por HTTPS verificado.
  - diff --check del índice señala tres espacios finales en app.routes.ts
    heredados de main; no son cambios de esta entrega. Se comprueba también
    el diff contra origin/main.
- **Pendiente:** revisión humana y merge; sincronizar Blueprint/crear frontend
  en Dashboard y verificar su URL pública. La prueba HTTPS anterior ejecutó
  Nginx local contra la API real, no un frontend ya desplegado en Render.
