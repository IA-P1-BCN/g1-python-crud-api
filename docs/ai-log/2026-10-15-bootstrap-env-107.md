# Bootstrap de .env — #107

- Herramienta: ZCode (GLM).
- Prompt: tarea de utilidad para que `task demo` prepare `.env` solo (copiar
  `.env.example` y rellenar todo lo necesario: SECRET_KEY, ADMIN_PASSWORD) y
  sugerir otro puerto MySQL si 3306 está ocupado; con spec openspec previa.
- Spec previa: add-env-bootstrap; issue #107 (P1, STORY #93).
- Decisión/alcance: script idempotente que solo rellena (nunca pisa valores
  no vacíos), regenera `.env` desde la plantilla conservando claves extra, y
  sustituye marcadores de ADMIN_PASSWORD en cualquier capitalización. Sonda
  de puerto por bind en 127.0.0.1 con excepción explícita: si el puerto lo
  ocupa el propio contenedor `gym-mysql`, se reutiliza (no es conflicto).
  Tarea `task env` nueva; `task demo` la usa en lugar del `cp` condicional.
- Errores corregidos: un test propio detectó que las claves extra del
  `.env` viejo se perdían (`extra` siempre vacío); corregido en `main`.
- Verificación: `task test` **208 aprobados** (7 nuevos del bootstrap),
  `task lint` y `task spec:validate` (12/12) correctos; `task demo` completo
  de principio a fin en un entorno con `.env` heredado de V1 sin SECRET_KEY.
- Revisión: la evidencia automatizada no sustituye la revisión humana de la
  PR; vigilar que el bootstrap no imprima secretos y que `docker ps` solo se
  use para identificar el contenedor propio.
