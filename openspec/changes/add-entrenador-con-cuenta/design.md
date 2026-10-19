# Design — Entrenador con Cuenta

- **Una transacción**: `cuenta_repository.create_entrenador(...)` inserta
  `EntrenadorRecord` y `CuentaRecord` (rol `staff`, activa, vinculada por
  `id_entrenador`) en el mismo flush; el caso de uso envuelve en transacción
  y valida antes el email (`get_by_email` → 409 sin crear nada). Sigue el
  precedente de `create_cliente` en el mismo repositorio.
- **Contraseña inicial**: la demo común `Demo56789012` (documentada en el
  README), coherente con el seed. Un admin puede cambiarla después.
- **Contrato**: `POST /v1/entrenadores` acepta `email` opcional (solo alta;
  `PUT` lo rechaza con 422 por `extra=forbid`). `EntrenadorResponse` añade
  `id_user` y `email` resueltos de la Cuenta vinculada (null si no hay),
  igual que clientes y reservas resuelven identidad (ADR 0002).
- **Permisos**: escribir Entrenadores ya exige admin (`_check_operation`);
  la rama con email revalida rol admin en el caso de uso de Cuentas.
