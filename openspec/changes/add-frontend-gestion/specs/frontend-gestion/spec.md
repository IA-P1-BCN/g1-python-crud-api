## ADDED Requirements

### Requirement: Navegación de gestión por rol
La aplicación SHALL mostrar en el menú de sesión un grupo «Gestión» con enlaces a
clientes, entrenadores, clases, pagos, cuentas y exportación, visible únicamente
cuando el rol de la sesión es `admin` o `staff`, y un enlace «Mi perfil» para
cualquier sesión autenticada. Las guardas de ruta MUST permanecer desactivadas en
este alcance.

#### Scenario: Rol cliente
- **WHEN** la sesión tiene rol `cliente`
- **THEN** el menú muestra «Mi perfil» y no muestra el grupo «Gestión»

#### Scenario: Rol admin o staff
- **WHEN** la sesión tiene rol `admin` o `staff`
- **THEN** el menú muestra los seis enlaces de gestión y «Mi perfil»

#### Scenario: Sin sesión
- **WHEN** no hay sesión
- **THEN** el menú solo ofrece iniciar sesión y crear cuenta

### Requirement: Listado de clientes con filtros
La aplicación SHALL mostrar en `/portal/clientes` la lista de clientes de
`GET /v1/clientes` con filtros de texto (`q`) y estado de membresía, paginada con
`listar` (páginas de 100). Cada fila SHALL mostrar el estado con el componente de
badge (Activo/Inactivo/Suspendido).

#### Scenario: Filtro de texto y estado
- **WHEN** el usuario escribe texto o elige un estado
- **THEN** la petición incluye `q` y/o `estado_membresia` y solo se muestran las filas que coinciden

#### Scenario: Listado vacío
- **WHEN** la API devuelve una lista vacía
- **THEN** se muestra un aviso de que no hay registros y la tabla permanece sin filas

### Requirement: Alta, edición y baja de clientes
La aplicación SHALL permitir crear clientes (`POST /v1/clientes`), editarlos con
sustitución total (`PUT /v1/clientes/{id}`) y borrarlos con diálogo de confirmación
(`DELETE /v1/clientes/{id}`). El formulario SHALL pedir nombre (obligatorio), email
opcional, estado de membresía y fecha de inscripción opcional.

#### Scenario: Alta correcta
- **WHEN** el formulario es válido y la API responde 201
- **THEN** el listado se recarga y se muestra un aviso de éxito

#### Scenario: Conflicto de email
- **WHEN** la API responde 409 al crear o editar un cliente
- **THEN** se muestra el detalle del conflicto sin cerrar el formulario

#### Scenario: Baja con historial
- **WHEN** la API responde 409 al borrar un cliente con reservas, pagos o cuentas
- **THEN** se muestra el mensaje del servidor y el registro sigue en el listado

#### Scenario: Límite de longitud
- **WHEN** el nombre supera los 100 caracteres o el email no es válido
- **THEN** el formulario bloquea el envío antes de llamar a la API

### Requirement: Gestión de entrenadores
La aplicación SHALL permitir listar, crear, editar y borrar entrenadores en
`/portal/entrenadores` con los campos nombre (obligatorio), especialidad y teléfono
opcionales, filtrando por texto con `q`.

#### Scenario: Baja de un entrenador con clases
- **WHEN** la API responde 409 al borrar un entrenador que imparte clases
- **THEN** se muestra el detalle y el entrenador permanece en la lista

### Requirement: Gestión de clases
La aplicación SHALL permitir crear, editar y borrar clases en
`/portal/gestion-clases` con nombre (máx. 50), horario UTC sin zona, capacidad
máxima y un entrenador elegido de `GET /v1/entrenadores`. El listado SHALL mostrar
el nombre del entrenador resuelto desde ese listado.

#### Scenario: Horario normalizado
- **WHEN** el usuario elige «2026-11-01T10:00» en el campo de fecha y hora
- **THEN** la petición envía `2026-11-01T10:00:00` sin sufijo de zona

#### Scenario: Capacidad menor que las reservas
- **WHEN** la API responde 409 con «La capacidad no puede ser menor que las reservas»
- **THEN** se muestra ese mensaje y la clase conserva su capacidad anterior

