# GymFlow · frontend

Aplicación Angular 22 de la pantalla de inicio de sesión (#83, STORY #42). Usa npm
y es independiente del `package.json` de OpenSpec de la raíz.

## Requisitos

- Node.js 24 (o >= 22.12 compatible con Angular 22)
- La API en `http://127.0.0.1:8000` y MySQL para las pantallas que consulten datos

## Comandos

```bash
npm ci              # instala dependencias exactas de package-lock.json
npm start           # servidor de desarrollo en http://127.0.0.1:4200
npm test            # tests unitarios (Vitest)
npm run build       # compilación de producción en dist/
```

En desarrollo, `npm start` reenvía `/v1` a `http://127.0.0.1:8000` mediante
`proxy.conf.json`, así que no hace falta CORS en la API.

## Autenticación de prueba

La pantalla usa `MockAuthService` (`src/app/core/auth/mock-auth.service.ts`), con
usuarios ficticios solo para desarrollo:

| Correo              | Contraseña   | Rol     |
|---------------------|--------------|---------|
| cliente@gym.test    | cliente123   | cliente |
| staff@gym.test      | staff123     | staff   |

`sin-red@gym.test` simula un fallo de conexión. Estos datos se sustituirán cuando
#55 (login JWT) esté disponible en `main`; el cambio afecta solo a
`app.config.ts`.
