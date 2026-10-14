---
name: gymflow-verify
description: Verifica una entrega de GymFlow contra su issue, spec, lint y tests, e informa la evidencia antes de preparar una PR. Úsala para comprobar cambios o diagnosticar verificaciones fallidas.
---

# Verificar una entrega de GymFlow

Trabajar desde la raíz del repositorio y leer `AGENTS.md`, la issue y la spec
del cambio si corresponde. Identificar la rama, el diff y los archivos nuevos
con `git status --short --branch`, `git diff` y `git diff --cached`.
Si el trabajo está commiteado, comparar con la base de la PR; no confundir
un árbol limpio con la ausencia de cambios.

Relacionar los escenarios de aceptación con las comprobaciones existentes.
No añadir tests que solo reproduzcan la implementación ni eliminar tests que
fallen. Para un cambio documental, comprobar enlaces y comandos descritos.

Ejecutar las verificaciones pertinentes:

- `task lint` y `task test`, según el contrato del repositorio. Si existe
  evidencia de la misma revisión sin cambios de código posteriores, reutilizarla
  indicando su procedencia en vez de fingir una ejecución nueva.
- Si el proyecto ya incorpora OpenSpec, `task spec:validate`; si faltan sus
  dependencias, informar que se necesita `task spec:install`.
- `git diff --check` para detectar problemas de formato.

Para integración completa, MySQL debe estar disponible y migrado. Consultar
`docker compose ps`; arrancar con `task db:up` y migrar con `task migrate` solo
cuando preparar el entorno entre en el alcance autorizado. No borrar volúmenes
ni vaciar tablas. Distinguir los fallos de código de bloqueos de entorno.

Entregar comandos ejecutados, resultado, número de aprobados/fallidos/saltados,
y qué criterio sigue sin verificar. Un test saltado no equivale a aprobado.
No afirmar cobertura si no se midió. Registrar evidencia en `docs/ai-log.md`
cuando se está implementando la tarea; en una consulta de solo revisión,
proponer la entrada sin editar archivos. La skill no publica ni aprueba PRs.
