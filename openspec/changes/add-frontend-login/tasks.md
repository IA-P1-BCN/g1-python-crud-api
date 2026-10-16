## 1. Especificación

- [x] 1.1 Escribir proposal, specs, design y tasks, y validarlos con `task spec:validate`.
- [ ] 1.2 Revisión humana del cambio antes de escribir código.

## 2. Scaffolding

- [x] 2.1 Generar `frontend/` con `npx @angular/cli@22 new frontend --package-manager npm --skip-git --routing --style css`.
- [x] 2.2 Comprobar `npm run build` y `npm test` dentro de `frontend/`.
- [x] 2.3 Añadir `frontend/.angular/` y `frontend/dist/` a `.gitignore`.
- [x] 2.4 Añadir `frontend/proxy.conf.json` y conectarlo en `angular.json`.

## 3. Autenticación con mock

- [x] 3.1 Definir `AuthService`, `InvalidCredentialsError` y `NetworkError`.
- [x] 3.2 Implementar `MockAuthService` con usuarios de prueba y el token de inyección.
- [x] 3.3 Tests unitarios del mock: credenciales válidas, incorrectas y fallo de red.

## 4. Pantalla de login

- [x] 4.1 Componente `/login` con formulario reactivo y validadores.
- [x] 4.2 Estados: enviando, error de credenciales, error de conexión y éxito con navegación a `/`.
- [x] 4.3 Tests del componente cubriendo cada escenario de la spec.

## 5. Documentación y verificación

- [x] 5.1 `frontend/README.md` con cómo instalar, arrancar y probar.
- [x] 5.2 Actualizar `AGENTS.md`: `frontend/` como carpeta raíz y npm para frontend.
- [x] 5.3 Entrada en `docs/ai-log/` con prompts, errores, decisiones y el commit de la skill de Spartan cuando se instale.
- [x] 5.4 Ejecutar `task spec:validate`, `task lint`, `task test` y `npm test` en `frontend/`, e informar de los resultados sin inventarlos.

## Workflow follow-up

- Revisión humana, integración en `main` por PR y archivo de la especificación.
