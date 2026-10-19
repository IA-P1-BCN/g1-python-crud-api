## ADDED Requirements

### Requirement: Cuenta admin demo pública
El seed SHALL crear admin.demo@gymflow.com con contraseña pública
AdminDemo56789012, rol admin, activa y sin vínculos Cliente/Entrenador.
SHALL almacenar solo un hash Argon2id y documentar el acceso en README.

#### Scenario: Primer seed
- **WHEN** el email demo no pertenece a ninguna Cuenta ni Cliente
- **THEN** se crea el admin demo y puede iniciar sesión y listar Cuentas

### Requirement: Preservación de identidades
El seed SHALL conservar el admin privado y todas las Cuentas existentes.
Si el email demo está ocupado por Cuenta o Cliente SHALL omitir el alta, sin
asignar privilegios, cambiar contraseña, activar ni vincular identidades.

#### Scenario: Repetir el seed
- **WHEN** la Cuenta demo ya existe
- **THEN** no se duplica ni se modifica su hash, rol, activo o vínculos

#### Scenario: Email en conflicto
- **WHEN** el email demo pertenece a otra Cuenta o Cliente
- **THEN** se omite la creación sin modificar el registro existente

### Requirement: Ejecución en Render
El entrypoint SHALL ejecutar el mismo seed antes de arrancar la API.

#### Scenario: Arranque tras integrar el cambio
- **WHEN** Render despliega main con la configuración de MySQL y ADMIN_PASSWORD
- **THEN** el seed intenta crear la Cuenta demo en la base externa