#### Scenario: Entrenador inexistente
- **WHEN** la API responde 404 con «Entrenador con id {id} no existe»
- **THEN** se muestra el mensaje en el aviso de error

### Requirement: Gestión de pagos
La aplicación SHALL permitir listar, crear, editar y borrar pagos en `/portal/pagos`,
con filtros por cliente y método de pago. El formulario SHALL pedir cliente
(obligatorio), monto positivo con dos decimales, fecha de pago y método opcional
(Tarjeta/Transferencia/Efectivo).

#### Scenario: Alta de un pago válido
- **WHEN** el formulario envía un monto mayor que cero con dos decimales y la API responde 201
- **THEN** el listado se recarga con el nuevo pago

#### Scenario: Monto inválido
- **WHEN** el monto es cero, negativo o tiene más de dos decimales
- **THEN** el formulario bloquea el envío o muestra el 422 de la API sin crear el pago

#### Scenario: Cliente inexistente
- **WHEN** la API responde 404 con «Cliente con id {id} no existe»
- **THEN** se muestra el mensaje en el aviso de error

### Requirement: Gestión de cuentas
La aplicación SHALL mostrar en `/portal/cuentas` las cuentas de `GET /v1/users`
(requiere token) con filtros de texto, rol y estado `activo`. Permitirá editar
nombre, email y contraseña opcional con `PUT /v1/users/{id}` y borrar con
confirmación (`DELETE /v1/users/{id}`). Los campos `rol`, `activo` e `id_cliente`
deben mostrarse como de solo lectura.

#### Scenario: Sin token
- **WHEN** la API responde 401 al listar cuentas
- **THEN** se muestra un aviso de que la sesión no es válida

#### Scenario: Email ya registrado
- **WHEN** la API responde 409 con «Email de Cuenta ya registrado»
- **THEN** se muestra el conflicto y el formulario sigue abierto

#### Scenario: Contraseña corta
- **WHEN** la contraseña indicada tiene menos de 12 caracteres
- **THEN** el formulario bloquea el envío y no se envía la petición

### Requirement: Perfil propio
La aplicación SHALL mostrar en `/portal/perfil` los datos de `GET /v1/users/me` y
permitir editar nombre, email y contraseña con `PATCH /v1/users/{id}` de la propia
cuenta. Tras guardar, la sesión local SHALL reflejar el nombre y email nuevos.

#### Scenario: Cambio de nombre y email
- **WHEN** la API responde 200 al PATCH
- **THEN** se muestra éxito, el perfil se recarga y la sesión de navegador muestra el nombre actualizado

#### Scenario: Cambio de contraseña
- **WHEN** el usuario indica una contraseña de 12 a 128 caracteres y guarda
- **THEN** la contraseña se envía como `password`, se guarda el hash en el servidor y la respuesta no contiene credenciales

#### Scenario: Email duplicado
- **WHEN** la API responde 409 al cambiar el email
- **THEN** se muestra «Email de Cuenta ya registrado» sin modificar la sesión

### Requirement: Exportación a CSV
La aplicación SHALL mostrar en `/portal/export` un botón por cada tabla exportable
(clientes, entrenadores, clases, reservas, pagos) que descargue
`GET /v1/export/csv?tablas=<tabla>` como archivo `<tabla>.csv` en el navegador.

#### Scenario: Descarga correcta
- **WHEN** la API responde 200 con `text/csv`
- **THEN** se descarga un archivo con el nombre de la tabla y el contenido CSV

#### Scenario: Fallo de red
- **WHEN** la petición no obtiene respuesta
- **THEN** se muestra un aviso de error y no se descarga ningún archivo

### Requirement: Feedback de operaciones
Toda operación de alta, edición, baja o descarga SHALL mostrar un aviso de éxito o
error con `ToastComponent`, y toda baja SHALL pasar por `ConfirmDialogComponent`.
Los mensajes de error provienen del `detail` de la API sin trazas técnicas.

#### Scenario: Operación correcta
- **WHEN** la API responde 200/201/204
- **THEN** se muestra el aviso de éxito y la lista se actualiza

#### Scenario: Error del servidor
- **WHEN** la API devuelve un `detail` de texto
- **THEN** el aviso muestra ese texto tal cual
