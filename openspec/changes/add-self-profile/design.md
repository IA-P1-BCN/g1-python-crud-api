Registrar /me antes de /{id}. Schema CuentaSelfPatch extiende la validación
existente con current_password SecretStr; secretos literales y errores sin input.
Caso de uso con bloqueo de la Cuenta: verificar el hash actual y actualizar
perfil/contraseña en la misma transacción. Reutilizar el núcleo de edición.
Separar edición propia de edición administrativa evita cambiar contraseña
usando el endpoint por ID sin demostrar conocimiento de la actual.
