# Edición de Cuentas — #58

- Herramienta: Codex (GPT-6), skills gymflow-review/gymflow-verify.
- Prompt: ejecutar las tareas asignadas en orden y según los conceptos del proyecto.
- Spec previa: add-user-update; dependencia de PR #99.
- Decisión/alcance: Añade PUT/PATCH autenticados de nombre, email y contraseña. PUT exige nombre/email, PATCH conserva omitidos y ambos conservan el hash si no se envía password. Rechaza campos protegidos y entradas inválidas con 422, inexistentes con 404 y duplicados con 409. Verifica login con la contraseña nueva.
- Verificación: task test **183 aprobados**, cero saltados; task lint,
  task spec:validate y git diff --check correctos. Aviso previo Starlette/httpx.
- Revisión: contrato, capas, errores y no exposición de credenciales comprobados.
  La evidencia automatizada no sustituye la revisión humana de la PR.
