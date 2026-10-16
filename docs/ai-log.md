# Bitácora de IA

Registro exigido por `docs/client/CLIENT_SPECS_V2_USER_MNG.md` (entregable 9):
herramienta y modelos usados, prompts clave, errores o alucinaciones del
agente y cómo se corrigieron, y decisiones tomadas (qué se aceptó, qué se
rechazó y por qué). Cada funcionalidad principal deja aquí su entrada.

## Registros detallados

- [2026-10-14 — #79: uso de las skills de verificación y revisión](ai-log/2026-10-14-skills.md).

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
La preparación de este proceso queda registrada en
[la entrada de #63](ai-log/2026-10-14-bitacora.md).

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

- [2026-10-14 — #22: filtros de listados, decisiones y validación](ai-log/2026-10-14-filtros.md).

- [2026-10-14 — Cuentas #53](ai-log/2026-10-14-cuentas-53.md)

- [2026-10-14 — Registro #54](ai-log/2026-10-14-registro-54.md)

- [2026-10-14 — Login #55](ai-log/2026-10-14-login-55.md)

- [2026-10-14 — Perfil autenticado #56](ai-log/2026-10-14-perfil-56.md)

- [2026-10-14 — Consulta de Cuentas #57](ai-log/2026-10-14-listado-cuentas-57.md)

- [2026-10-14 — Edición de Cuentas #58](ai-log/2026-10-14-editar-cuentas-58.md)

- [2026-10-14 — Baja de Cuentas #59](ai-log/2026-10-14-borrar-cuentas-59.md)

- [2026-10-14 — Filtros de Cuentas #61](ai-log/2026-10-14-filtros-cuentas-61.md)

- [2026-10-14 — Errores semánticos #23](ai-log/2026-10-14-errores-semanticos-23.md)

- [2026-10-14 — Swagger de Cuentas #60](ai-log/2026-10-14-swagger-cuentas-60.md)

- [2026-10-15 — Bootstrap de .env #107](ai-log/2026-10-15-bootstrap-env-107.md)

- [2026-10-16 — Contenedorización API+frontend y cuenta demo #28](ai-log/2026-10-16-docker-compose-demo-28.md)
- [2026-10-15 — Integración frontend con la API](ai-log/2026-10-15-frontend-api.md)
