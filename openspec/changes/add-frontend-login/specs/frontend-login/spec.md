## ADDED Requirements

### Requirement: Formulario de inicio de sesión
La aplicación SHALL mostrar en `/login` un formulario con correo electrónico y
contraseña. El botón de envío MUST estar deshabilitado mientras la petición está en
curso.

#### Scenario: Campos obligatorios vacíos
- **WHEN** el usuario envía el formulario sin correo o sin contraseña
- **THEN** no se llama a `AuthService` y se muestran los mensajes de campo obligatorio

#### Scenario: Correo con formato inválido
- **WHEN** el usuario introduce un correo sin formato válido
- **THEN** se muestra un mensaje de formato de correo y no se envía la petición

#### Scenario: Envío en curso
- **WHEN** la petición de login está pendiente
- **THEN** el botón está deshabilitado y se indica que se está validando

### Requirement: Autenticación contra interfaz
La aplicación SHALL autenticar a través de la interfaz `AuthService`. Los componentes
MUST NOT conocer la implementación concreta. Por defecto se usa `MockAuthService`.

#### Scenario: Credenciales válidas del mock
- **WHEN** el usuario envía un correo y contraseña que coinciden con un usuario de prueba
- **THEN** `AuthService` devuelve el usuario autenticado y la aplicación navega a `/`

#### Scenario: Credenciales incorrectas
- **WHEN** el usuario envía credenciales que no coinciden con ningún usuario de prueba
- **THEN** se muestra "Correo o contraseña incorrectos" y el usuario permanece en `/login`

#### Scenario: Sustitución de la implementación
- **WHEN** se cambia el proveedor de `AuthService` a una implementación HTTP
- **THEN** la pantalla de login funciona sin modificar sus componentes

### Requirement: Error de conexión
La aplicación SHALL distinguir un fallo de red o de servidor de unas credenciales
incorrectas, y SHALL mostrar un mensaje genérico sin detalles técnicos.

#### Scenario: Fallo de red
- **WHEN** la llamada a `AuthService` falla por error de conexión
- **THEN** se muestra "No se pudo conectar con el servidor. Inténtalo de nuevo." y el formulario conserva los datos introducidos

### Requirement: Acceso a la API en desarrollo
En desarrollo, las peticiones a `/v1` SHALL salir del mismo origen de la aplicación y
reenviarse a `http://127.0.0.1:8000` mediante el proxy de Angular, sin modificar el
backend.

#### Scenario: Petición a la API con proxy activo
- **WHEN** la aplicación ejecuta `npm start` y realiza una petición a `/v1/health`
- **THEN** la petición se reenvía a `http://127.0.0.1:8000/v1/health`
