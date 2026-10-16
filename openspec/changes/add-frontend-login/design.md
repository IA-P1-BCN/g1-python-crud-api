## Decisions

- **Carpeta independiente.** `frontend/` contiene su propio `package.json` y
  `package-lock.json`, generados por Angular CLI 22 con npm. La raíz sigue con npm
  solo para OpenSpec.
- **Interfaz de autenticación.** `AuthService` define `login(email, password)` y
  devuelve un usuario. `MockAuthService` implementa la interfaz con usuarios de
  prueba en memoria. La selección de implementación se hace en `app.config.ts`
  mediante un token de inyección, de modo que sustituirla no toca componentes.
- **Errores tipados.** `AuthService` lanza `InvalidCredentialsError` para
  credenciales incorrectas y `NetworkError` para fallos de conexión. El componente
  traduce cada error a su mensaje; no compara cadenas.
- **Formularios reactivos.** Validadores de Angular para campos obligatorios y
  formato de correo. Sin lógica de validación en el template.
- **Estilos.** Tailwind CSS 4 y Spartan UI, instalados en una tarea posterior al
  scaffolding. Mientras tanto, la pantalla usa CSS sencillo para validar la
  estructura.
- **Proxy de desarrollo.** `frontend/proxy.conf.json` reenvía `/v1` a
  `http://127.0.0.1:8000`. Así no hace falta CORS en FastAPI.
- **Sin tokens reales.** `MockAuthService` no guarda tokens. La sesión en memoria
  se considera provisional y se reemplazará con JWT en #55.
- **Sin contrato OpenAPI.** La API no versiona un contrato. El frontend no genera
  tipos a partir de la API en esta tarea; los modelos del mock se escriben a mano y
  se revisarán cuando exista `/v1/auth/*`.

## Alternatives considered

- **Repositorio separado.** Descartado: el equipo de backend y la persona de deploy
  trabajan en el mismo repo y el cambio de contrato sería doble.
- **CORS en FastAPI.** Descartado para esta PR: obliga a decidir orígenes permitidos
  y toca el backend, que no es responsabilidad de esta tarea.

## Risks

- El mock puede diferir de la API real. Mitigación: el contrato de `AuthService` es
  el único punto de acoplamiento y se cubre con tests del componente.
- Dos gestores de paquetes en el repo (npm en raíz y en `frontend/`) son aceptados
  porque ambos usan npm. Esto evita conflictos de lockfiles.
