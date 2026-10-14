# Decisiones
- Registro y login públicos son excepciones explícitas a la protección V2.
- `crear_cliente=false` por defecto; true crea perfil Inactivo nuevo. Sin tomar
  propiedad de perfiles existentes; email repetido produce 409.
- Repositorio propio con transacción atómica y errores de dominio.
- SecretStr de entrada no recorta contraseña; email en minúsculas.
- Errores de validación de auth/users omiten input/ctx para no reflejar secretos.
- PR depende de #95, revisión e integración en ese orden.
