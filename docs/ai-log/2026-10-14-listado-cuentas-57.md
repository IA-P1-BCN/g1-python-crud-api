# Consulta de Cuentas — #57

- Herramienta: Codex (GPT-6), skills gymflow-review/gymflow-verify.
- Prompt: ejecutar las tareas asignadas en orden y según los conceptos del proyecto.
- Spec previa: add-user-listing; dependencia de PR #98.
- Decisión/alcance: Añade GET /v1/users y GET /v1/users/{id} protegidos con JWT, orden estable, paginación offset/limit y 404. Las respuestas excluyen credenciales; la política admin-only queda en #65.
- Verificación: task test **169 aprobados**, cero saltados; task lint,
  task spec:validate y git diff --check correctos. Aviso previo Starlette/httpx.
- Revisión: contrato, capas, errores y no exposición de credenciales comprobados.
  La evidencia automatizada no sustituye la revisión humana de la PR.
