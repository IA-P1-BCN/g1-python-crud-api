# Bitácora de IA

Registro exigido por `docs/client/CLIENT_SPECS_V2_USER_MNG.md` (entregable 9):
herramienta y modelos usados, prompts clave, errores o alucinaciones del
agente y cómo se corrigieron, y decisiones tomadas (qué se aceptó, qué se
rechazó y por qué). Cada funcionalidad principal deja aquí su entrada.

## Formato de entrada

- **Fecha** — Tarea/PR — Herramienta y modelo — Qué se pidió (resumen) —
  Qué salió bien — Errores/alucinaciones y corrección — Decisión.

## Cómo mantenerla (#63)

Cada funcionalidad principal añade una entrada durante su desarrollo y la
enlaza desde la PR. Todas las personas del equipo registran su trabajo; la
responsable de #63 comprueba la continuidad de la bitácora durante la entrega.
Se incluyen también los cambios de tooling con decisiones relevantes.

Usar esta plantilla y sustituir los campos con hechos de la sesión:

```markdown
### AAAA-MM-DD — #issue — Nombre del cambio

- **PR/spec:** enlaces, o motivo por el que la issue no requiere spec.
- **Herramienta/modelo:** identificación real; si no está disponible, indicarlo.
- **Qué se pidió y prompts clave:** resumen fiel de las instrucciones relevantes.
- **Qué salió bien:** resultado observado.
- **Errores y corrección:** fallo real y cómo se resolvió; si no hubo, indicarlo.
- **Decisiones:** qué se aceptó, qué se rechazó y por qué.
- **Validación:** comandos y resultados reales; separar fallos y skips.
- **Pendiente:** revisión, bloqueos o limitaciones que siguen abiertos.
```

No copiar `.env`, tokens, contraseñas ni datos personales del gimnasio. Resumir
los prompts que contengan información sensible. No inventar modelos, errores,
resultados o revisiones: si no se comprobó algo, se indica expresamente.

La [plantilla de PR](../.github/pull_request_template.md) recuerda enlazar esta
entrada, la issue y la spec, y comprobar evidencia y revisión humana. Esta
checklist es una ayuda de revisión; no es una barrera automática de CI.
La bitácora sigue viva hasta completar las funcionalidades del proyecto.

## Entradas

- **2026-10-14** — Migración del plan V2 (gestión de usuarios) al alcance de
  este repo. Agente: ZCode (GLM). Se pidió leer el plan del proyecto
  `g1_user_management_api` (30 historias + 72 tareas; sin mirar su código ni
  sus docs) y adaptarlo a los milestones abiertos: V2-Esencial → #2 Nivel
  medio, V2-Medio+Avanzado → #3 Nivel Avanzado, V2-Experto → #4 Nivel
  Experto. Adaptaciones aceptadas: roles `admin/user` → `admin/staff/cliente`
  (la STORY #38 ya los prometía); tareas que este repo ya cubre (uv/Taskfile,
  /health, capas, Alembic, Swagger base) se omiten con nota en la STORY;
  tareas de tests fusionadas en su tarea de feature (convención del repo).
  Decisión de diseño: Cuenta (`users`) separada de Cliente con vínculo 1:1
  (ADR 0001). Prioridades P1/P2/P3 y bloqueos (#refs) añadidos a cada tarea.

### 2026-10-14 — #63 — Continuidad de la bitácora

- **Herramienta/modelo:** Codex, GPT-6 (identificación del entorno).
- **Qué se pidió y prompts clave:** completar las tareas de Fabiana,
  priorizando la STORY #49 según el PO, y dejar un resumen breve para el equipo.
- **Qué salió bien:** se define una plantilla de entradas y se incorpora su
  enlace a la checklist de cada PR de funcionalidad.
- **Errores y corrección:** no se detectaron errores funcionales en este cambio
  documental. Se distingue la comprobación humana de una barrera automática.
- **Decisiones:** mantener una bitácora compartida; cada autor aporta la
  evidencia de su funcionalidad. No cerrar #63 al crear la plantilla porque su
  alcance exige continuar el registro durante las siguientes entregas.
- **Validación:** revisión de enlaces y `git diff --check`. El código Python
  coincide con la base validada durante #62: 101 tests aprobados con MySQL,
  sin skips; este cambio no introduce lógica ejecutable.
- **Spec:** la issue #63 indica expresamente que no requiere carpeta de cambio.
- **Pendiente:** continuar las entradas por funcionalidad y revisión humana.
