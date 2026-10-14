# Bitácora de IA

Registro exigido por `docs/client/CLIENT_SPECS_V2_USER_MNG.md` (entregable 9):
herramienta y modelos usados, prompts clave, errores o alucinaciones del
agente y cómo se corrigieron, y decisiones tomadas (qué se aceptó, qué se
rechazó y por qué). Cada funcionalidad principal deja aquí su entrada.

## Formato de entrada

- **Fecha** — Tarea/PR — Herramienta y modelo — Qué se pidió (resumen) —
  Qué salió bien — Errores/alucinaciones y corrección — Decisión.

## Entradas

### 2026-10-14 — #62, inicialización de OpenSpec (STORY #49)

- **Herramienta/modelo:** Codex, GPT-6 (identificación del entorno).
- **Qué se pidió:** revisar las tareas de Fabiana y empezar por la entrega
  asistida por IA, priorizando OpenSpec según la indicación del PO.
- **Prompts clave:** «vamos con las mías»; «la story entrega asistida tiene
  que hacer primero». Se tradujeron en preparar #62 antes de modificar filtros.
- **Qué salió bien:** estructura `spec-driven`, contexto de GymFlow y comandos
  reproducibles. La CLI está fijada a 1.14.1; Node solo se utiliza para specs.
- **Errores y correcciones:** la copia local seguía en V1; se creó la rama desde
  `origin/main` y se corrigió el texto desactualizado del README. La primera
  instalación npm falló por DNS del sandbox; se repitió con el acceso autorizado.
  Docker estaba detenido y el sandbox impedía acceder a su socket/cache de uv;
  se obtuvo acceso y se ejecutó la integración real, sin ocultar skips.
- **Decisiones:** usar `openspec/specs/` como carpeta canónica; mantener la
  integración de cada agente opcional; no atribuir a la CLI comprobaciones de
  comportamiento que corresponden a tests y revisión humana. #63 continúa
  como registro transversal; #75 conserva la validación en CI.
- **Validación:** OpenSpec 1.14.1; instalación con `task spec:install` en una
  copia temporal limpia; `task spec:validate` aprobado. Una spec temporal sin
  escenarios fue rechazada correctamente. `task lint` aprobado; `task migrate`
  aplicado; `task test`: **101 aprobados, 0 saltados**, con MySQL 8.4.
- **Limitación:** `npm audit` informa de cuatro entradas altas correspondientes
  a la misma cadena de dependencias de desarrollo (`braces` → `micromatch` →
  `fast-glob` → OpenSpec), sin parche publicado para
  [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
  No se aplicó el downgrade incompatible sugerido por npm. El resultado se
  comunica en la PR; no se presenta la auditoría como aprobada.
- **Spec:** [init-openspec](../openspec/changes/init-openspec/proposal.md).

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
