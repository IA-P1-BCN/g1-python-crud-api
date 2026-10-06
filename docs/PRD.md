# Documento de Requisitos del Proyecto (PRD)

**Proyecto:** GymFlow API & Backend Relacional
**Autor:** G1 – Factoría 5
**Fecha:** Octubre 2026
**Versión:** 1.0

> Procedencia: `tmp_docs/documento_PR.docx` (documento del cliente, transcrito a
> markdown). La especificación detallada de las tablas vive en
> [DATABASE_SPEC.md](DATABASE_SPEC.md) y el diagrama en
> [EDR_DIAGRAM.md](EDR_DIAGRAM.md).

## 1. Objetivos del proyecto

El proyecto GymFlow API tiene como objetivo principal diseñar e implementar una
arquitectura backend robusta y eficiente para centralizar, gestionar y automatizar
las operaciones diarias de un gimnasio o centro deportivo. La solución conecta una
API RESTful con una base de datos relacional SQL, garantizando la consistencia,
integridad y disponibilidad de la información comercial crítica.

Objetivos específicos:

- **Automatización del control de acceso y membresías:** validar en tiempo real
  si un miembro cuenta con una suscripción activa antes de permitir su ingreso
  o reserva.
- **Optimización de la ocupación de clases:** controlar los aforos de las
  sesiones dirigidas, evitando la sobreventa de cupos y gestionando listas de
  asistencia.
- **Centralización de la información:** eliminar el uso de registros físicos o
  herramientas descentralizadas (como hojas de cálculo) para evitar errores
  operativos.

## 2. Público objetivo (Target Audience)

El sistema está diseñado con un enfoque multi-actor, proveyendo endpoints e
información estructurada para tres perfiles clave:

- **Administradores y dueños del gimnasio:** requieren visibilidad del estado
  financiero de las membresías, métricas de asistencia total y rendimiento de
  los entrenadores.
- **Staff y entrenadores:** necesitan conocer la lista de alumnos inscritos en
  sus clases diarias, actualizar perfiles y validar pagos de forma ágil.
- **Clientes / miembros del gimnasio:** a través de aplicaciones cliente
  conectadas a esta API, buscan reservar clases, visualizar el estado de su
  plan y registrar su asistencia técnica.

## 3. Funcionalidades principales de la API

- **Gestión de clientes:** altas, bajas, modificaciones y consulta del estado
  de membresías.
- **Control de clases dirigidas:** creación de horarios, asignación de
  instructores y definición de capacidades máximas (aforos).
- **Sistema de reservas:** permite a los miembros agendar una plaza en una
  clase específica y cancelar si es necesario, liberando el cupo
  automáticamente.
- **Monitoreo de asistencia:** registro preciso de la fecha y hora en la que un
  cliente asiste a una sesión programada.

## 4. Estructura de datos relacionales

Para dar soporte a estas necesidades del negocio, se ha estructurado una base de
datos relacional compuesta por **5 tablas principales**. Las relaciones de
muchos a muchos (N:N) se han resuelto mediante una tabla intermedia de
acoplamiento (`RESERVAS`), optimizando el rendimiento de las consultas e
indexación.

Las tablas son:

| Tabla | Rol |
|---|---|
| `CLIENTES` | Entidad fuerte — miembros del gimnasio |
| `ENTRENADORES` | Entidad fuerte — instructores |
| `CLASES` | Sesiones programadas, con aforo y entrenador asignado |
| `RESERVAS` | Tabla intermedia que resuelve el N:N entre `CLIENTES` y `CLASES` |
| `PAGOS` | Entidad débil — abonos económicos de cada cliente |

### Resumen de relaciones y cardinalidades

- **CLIENTES a PAGOS (1:N):** un cliente puede efectuar de 0 a muchos pagos
  (0:N); un pago específico pertenece estrictamente a un único cliente (1:1).
- **ENTRENADORES a CLASES (1:N):** un entrenador puede impartir de 0 a
  múltiples clases (0:N); una clase es dirigida por un único entrenador (1:1).
- **CLIENTES a CLASES (N:N, a través de RESERVAS):** se divide en dos
  relaciones dirigidas a la tabla intermedia: CLIENTES a RESERVAS (1:N) y
  CLASES a RESERVAS (1:N). Esto permite que un cliente agende muchas clases y
  una clase reciba a muchos clientes de manera controlada y sin redundancia de
  datos.
