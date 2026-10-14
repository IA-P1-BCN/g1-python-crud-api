## Why

La issue #22 (STORY #37) necesita localizar registros por campos del gimnasio.
Los GET actuales solo permiten paginar; cada consulta obliga a recorrer listados.

## What Changes

- Añadir filtros específicos en los cinco listados, combinables con offset/limit.
- Buscar texto literal por fragmentos sin distinguir mayúsculas y ofrecer `q`
  en clientes, entrenadores y clases.
- Filtrar por relaciones, estado/asistencia/método y rangos inclusivos de fechas.
- Validar tipos con 422 y rechazar intervalos invertidos con 400 documentado
  (avance parcial de #23; 401/403 siguen ligados a autenticación).
- Mantener CSV completo y los contratos de escritura existentes.

## Capabilities

### New Capabilities

- `gym-listing`: búsqueda y filtrado de listados del gimnasio antes de paginar.

### Modified Capabilities

Ninguna.

## Impact

Schemas y rutas GET, controladores, caso de uso y puerto/repositorio de listados.
No hay migración. #61 aplica a cuentas y continúa bloqueada por #57; no se crean
endpoints `/v1/users` en esta tarea. El tooling de OpenSpec se entrega en PR #89.
