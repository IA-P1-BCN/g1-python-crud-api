# GymFlow

Sistema de gestión de un gimnasio (clientes, clases, reservas y pagos) expuesto
como API REST. Desde la integración de la especificación de gestión de
usuarios (V2), toda persona que accede al sistema lo hace con una Cuenta.

## Language

### Acceso e identidad

**Cuenta**:
Identidad de acceso al sistema: email único y contraseña, con un Rol y un
indicador de `activo` (puede iniciar sesión).
_Avoid_: User, usuario, login, perfil

**Rol**:
Alcance de permisos de una Cuenta: `admin`, `staff` o `cliente`.
_Avoid_: perfil, permiso, rango

**Cliente**:
Socio del gimnasio: la persona que se inscribe, paga y reserva Clases. Puede
estar vinculado a una Cuenta; no toda Cuenta es de un Cliente (admin y staff
tienen Cuenta sin ser socios).
_Avoid_: usuario, User, cuenta, socio

**Estado de Membresía**:
Situación de un Cliente en el negocio: `Activo`, `Inactivo` o `Suspendido`.
Decide si puede reservar; es distinto del `activo` de la Cuenta, que decide
si puede iniciar sesión.
_Avoid_: estado (a secas), status, activo

### Negocio del gimnasio

**Entrenador**:
Persona que imparte Clases. Si accede al sistema, lo hace con una Cuenta de
Rol `staff`, vinculada explícitamente mediante `id_entrenador`; la entidad de
negocio y el Rol no son lo mismo. Gestiona sus Clases y sus Reservas asociadas.
_Avoid_: staff (como entidad), monitor

**Clase**:
Sesión impartida por un Entrenador con un aforo limitado de plazas.

**Reserva**:
Plaza de un Cliente en una Clase. Requiere Cliente con Estado de Membresía
`Activo`, al menos un Pago y plaza disponible; un Cliente no puede tener dos
Reservas para la misma Clase.

**Pago**:
Cobro registrado a nombre de un Cliente (monto, fecha, método).
