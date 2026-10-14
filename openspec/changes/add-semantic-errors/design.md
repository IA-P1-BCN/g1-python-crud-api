# Decisiones
- Reutilizar handlers de #22/#55/#56. No inventar un 403 por rol antes de #65.
- 403 real: Cuenta desactivada después del login; 401: sin token válido o Cuenta borrada.
- hide_input_in_errors de Settings evita que trazas de validación muestren valores.
- Pruebas de handlers separadas de pruebas HTTP/MySQL ya entregadas.
