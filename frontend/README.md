# GymFlow · frontend

Aplicación Angular 22 de GymFlow. Usa npm y es independiente del `package.json`
de OpenSpec de la raíz. Consume la API real (`/v1`) para autenticación, clases,
reservas y el resto de recursos.

## Requisitos

- Node.js 24 (o >= 22.12 compatible con Angular 22)
- La API en `http://127.0.0.1:8000` y MySQL (`task db:up && task migrate && task seed`)

## Comandos

```bash
npm ci              # instala dependencias exactas de package-lock.json
npm start           # servidor de desarrollo en http://127.0.0.1:4200
npm test            # tests unitarios (Vitest)
npm run build       # compilación de producción en dist/
```

En desarrollo, `npm start` reenvía `/v1` a `http://127.0.0.1:8000` mediante
`proxy.conf.json`, así que no hace falta CORS en la API.

## Arranque con datos

```bash
task db:up && task migrate && task seed   # desde la raíz
task dev                                   # API en 127.0.0.1:8000
npm start                                  # en frontend/
```

## Cuenta demo

`task seed` crea clientes ficticios, pero no cuentas con contraseña conocida. Para
probar el flujo completo, crea una cuenta demo por el registro público y actívala:

1. Regístrate en `/registro` con crear ficha de socio. Correo sugerido:
   `demo@example.com` (la API rechaza `.test`).
2. Activa la ficha y añade un pago con la API (`PUT /v1/clientes/{id_cliente}` con
   `estado_membresia: "Activo"` y `POST /v1/pagos`). Sin pago no se puede reservar.
3. Inicia sesión y reserva una clase.

Las credenciales no se versionan en el repositorio.

## Integración con la API

- `app.config.ts` registra las implementaciones HTTP: `HttpAuthService`,
  `HttpClaseService` y `HttpReservaService`.
- `core/http/` contiene el interceptor de Bearer, la traducción de errores y la
  paginación. Un 401 de una petición protegida cierra la sesión local.
- `services/api/` expone un cliente CRUD por recurso (clientes, entrenadores, clases,
  reservas, pagos, cuentas y export CSV), aún sin pantallas.
- Los mocks (`core/auth/mock-auth.service.ts`, `services/mock/`) se usan solo en tests.
