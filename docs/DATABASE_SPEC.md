# Especificación de Base de Datos — GymFlow

> Procedencia: fusión de `tmp_docs/documento_PR.docx` y
> `tmp_docs/Relaciones y definiciones.docx` (documentos del cliente). Las
> diferencias entre ambos se detallan en
> [Discrepancias entre documentos](#discrepancias-entre-documentos). El diagrama
> visual está en [EDR_DIAGRAM.md](EDR_DIAGRAM.md).

## Descripción general

- **Objetivo general:** API REST conectada a una base de datos relacional
  orientada a centralizar y automatizar el control de membresías, asignación de
  instructores, facturación y el aforo en las clases grupales programadas.
- **Normalización:** Tercera Forma Normal (3FN), 5 tablas principales.
- **N:N resuelto:** la relación muchos a muchos entre `CLIENTES` y `CLASES` se
  resuelve con la tabla intermedia `RESERVAS`.
- **Valor del motor SQL:** el aislamiento de transacciones garantiza que no hay
  sobreventa de cupos y evita que clientes inactivos o sin pagos asociados
  reserven turnos de entrenamiento.

## Diccionario de datos

### CLIENTES (entidad fuerte)

| Campo | Tipo / Restricción | Rol | Descripción |
|---|---|---|---|
| `id_cliente` | `INT AUTO_INCREMENT` | PK | Identificador único de cada miembro. |
| `nombre` | `VARCHAR(100) NOT NULL` | — | Nombre completo del cliente. |
| `email` | `VARCHAR(150) UNIQUE` | — | Correo electrónico para login y notificaciones. |
| `fecha_inscripcion` | `DATE` *solo PRD* | — | Fecha de alta en el gimnasio. |
| `estado_membresia` | `VARCHAR(20)` | — | Estado del plan: `'Activo'`, `'Inactivo'`, `'Suspendido'` *('Suspendido' solo aparece en el PRD)*. |

### ENTRENADORES (entidad fuerte)

| Campo | Tipo / Restricción | Rol | Descripción |
|---|---|---|---|
| `id_entrenador` | `INT AUTO_INCREMENT` | PK | Identificador único de cada instructor. |
| `nombre` | `VARCHAR(100) NOT NULL` | — | Nombre completo del entrenador. |
| `especialidad` | `VARCHAR(100)` | — | Área técnica (p. ej. CrossFit, Yoga, Musculación). |
| `telefono` | `VARCHAR(20)` *solo PRD* | — | Teléfono de contacto. |

### CLASES (entidad relacionada)

| Campo | Tipo / Restricción | Rol | Descripción |
|---|---|---|---|
| `id_clase` | `INT AUTO_INCREMENT` | PK | Identificador único de la sesión. |
| `nombre_clase` | `VARCHAR(50) NOT NULL` *NOT NULL solo en el diccionario* | — | Nombre del tipo de clase (p. ej. Spinning). |
| `horario` | `DATETIME NOT NULL` *NOT NULL solo en el diccionario* | — | Fecha y hora exacta de la sesión. |
| `capacidad_max` | `INT NOT NULL` *NOT NULL solo en el diccionario* | — | Límite de alumnos permitido (aforo). |
| `id_entrenador` | `INT` | FK → `ENTRENADORES` | Instructor asignado a dictar la clase. |

### RESERVAS (tabla intermedia, resuelve el N:N CLIENTES–CLASES)

| Campo | Tipo / Restricción | Rol | Descripción |
|---|---|---|---|
| `id_reserva` | `INT AUTO_INCREMENT` | PK | Identificador único de la transacción. |
| `id_cliente` | `INT` | FK → `CLIENTES` | Cliente que realiza la reserva. |
| `id_clase` | `INT` | FK → `CLASES` | Clase que es reservada. |
| `fecha_reserva` | `DATETIME` | — | Sello de tiempo de la solicitud. |
| `asistio` | `BOOLEAN DEFAULT FALSE` | — | Indicador de asistencia efectiva para métricas. |

### PAGOS (entidad débil / dependiente)

| Campo | Tipo / Restricción | Rol | Descripción |
|---|---|---|---|
| `id_pago` | `INT AUTO_INCREMENT` | PK | Identificador único del recibo bancario. |
| `id_cliente` | `INT` | FK → `CLIENTES` | Cliente asociado al abono financiero. |
| `monto` | `DECIMAL(10,2) NOT NULL` | — | Cantidad económica cobrada. |
| `fecha_pago` | `DATE` | — | Fecha de emisión de la transacción. |
| `metodo_pago` | `VARCHAR(30)` *solo PRD* | — | Método utilizado: `'Tarjeta'`, `'Transferencia'`, `'Efectivo'`. |

## Relaciones y cardinalidades

| Relación | Cardinalidad | Lectura |
|---|---|---|
| `CLIENTES` → `PAGOS` | 1:N (0:N / 1:1) | Un cliente puede efectuar de cero a muchos pagos; un pago pertenece estrictamente a un único cliente. |
| `ENTRENADORES` → `CLASES` | 1:N (0:N / 1:1) | Un entrenador puede impartir ninguna o múltiples clases; una clase es dirigida por un único entrenador. |
| `CLIENTES` → `RESERVAS` | 1:N (0:N / 1:1) | Un cliente puede agendar de cero a muchas reservas; cada reserva le pertenece a un solo cliente. |
| `CLASES` → `RESERVAS` | 1:N (0:N / 1:1) | Una clase puede recibir de cero a múltiples reservas (hasta su aforo); cada reserva apunta a una única clase. |

## Discrepancias entre documentos

### Resolución aplicada en la issue #10

La responsable de #10 confirmó el alcance V1 y la inclusión de
`fecha_inscripcion`, `telefono` y `metodo_pago` como campos opcionales, además
del estado `Suspendido`. La implementación aplica los `NOT NULL` de clases,
las FK obligatorias de las relaciones y exige estado de membresía y fecha
de pago al crear esos registros.

Decisiones de implementación para revisión del equipo: `VARCHAR` con `CHECK`
para estados y métodos de pago, `UNIQUE (id_cliente, id_clase)`, capacidad y
monto positivos, y FK con `ON DELETE RESTRICT` (HTTP 409 si hay dependencias).
Las reservas bloquean la fila de la clase durante la transacción para impedir
la sobreventa. Se exige al menos un pago registrado; no se deduce su vigencia.

### Discrepancias de los documentos originales

Al fusionar el PRD y el diccionario de datos del cliente se detectaron estas
diferencias, resueltas para #10 según el apartado anterior:

1. **Campos que solo aparecen en el PRD:** `CLIENTES.fecha_inscripcion`,
   `ENTRENADORES.telefono` y `PAGOS.metodo_pago` no están en el diccionario de
   datos. Propuesta: incluirlos (enriquecen el modelo sin coste).
2. **Restricciones que solo aparecen en el diccionario:** `NOT NULL` en
   `CLASES.nombre_clase`, `CLASES.horario` y `CLASES.capacidad_max`. Propuesta:
   aplicarlas (una clase sin horario ni aforo no tiene sentido de negocio).
3. **`estado_membresia`:** el PRD contempla `'Suspendido'` además de
   `'Activo'`/`'Inactivo'`. Propuesta: mantener los tres estados.

## Notas de revisión (equipo G1)

Riesgos detectados antes de implementar las migraciones (las decisiones
aplicadas en #10 se indican arriba):

- **Reservas duplicadas:** ninguna restricción impediría que un cliente reserve
  la misma clase dos veces. Se propone `UNIQUE (id_cliente, id_clase)`.
- **Aforo coherente:** se propone `CHECK (capacidad_max > 0)` en `CLASES`; la
   no-sobreventa de cupos la garantiza la transacción del endpoint de reservas,
   no el esquema.
- **Enums como VARCHAR:** `estado_membresia` y `metodo_pago` son `VARCHAR` con
  valores fijos; en MySQL 8 se pueden tipar como `ENUM` o mantener `VARCHAR`
  con validación en la capa de aplicación (Pydantic). Decisión pendiente.
- **Borrado en cascada:** decidir `ON DELETE` de las FK (p. ej. borrar un
  cliente, ¿borra sus pagos/reservas o se bloquea si tiene historial?). Los
  documentos del cliente no lo especifican.
