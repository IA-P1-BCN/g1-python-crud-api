# Decisiones
- Solo campos de perfil/credencial; no cambiar rol, activo o vínculo mediante edición general.
- PUT exige todos los campos de perfil; password tiene semántica de sustitución
  opcional explícita según #58. PATCH solo aplica campos enviados.
- Bloqueo de fila, validación de email duplicado y restricción UNIQUE definitiva.
- Política actual: JWT activo como #57. Permisos por rol y cambio de contraseña
  propia con contraseña actual siguen en #64–#66, sin cerrarlos aquí.
