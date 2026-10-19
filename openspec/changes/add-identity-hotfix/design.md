# Design — hotfix de identidad

- **Una sola fuente de verdad**: `users` es la única tabla con nombre y
  email. `clientes` queda como perfil de negocio (estado, fecha). La
  respuesta de `/v1/clientes` AÑADE la identidad resuelta del user vinculado
  (`id_user`, `nombre`, `email`), pero no se almacena en clientes.
- **Backfill seguro en la migración**: cada cliente sin user vinculado
  recibe un user con su nombre/email (o sintético `cliente-{id}@demo.local`
  si es null o colisiona), hash aleatorio NO verificable (no puede iniciar
  sesión) y `activo=false`. Después se borran columnas y `uq_clientes_email`.
- **Persona en reservas**: join en lectura — el repositorio resuelve
  `users_for_clientes(ids)`; el caso de uso compone la respuesta con
  `id_user/nombre/email` (nulls si el cliente no tiene user). Sin cambios
  de permisos: staff ya ve las reservas de sus clases.
- **404s**: la whitelist `SPA_ROUTES` es la causa; se amplía con los
  segmentos nuevos en vez de cambiar a lista de exclusión (cambio mínimo y
  testeable).
- **Breaking**: contrato de `/v1/clientes` (input pierde nombre/email) y
  filtros (nombre/email/q fuera de ClienteQuery) → commits con `!`.
