# Baja de Cuentas — #59

- Herramienta: Codex (GPT-6), skills gymflow-review/gymflow-verify.
- Prompt: ejecutar las tareas asignadas en orden y según los conceptos del proyecto.
- Spec previa: add-user-delete; dependencia de PR #100.
- Decisión/alcance: Añade DELETE /v1/users/{id} autenticado con borrado físico, 204 sin cuerpo y 404 para inexistentes. Conserva el Cliente vinculado y su historial; la Cuenta desaparece y sus tokens dejan de resolver identidad. Soft delete y permisos de admin permanecen en #73/#65.
- Verificación: task test **186 aprobados**, cero saltados; task lint,
  task spec:validate y git diff --check correctos. Aviso previo Starlette/httpx.
- Revisión: contrato, capas, errores y no exposición de credenciales comprobados.
  La evidencia automatizada no sustituye la revisión humana de la PR.
