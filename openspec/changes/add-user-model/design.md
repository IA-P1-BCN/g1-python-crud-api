# Decisiones
- `Cuenta` dataclass; `PasswordHasher` Protocol y adaptador pwdlib/Argon2.
- `users.id_cliente` UNIQUE nullable, FK RESTRICT: preserva el historial del socio.
- Email normalizado en minúsculas; rol mínimo permite admin del seed (#53).
  Las políticas de roles completas siguen en #64/#65, sin cerrar esas tareas.
- SECRET_KEY opcional hasta #55; ADMIN_PASSWORD obligatoria en el punto de uso
  (seed), no en procesos de lectura/migración que no crean administradores.
- Clientes sin email: no inventar identidad; informar conteos. Las cuentas de
  clientes empiezan inactivas sin credencial común, pendientes de activación.
- ADMIN_EMAIL configurable; una cuenta previa con ese email que no sea admin
  causa conflicto, nunca elevación de privilegios.
- Referencia: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
