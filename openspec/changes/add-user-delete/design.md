# Decisiones
- Borrado físico dentro de transacción con bloqueo de fila.
- FK de users a clientes impide cascada hacia Cliente; no toca pagos/reservas.
- El propio token pierde validez práctica porque get_current_user relee la Cuenta.
- Soft delete es #73; admin-only es #65. No cerrar esas tareas con esta entrega.
