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
task up                                    # desde la raíz: init + API + frontend
task docker:up                             # lo mismo, con API, frontend y seed en Docker
```

O por separado:

```bash
task db:up && task migrate && task seed   # desde la raíz
task dev                                   # API en 127.0.0.1:8000
npm start                                  # en frontend/
```

## Cuenta demo

Tras `task migrate` o al arrancar la API de Compose, existe la cuenta
`demo@gymflow.com` / `Demo56789012`. Es rol cliente, está activa y tiene ficha
de socio activa y un pago, así que puede iniciar sesión y reservar. En la base
solo está el hash. El admin del seed es otra cuenta.

## Integración con la API

- `app.config.ts` registra las implementaciones HTTP: `HttpAuthService`,
  `HttpClaseService` y `HttpReservaService`.
- `core/http/` contiene el interceptor de Bearer, la traducción de errores y la
  paginación. Un 401 de una petición protegida cierra la sesión local.
- `services/api/` expone un cliente CRUD por recurso (clientes, entrenadores, clases,
  reservas, pagos, cuentas y export CSV), aún sin pantallas.
- Los mocks (`core/auth/mock-auth.service.ts`, `services/mock/`) se usan solo en tests.
