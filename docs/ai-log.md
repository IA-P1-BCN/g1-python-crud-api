# Bitácora de IA

Registro exigido por `docs/client/CLIENT_SPECS_V2_USER_MNG.md` (entregable 9):
herramienta y modelos usados, prompts clave, errores o alucinaciones del
agente y cómo se corrigieron, y decisiones tomadas (qué se aceptó, qué se
rechazó y por qué). Cada funcionalidad principal deja aquí su entrada.

## Formato de entrada

- **Fecha** — Tarea/PR — Herramienta y modelo — Qué se pidió (resumen) —
  Qué salió bien — Errores/alucinaciones y corrección — Decisión.

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

- [2026-10-14 — #22: filtros de listados, decisiones y validación](ai-log/2026-10-14-filtros.md).
