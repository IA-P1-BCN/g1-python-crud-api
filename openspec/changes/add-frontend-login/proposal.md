## Why

La issue #83 (UI web de registro y login) forma parte de la STORY #42 "Portal web
del socio" y es la primera tarea del frontend. La API de `main` no expone
`/v1/auth/*` ni JWT: la issue #55 aparece cerrada en GitHub, pero su código no
está en `main`. Para avanzar en la interfaz sin bloquearse, el login se construye
contra una interfaz estable de autenticación con una implementación de mock.

## What Changes

- Crear `frontend/`, una aplicación Angular 22 independiente con npm, dentro del
  mismo repositorio.
- Añadir una pantalla de login (`/login`) con validación de formulario y estados de
  carga, error de credenciales y éxito.
- Definir `AuthService` como interfaz y una implementación `MockAuthService` con
  usuarios de prueba. La implementación real se sustituirá cuando #55 esté en `main`.
- Configurar el proxy de desarrollo de Angular para `/v1` hacia `127.0.0.1:8000`,
  sin modificar el backend.
- Documentar la nueva carpeta en `AGENTS.md` y el uso en `frontend/README.md`.

## Alcance excluido

- Registro de usuarios: se trata en una tarea posterior de #83; esta PR no lo
  implementa.
- Guardas de ruta por rol y panel de administración (#84, #65).
- Cambios en la API FastAPI, incluido CORS: el proxy evita la necesidad.
- Dockerfile y servicio en `docker-compose.yml`: se coordinan con la persona de
  deploy en una tarea aparte.

## Capabilities

### New Capabilities

- `frontend-login`: pantalla de inicio de sesión de la interfaz web contra una
  interfaz de autenticación con mock.

### Modified Capabilities

Ninguna. No cambia ningún requisito vigente de la API.

## Impact

- Nueva carpeta `frontend/` con su propio `package.json` y `package-lock.json`.
- `AGENTS.md`: npm deja de ser solo para OpenSpec y pasa a cubrir `frontend/`.
- `.gitignore`: se ignoran `frontend/.angular/` y `frontend/dist/`.
- Sin migraciones ni cambios en la base de datos.
- La PR referencia #83 y #42 con `Refs`, no `Closes`, porque el registro y la
  autenticación real siguen pendientes.
