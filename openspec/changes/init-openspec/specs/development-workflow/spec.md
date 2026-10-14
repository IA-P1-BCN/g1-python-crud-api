## Purpose

Permitir que el equipo describa, valide y revise cada funcionalidad de GymFlow
antes de implementarla, conservando la trazabilidad del trabajo con IA.

## ADDED Requirements

### Requirement: Instalación reproducible de la herramienta
El equipo SHALL poder instalar y ejecutar la misma versión de la CLI desde
un clon del repositorio sin depender de una instalación global de OpenSpec.

#### Scenario: Preparación desde un clon
- **WHEN** una persona con Node.js compatible ejecuta `task spec:install`
- **THEN** se instalan las dependencias fijadas en el lockfile
- **AND** `task spec -- --version` devuelve la versión fijada por el proyecto

### Requirement: Especificación antes de implementación
Cada funcionalidad nueva SHALL contar con una propuesta vinculada a su issue,
requisitos y escenarios de aceptación antes de modificar su código.

#### Scenario: Inicio de una funcionalidad
- **WHEN** una tarea entra en desarrollo
- **THEN** se crea su cambio en `openspec/changes/`
- **AND** sus requisitos y escenarios quedan escritos antes de implementar
- **AND** el vocabulario coincide con `CONTEXT.md` y las convenciones de `AGENTS.md`

### Requirement: Validación local de contratos
El equipo SHALL poder validar las especificaciones y cambios sin interacción.
La validación debe fallar si un requisito carece de escenarios de aceptación.

#### Scenario: Especificaciones válidas
- **WHEN** se ejecuta `task spec:validate` con requisitos y escenarios válidos
- **THEN** el comando termina con código cero

#### Scenario: Requisito incompleto
- **WHEN** se valida un requisito que no contiene ningún escenario
- **THEN** el comando termina con código distinto de cero
- **AND** informa del requisito que debe corregirse

### Requirement: Evidencia y revisión de la entrega
Cada PR de funcionalidad SHALL enlazar su especificación, registrar el uso de IA
y los resultados reales de validación, y recibir revisión humana antes del merge.

#### Scenario: Preparación de una PR
- **WHEN** se propone integrar una funcionalidad
- **THEN** la PR enlaza la issue y la especificación
- **AND** la bitácora identifica herramienta, modelo, prompts y decisiones
- **AND** se distinguen tests aprobados, fallidos y saltados
- **AND** no se incluyen secretos en la evidencia
