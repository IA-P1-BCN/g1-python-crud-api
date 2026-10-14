## Decisions

- Usar schemas de query Pydantic en interfaces y convertirlos en un filtro
  dataclass de dominio; ninguna capa interna importa Pydantic.
- Aplicar predicados parametrizados con SQLAlchemy antes de OFFSET/LIMIT.
  Escapar comodines de LIKE y agrupar los campos de `q` con OR.
- Campos por entidad: clientes `nombre`, `email`, `estado_membresia`,
  `fecha_inscripcion_desde/hasta`; entrenadores `nombre`, `especialidad`,
  `telefono`; clases `nombre_clase`, `id_entrenador`, `horario_desde/hasta`;
  reservas `id_cliente`, `id_clase`, `asistio`, `fecha_reserva_desde/hasta`;
  pagos `id_cliente`, `metodo_pago`, `fecha_pago_desde/hasta`.
- El caso de uso comprueba la coherencia del intervalo; el adaptador HTTP
  traduce el error de dominio a 400 solo documentado en listados. La validación
  de tipos sigue siendo 422. No inventar respuestas 401/403 antes de auth.
- No cambiar `list_all` ni la exportación CSV acordada en #18: exporta la tabla
  completa. Una exportación filtrada requerirá definir su contrato con el equipo.

## Validation

Tests HTTP con MySQL que comprueban los cinco listados, combinaciones, fechas,
valores falsos, nulos, comodines literales, paginación después de filtrar y
entradas inválidas. Tests de contrato OpenAPI y la suite de regresión existente.
