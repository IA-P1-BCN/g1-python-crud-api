## Why
#107: desde que SECRET_KEY es obligatoria (#95), `task demo` revienta en
`migrate` si el `.env` es viejo o viene de copiar `.env.example` (que trae
`SECRET_KEY=` vacía). Además, un puerto 3306 ocupado (otro MySQL o un túnel
SSH) hace fallar el arranque sin guía.

## What Changes
Un bootstrap idempotente de `.env` (`task env`, usado por `task demo`):
copia el example si falta, rellena SECRET_KEY y ADMIN_PASSWORD solo cuando
faltan o son marcadores, y elige el primer puerto MySQL libre si el
preferido está ocupado.

## Capabilities
### New Capabilities
- `env-bootstrap`: preparación automática y segura del entorno local.
### Modified Capabilities
Ninguna.

## Impact
Taskfile (tareas env/demo), scripts/bootstrap_env.py nuevo,
.env.example (comentario), tests unitarios.
