## ADDED Requirements

### Requirement: Rutas y guards del portal
La aplicación SHALL servir el catálogo bajo `/marketplace`, la autenticación
bajo `/auth`, el panel del staff bajo `/staff` y la administración bajo
`/admin`. Las rutas de `/staff` y `/admin` SHALL exigir sesión (y rol
correspondiente) con `authGuard`/`staffGuard`/`adminGuard` resueltos contra
`GET /v1/users/me`; la raíz `/` SHALL redirigir a `/marketplace`; las rutas
antiguas (`/clientes`, `/gestion-clases`, `/pagos`, `/cuentas`, `/export`,
`/portal/**`) SHALL redirigir a su nueva ubicación.

#### Scenario: Sin sesión en /marketplace
- **WHEN** no hay sesión válida y se pide `/marketplace` o sus subrutas
- **THEN** el guard redirige a `/auth/login` con `returnUrl`

#### Scenario: Cliente en /admin
- **WHEN** la sesión tiene rol `cliente` y se pide una ruta de `/admin`
- **THEN** el guard responde 403 en la UI y redirige a `/marketplace`

#### Scenario: Staff en /admin
- **WHEN** la sesión tiene rol `staff` y se pide `/admin/dashboard`
- **THEN** el guard redirige a `/staff`

#### Scenario: Sesión expirada
- **WHEN** `GET /v1/users/me` responde 401
- **THEN** se limpia la sesión y se redirige a `/auth/login`

### Requirement: Home del marketplace
La aplicación SHALL mostrar en `/marketplace` un hero con bienvenida y un
buscador que envía `q` a `GET /v1/clases`, más una sección de próximas clases
(ordenadas por horario ascendente) presentadas con tarjeta de clase.

#### Scenario: Búsqueda con resultados
- **WHEN** el usuario escribe «yoga» y la API devuelve clases
- **THEN** la petición incluye `q=yoga` y se muestra el grid de resultados

#### Scenario: Catálogo vacío
- **WHEN** `GET /v1/clases` devuelve lista vacía
- **THEN** se muestra un estado vacío con invitación a crear clases (staff/admin) o aviso (cliente)

### Requirement: Detalle de clase y reserva
La aplicación SHALL mostrar el detalle de clase con nombre, horario UTC,
entrenador y plazas disponibles (`GET /v1/clases/{id}/cupo`), y un botón
Reservar que ejecuta `POST /v1/reservas` con `id_clase` de la sesión.

#### Scenario: Reserva correcta
- **WHEN** hay plazas y la API responde 201
- **THEN** se avisa del éxito, se refresca el cupo y se enlaza a «Mis reservas»

#### Scenario: Sin plazas
- **WHEN** la API responde 409 por aforo completo
- **THEN** se muestra el mensaje del servidor y el botón queda deshabilitado

#### Scenario: Sin membresía activa o sin pago
- **WHEN** la API responde 403 por reglas de negocio
- **THEN** se muestra el mensaje del servidor sin crear la reserva

#### Scenario: Duplicada
- **WHEN** la API responde 409 por reserva duplicada
- **THEN** se muestra el conflicto y se enlaza a la reserva existente

### Requirement: Mis reservas
La aplicación SHALL listar en `/marketplace/mis-reservas` las reservas de la
sesión (`GET /v1/reservas?id_cliente=<me>`) con clase, fecha, estado de
asistencia y el cupo de cada clase, más un botón Cancelar que ejecuta
`DELETE /v1/reservas/{id}` con confirmación.

#### Scenario: Cancelar
- **WHEN** el usuario confirma la cancelación y la API responde 204
- **THEN** la reserva desaparece de la lista y el cupo de esa clase queda libre

#### Scenario: Sin reservas
- **WHEN** no hay reservas del cliente
- **THEN** se muestra estado vacío con enlace al catálogo

### Requirement: Panel del staff
La aplicación SHALL ofrecer en `/staff` un panel con «Mis clases»
(`GET /v1/clases` con el alcance de servidor) y «Reservas de mis clases»
(`GET /v1/reservas` con el alcance de servidor). El staff podrá crear, editar y
borrar sus clases, cancelar reservas y marcar asistencia (`PUT /v1/reservas/{id}`
con `asistio: true`). Sin sesión de staff o sin vínculo a entrenador, los
listados se muestran vacíos sin error.

#### Scenario: El staff solo ve lo suyo
- **WHEN** el staff abre «Mis clases»
- **THEN** la respuesta de la API solo contiene sus clases (alcance de servidor)

#### Scenario: Marcar asistencia
- **WHEN** el staff marca asistencia y la API responde 200
- **THEN** la reserva queda como asistida en el listado

### Requirement: Dashboard del admin
La aplicación SHALL mostrar en `/admin/dashboard` gráficas ng2-charts calculadas
con datos reales de `GET /v1/reservas`, `/v1/clientes`, `/v1/entrenadores` y
`/v1/clases`: reservas por mes, asistidas vs canceladas, clientes vs
entrenadores y clases por entrenador. La UI SHALL advertir de que los listados
se limitan a 100 registros por página.

#### Scenario: Gráficas con datos
- **WHEN** la API devuelve reservas y clientes
- **THEN** cada serie se dibuja con los totales calculados en cliente

#### Scenario: Sin datos
- **WHEN** los listados están vacíos
- **THEN** cada gráfica muestra un estado vacío en lugar de un error

### Requirement: Menú por rol
El menú de sesión SHALL mostrar para `cliente` el catálogo, «Mis reservas» y
«Mi perfil»; para `staff` además «Mi panel»; para `admin` además «Admin» y
«Exportar CSV». Sin sesión solo ofrece login y registro.

#### Scenario: Rol cliente
- **WHEN** la sesión tiene rol `cliente`
- **THEN** no aparecen enlaces de staff ni de admin

#### Scenario: Rol admin
- **WHEN** la sesión tiene rol `admin`
- **THEN** aparecen catálogo, panel, admin, export y perfil
