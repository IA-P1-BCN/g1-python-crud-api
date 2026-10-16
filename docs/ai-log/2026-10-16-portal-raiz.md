# 2026-10-16 — #29: portal en la raíz del servicio de la API

- **Spec:** [serve-portal-at-root](../../openspec/changes/serve-portal-at-root/).
  Sustituye la topología de dos servicios de la PR #109 ya mergeada.
- **Herramienta/modelo:** OpenCode, OpenAI gpt-6.1-sol; skills
  `gymflow-verify` (contraste de evidencia) y `render-docker` (multi-stage).
- **Prompts clave:** el frontend no funciona en /portal; mostrar su contenido
  en la raíz del dominio existente; ejecutar el plan.
- **Decisiones:** Angular se construye con Node y se copia a /app/static;
  FastAPI monta archivos al final solo si existe build. Fallback restringido
  a pantallas SPA, sin ocultar 404 de API o assets. El shell de /portal pasa
  a /; enlaces y login sin prefijo, con redirección de URL antiguas.
  Render conserva un único servicio Free y Aiven. Compose conserva Nginx.
- **Errores y corrección:** primer test nuevo de navegación tenía mock de
  ClaseService incompleto (faltaba listarEntrenadores). Vitest señaló un error
  no capturado aunque los asserts pasaran; se completó el mock y se repitió
  hasta obtener 112 tests aprobados sin errores no capturados.
- **Evidencia:**
  - `task spec:validate`: 17 cambios válidos; `task lint`: limpio.
  - `task test`: 218 aprobados, 0 fallidos, 0 saltados, con MySQL disponible;
    aviso de deprecación Starlette/httpx existente.
  - `npm test -- --watch=false`: 112 aprobados, 24 archivos; build correcto.
    Tests de routing comprueban portal en / y redirecciones /portal y
    /portal/clases; tests HTTP cubren recursos, enlaces profundos y ausencia
    de build. npm sigue informando 13 vulnerabilidades del árbol existente.
  - `docker compose up -d --build --wait api`: imagen multi-stage construida,
    API saludable. HTTP real al puerto 8000: /, /clases, /perfil, /portal y
    /portal/clases sirven Angular; bundle JS 200; archivos ausentes y
    /v1/no-existe 404; Swagger, health/db, login demo y perfil Bearer correctos.
  - Blueprint validado contra schema oficial con PyYAML/jsonschema. CLI Render
    sin login; no se atribuye a esa CLI una validación exitosa.
- **Pendiente:** revisión humana, merge y auto-deploy de main; comprobar raíz
  pública al terminar el deploy. La comprobación actual es local con la imagen
  Docker, no evidencia de que Render haya publicado esta rama.
