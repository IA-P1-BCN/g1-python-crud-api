## 1. Especificación
- [x] Cambio `add-frontend-gestion` con propuesta, requisitos y escenarios (#31, #84, STORY #42).
- [ ] `task spec:validate` en verde antes del código.

## 2. Scaffolding
- [ ] Primitiva de tabla Spartan (`shared/ui/table` + paths en `tsconfig.json`).
- [ ] Helper de descarga de CSV en `shared/`.

## 3. Pantallas
- [ ] Clientes: listado con filtros, alta, edición y baja con confirmación.
- [ ] Entrenadores: CRUD con filtros de texto.
- [ ] Gestión de clases: CRUD con entrenador y horario UTC.
- [ ] Pagos: CRUD con filtros de cliente y método.
- [ ] Cuentas: listado con filtros, edición PUT y baja (requiere token).
- [ ] Perfil propio: `GET /v1/users/me` + `PATCH /v1/users/{id}` y sesión actualizada.
- [ ] Exportación CSV con descarga por tabla.
- [ ] Menú de sesión: grupo «Gestión» por rol y enlace «Mi perfil».

## 4. Tests
- [ ] Spec por pantalla con proveedores falsos de los `*Api`.
- [ ] Spec del menú con el grupo de gestión por rol.
- [ ] `npx tsc -p tsconfig.app.json --noEmit`, `npm test` y `npm run build` en verde.

## 5. Verificación
- [ ] `task lint`, `task spec:validate` y smoke contra la API en marcha (endpoints que usan las pantallas).
- [ ] Guards de ruta sin cambios (seguirán comentados).

## 6. Documentación y workflow
- [ ] Entrada en `docs/ai-log.md` con prompts, decisiones y lo no comprobado.
- [ ] `frontend/README.md` con las pantallas nuevas.
- [ ] Revisión humana; archivar con `task spec -- archive add-frontend-gestion --yes` tras el merge.
