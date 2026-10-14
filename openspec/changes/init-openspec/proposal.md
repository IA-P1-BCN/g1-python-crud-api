## Why

La STORY #49 exige especificar cada funcionalidad antes de implementarla.
La issue #62 prepara ese flujo para el equipo y desbloquea la validación
en CI de #75. El repositorio todavía no contiene una estructura OpenSpec.

## What Changes

- Inicializar OpenSpec con contexto y convenciones de GymFlow.
- Fijar la versión de la CLI y sus dependencias para reproducir la instalación.
- Exponer instalación, ejecución y validación local mediante Taskfile.
- Documentar cómo crear una propuesta, especificarla, implementarla y revisarla.
- Registrar este trabajo en la bitácora exigida por #63.

## Capabilities

### New Capabilities

- `development-workflow`: preparación y validación de especificaciones antes
  de implementar funcionalidades, con trazabilidad de IA y revisión humana.

### Modified Capabilities

Ninguna.

## Impact

Herramientas y documentación del equipo. Node.js solo se utiliza para la CLI
de OpenSpec; las dependencias y ejecución de la API continúan con uv.
La validación en CI pertenece a #75. Los automatismos propios del agente
pertenecen a #79 y #85. No cambia ningún endpoint ni la base de datos.
