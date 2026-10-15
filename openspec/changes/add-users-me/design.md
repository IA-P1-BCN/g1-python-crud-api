# Decisiones
- Revalidar activo en cada petición. 401 identifica fallo de autenticación;
  403 expresa acceso denegado a identidad autenticada inactiva (#23).
- Leer cuenta en una transacción que termina antes del controlador de negocio.
- /me se registra antes de futuros /{id}. El esquema OAuth2 ya lo genera FastAPI.
- Esta base no implementa todavía la política completa de roles (#64/#65).
