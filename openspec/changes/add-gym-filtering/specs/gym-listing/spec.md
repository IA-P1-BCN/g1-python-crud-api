## Purpose

Permitir al staff localizar clientes, entrenadores, clases, reservas y pagos
mediante criterios combinables y listados paginados de resultados relevantes.

## ADDED Requirements

### Requirement: Búsqueda literal por texto
Los listados de clientes, entrenadores y clases SHALL admitir fragmentos de texto
sin distinguir mayúsculas. `q` busca en nombre/email de clientes,
nombre/especialidad/teléfono de entrenadores y nombre de clase. `%` y `_`
se interpretan como caracteres literales, no como comodines SQL.

#### Scenario: Coincidencia en cualquiera de los campos de búsqueda
- **WHEN** se consulta clientes con `q=ANA`
- **THEN** se devuelven clientes cuyo nombre o email contiene ese fragmento

#### Scenario: Comodines literales
- **WHEN** se busca el nombre `Yoga_100%`
- **THEN** solo coinciden nombres que contienen esos caracteres literalmente

### Requirement: Combinación de filtros antes de paginar
Cada listado SHALL combinar sus filtros con AND, ordenar por ID y aplicar
offset/limit después de filtrar. Sin filtros se conserva el listado anterior.
Sin coincidencias se devuelve 200 con una lista vacía.

#### Scenario: Filtro y segunda página
- **WHEN** se filtra clientes activos con `limit=1&offset=1`
- **THEN** se devuelve el segundo cliente activo por ID, si existe

#### Scenario: Relación sin coincidencias
- **WHEN** se consultan pagos de un ID de cliente válido sin pagos
- **THEN** se devuelve 200 con una lista vacía

### Requirement: Campos y fechas del gimnasio
Los listados SHALL admitir los filtros documentados por entidad: texto y
membresía/inscripción en clientes; texto en entrenadores; entrenador/horario en
clases; cliente/clase/asistencia/fecha en reservas; cliente/método/fecha en pagos.
Los extremos de fecha son inclusivos y los DATETIME usan UTC sin zona.

#### Scenario: Intervalo inclusivo y asistencia falsa
- **WHEN** se filtran reservas por `asistio=false` y un intervalo de fechas
- **THEN** solo se incluyen reservas no asistidas dentro de ambos extremos

#### Scenario: Valores nulos
- **WHEN** se filtra un campo opcional con valor o rango
- **THEN** los registros con null en ese campo no coinciden

### Requirement: Errores de consulta documentados
La API SHALL responder 422 ante tipos, estados, IDs, límites o texto vacíos
inválidos; un intervalo cuyo inicio es posterior al final devuelve 400 con
`detail`. Swagger describe los filtros y las respuestas de error.

#### Scenario: Intervalo invertido
- **WHEN** ambos extremos son válidos pero el inicio es posterior al final
- **THEN** se devuelve 400 sin ejecutar la consulta del listado

#### Scenario: Tipo incorrecto
- **WHEN** se envía un ID negativo, estado desconocido o fecha inválida
- **THEN** se devuelve 422
