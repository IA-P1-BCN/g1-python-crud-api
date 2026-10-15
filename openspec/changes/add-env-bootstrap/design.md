# Design — bootstrap de .env

- **Solo añade, nunca pisa**: los valores ya presentes y no vacíos del
  `.env` existente mandan; el bootstrap rellena huecos y corrige marcadores.
- **Secretos**: `SECRET_KEY` = `secrets.token_urlsafe(48)` si falta, está
  vacía o mide <32. `ADMIN_PASSWORD` = `secrets.token_urlsafe(16)` si falta,
  es marcador (`change-me`, `cambia-`, `replace-`, case-insensitive) o mide
  <12. Nunca se imprimen los valores, solo qué se rellenó.
- **Puerto**: sonda con bind en 127.0.0.1 (portable, sin lsof). Si el
  preferido está ocupado, prueba 3307..3316 y fija el primero libre como
  `MYSQL_PORT` con aviso en consola. Excepción: si el puerto lo ocupa
  nuestro propio contenedor `gym-mysql` (`docker ps`), no es conflicto —
  es la base de datos del proyecto y se reutiliza. docker-compose ya mapea
  `${MYSQL_PORT:-3306}` y settings lee el mismo valor, así que no hay más
  cambios.
- **Escritura**: se regenera el `.env` desde la plantilla `.env.example`
  (conserva comentarios y orden) sustituyendo valores; las claves extra del
  `.env` viejo se añaden al final.
