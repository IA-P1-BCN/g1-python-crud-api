# CRUD de usuarios con autenticación JWT

La issue #10 implementa la gestión de usuarios definida en
[la especificación V2](../docs/client/CLIENT_SPECS_V2_USER_MNG.md).
La usuaria confirmó el 6 de octubre de 2026 que esta V2 sustituye a GymFlow.
La arquitectura por capas, MySQL, Alembic y el prefijo `/v1` se mantienen.

## Entidades y permisos

`User` contiene `id`, `name`, `email` único normalizado a minúsculas,
`password_hash`, `created_at` en UTC e `is_active`. Se añade `role`
(`user` o `admin`) para limitar la administración del directorio, según el
nivel medio de la V2. `token_version` es interno y permite invalidar sesiones
al cambiar la contraseña. Ni el hash ni esta versión aparecen en respuestas.

El registro público y la creación HTTP siempre generan usuarios con rol `user`.
Solo el comando local de datos de demostración crea el administrador de prueba.
Un usuario puede consultar, modificar o borrar su propio perfil; un
administrador puede hacerlo sobre cualquier usuario. Listar y crear usuarios
desde el directorio requiere rol `admin`. Las cuentas inactivas no pueden
iniciar sesión ni usar tokens emitidos anteriormente.

## Contrato HTTP

| Método | Ruta | Acceso y resultado |
|---|---|---|
| POST | `/v1/auth/register` | Público; registra usuario activo, 201 |
| POST | `/v1/auth/login` | Público; formulario OAuth2 con email en `username`, devuelve JWT, 200 |
| GET | `/v1/users/me` | Token válido; perfil propio, 200 |
| POST | `/v1/users` | Admin; crea usuario, 201 |
| GET | `/v1/users` | Admin; lista ordenada por ID con `offset` y `limit`, 200 |
| GET | `/v1/users/{user_id}` | Propietario o admin; consulta, 200 |
| PUT | `/v1/users/{user_id}` | Propietario o admin; reemplaza nombre, email y estado, 200 |
| DELETE | `/v1/users/{user_id}` | Propietario o admin; borra, 204 sin cuerpo |

La entrada de registro/creación es `name`, `email`, `password`.
PUT exige `name`, `email`, `is_active`; `password` es opcional y, si se
incluye, sustituye la contraseña e invalida tokens anteriores. No acepta
`role`, `id`, `password_hash`, `created_at` ni `token_version`.

Los errores usan `detail`: 401 para credenciales/token inválidos o cuenta
inactiva, 403 para permisos insuficientes, 404 para un usuario inexistente
consultado por un administrador, 409 para email duplicado, 422 para datos
inválidos y 503 para fallo de conexión a MySQL. Un usuario normal recibe 403
al acceder a otro ID, exista o no. El login devuelve el mismo 401 si la
cuenta no existe, está inactiva o la contraseña es incorrecta.

## Seguridad

- Hash Argon2 mediante `pwdlib`; JWT firmado con PyJWT y algoritmo HS256 fijo.
  Se sigue la [guía oficial de FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).
- Clave de firma aleatoria de al menos 32 caracteres, cargada desde `.env`;
  no se guarda en Git. Expiración configurable, por defecto 30 minutos.
- El token requiere sujeto, emisión, expiración y versión de credenciales.
  Cada petición verifica que la cuenta sigue existiendo y activa.
- Contraseñas de 12 a 128 caracteres; no se recortan espacios ni se guardan
  contraseñas o tokens en logs. Los errores de validación no reflejan secretos.
- Swagger muestra **Authorize** mediante OAuth2 Password Flow.

## Persistencia y datos de demostración

Alembic crea `users`, sus restricciones y la versión de esquema `0.2`.
El comando `task seed` crea cuentas de demostración de forma repetible,
sin sobrescribir cuentas existentes. Las contraseñas son aleatorias y se
guardan solo en un archivo local ignorado por Git, con permisos restringidos.
El esquema no mezcla tablas del gimnasio con el nuevo servicio de usuarios.

## Criterios de aceptación

1. Registro, login y todas las operaciones CRUD funcionan sobre MySQL migrado.
2. Email duplicado produce 409 en creación y actualización; una operación
   fallida no deja cambios parciales.
3. Faltan credenciales, JWT alterado/caducado, cuenta borrada/inactiva o
   contraseña cambiada: acceso denegado con 401.
4. Un usuario no administra perfiles ajenos ni puede elevar su propio rol.
5. Las respuestas y errores nunca incluyen contraseñas ni hashes; OpenAPI
   marca la contraseña como campo de solo escritura y omite los campos internos.
6. Los tests unitarios cubren los endpoints y permisos; los de integración
   arrancan uvicorn y hacen HTTP real contra MySQL. Lint y tests pasan.
7. README, colección de peticiones, spec y bitácora permiten reproducir la demo.

Refresh tokens, recuperación de contraseña, verificación de email, CSV,
websockets, frontend y despliegue quedan fuera de esta issue.
