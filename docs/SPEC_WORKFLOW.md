# Especificaciones de GymFlow

La issue [#62](https://github.com/IA-P1-BCN/g1-python-crud-api/issues/62)
prepara el flujo de la STORY #49: definir qué debe hacer una funcionalidad
antes de pedir su implementación al agente. La API sigue usando uv;
Node.js >=20.19.0 solo es necesario para la CLI de OpenSpec.

## Preparación

Desde la raíz del repositorio:

```bash
task spec:install
task spec -- --version
task spec:validate
```

`spec:install` ejecuta `npm ci --ignore-scripts` con el lockfile versionado.
`spec` usa el binario local y desactiva la telemetría. No requiere instalar
OpenSpec globalmente. `spec:validate` equivale a
`openspec validate --all --strict --no-interactive`.

## Estructura

```text
openspec/
  config.yaml                         contexto y reglas de GymFlow
  specs/<capacidad>/spec.md            contratos vigentes
  changes/<cambio>/
    .openspec.yaml                    esquema del cambio
    proposal.md                      problema, alcance e issue
    specs/<capacidad>/spec.md         requisitos nuevos o modificados
    design.md                        decisiones técnicas
    tasks.md                         implementación y comprobaciones
  changes/archive/                   cambios revisados y archivados
```

`openspec/specs/` es la carpeta `specs/` solicitada por V2. Inicialmente está
vacía: el primer contrato se incorpora al archivar `init-openspec` después
de su revisión. La propuesta de esta entrega es un ejemplo real en
[`openspec/changes/init-openspec/`](../openspec/changes/init-openspec/).

## Una tarea, una rama, una PR

1. Leer la issue, los bloqueos, `AGENTS.md`, `CONTEXT.md` y las specs vigentes.
   Una tarea bloqueada no autoriza implementar las tareas de otra persona.
2. Crear una rama `feature/<tema>` desde la base actualizada.
3. Crear el cambio. Ejemplo para la futura #22, cuando se inicie esa tarea:

   ```bash
   task spec -- new change add-gym-filtering
   task spec -- instructions proposal --change add-gym-filtering
   task spec -- status --change add-gym-filtering
   ```

4. Escribir `proposal.md`; después, specs y decisiones de diseño; por último,
   `tasks.md`. Los comandos `instructions specs`, `instructions design` e
   `instructions tasks` ofrecen las plantillas y el contexto del proyecto.
5. Revisar criterios de aceptación y ejecutar `task spec:validate` antes del
   código. Corregir ambigüedades con el contexto de la issue o el PO.
6. Implementar el cambio y marcar las tareas solo cuando exista evidencia.
   `task spec -- instructions apply --change add-gym-filtering` muestra
   los archivos y tareas que debe leer el agente.
7. Ejecutar `task spec:validate`, `task lint` y `task test`. Para comprobar
   integración completa, ejecutar antes `task db:up` y `task migrate`.
   Informar tests saltados; no contarlos como aprobados.
8. Registrar el trabajo en `docs/ai-log.md`; abrir PR con `Closes #N`, enlace
   al cambio, decisiones relevantes y validación. Revisión humana antes del merge.
9. Tras revisar el cambio completo, ejecutar
   `task spec -- archive add-gym-filtering --yes`, validar de nuevo y revisar
   el contrato consolidado antes de integrar su archivo.

No archivar propuestas incompletas ni cerrar una STORY por completar solo una
de sus tareas. Las tareas simples de bitácora o tooling que indiquen expresamente
que no requieren un cambio OpenSpec siguen esa instrucción de su issue.

## Requisitos y escenarios

Las explicaciones se escriben en español. Los encabezados y palabras normativas
del formato se conservan en inglés. Ejemplo de un delta para una capacidad nueva:

```markdown
## Purpose

Permitir al staff localizar clientes por criterios de búsqueda observables.

## ADDED Requirements

### Requirement: Filtrado por estado de membresía
El listado SHALL devolver solo clientes del estado solicitado.

#### Scenario: Consulta de clientes activos
- **WHEN** se consulta el listado con el filtro `estado_membresia=Activo`
- **THEN** todos los resultados tienen ese estado
```

Usar `## MODIFIED Requirements` para cambiar un requisito existente,
copiando su bloque completo y todos sus escenarios. Incluir errores y límites
relevantes. El validador detecta problemas estructurales; los tests y la revisión
demuestran el cumplimiento de los escenarios.

## Integración opcional con agentes

La inicialización base usa `--tools none`. Para OpenCode:

```bash
task spec -- init --tools opencode
```

Después se puede usar `/opsx-propose` y `/opsx-apply` en OpenCode. Los nombres
de skills correspondientes son `openspec-propose` y `openspec-apply-change`.
`openspec-new-change` pertenece al flujo ampliado, activable con
`task spec -- config profile` y `task spec -- update`; ese perfil modifica
preferencias personales, por lo que no se configura automáticamente.
La alternativa de terminal `task spec -- new change <nombre>` siempre está
disponible. Los comandos de terminal tampoco dependen del modelo elegido.

Las integraciones generadas son locales. Los comandos propios del equipo se
versionan por separado en #79.

Referencia oficial de la CLI fijada:
[OpenSpec v1.14.1](https://github.com/Fission-AI/OpenSpec/blob/v1.14.1/docs/cli.md).
