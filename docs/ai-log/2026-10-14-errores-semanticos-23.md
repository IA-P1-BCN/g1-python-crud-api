# Errores semánticos — #23

- Herramienta: Codex (GPT-6), skills gymflow-review/gymflow-verify.
- Prompt: ejecutar las tareas asignadas en orden y según los conceptos del proyecto.
- Spec previa: add-semantic-errors; dependencia de PR #102.
- Decisión/alcance: Consolida los handlers 400/401/403 de las tareas previas con pruebas de formato, reto Bearer y nivel de logging. Mantiene 404/409/422/500/503 y evita imprimir valores sensibles en errores de configuración. La semántica 403 actual corresponde a Cuenta autenticada inactiva; permisos por rol siguen en #65.
- Verificación: task test **200 aprobados**, cero saltados; task lint,
  task spec:validate y git diff --check correctos. Aviso previo Starlette/httpx.
- Revisión: contrato, capas, errores y no exposición de credenciales comprobados.
  La evidencia automatizada no sustituye la revisión humana de la PR.
