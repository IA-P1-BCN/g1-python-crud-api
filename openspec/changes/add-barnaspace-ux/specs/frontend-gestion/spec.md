## MODIFIED Requirements

### Requirement: Navegación de gestión por rol
La aplicación SHALL mostrar en el menú de sesión un enlace a la administración
visible únicamente con rol `admin`, y un enlace al panel visible con rol
`staff` o `admin`. Las pantallas de gestión se sirven bajo `/admin/**`
(clientes, entrenadores, clases, pagos, cuentas, export) protegidas con
`adminGuard`; las rutas antiguas en la raíz redirigen a la nueva ubicación.
Este requisito sustituye la decisión del alcance anterior de mantener las
guardas desactivadas: las guardas se activan en este cambio.

#### Scenario: Rol cliente
- **WHEN** la sesión tiene rol `cliente`
- **THEN** el menú muestra catálogo, mis reservas y perfil, sin enlaces de gestión

#### Scenario: Rol staff
- **WHEN** la sesión tiene rol `staff`
- **THEN** el menú muestra «Mi panel» (`/staff`) y no los enlaces de `/admin`

#### Scenario: Rol admin
- **WHEN** la sesión tiene rol `admin`
- **THEN** el menú muestra «Admin» con acceso a `/admin/dashboard` y a las pantallas de gestión

#### Scenario: Sin sesión
- **WHEN** no hay sesión
- **THEN** el menú solo ofrece iniciar sesión y crear cuenta
