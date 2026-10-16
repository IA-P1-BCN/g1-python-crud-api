## ADDED Requirements

### Requirement: Portal en el origen de la API
La imagen de producción SHALL incluir Angular y servir su portal en /.
Las rutas de la SPA SHALL poder recargarse directamente. /v1, /docs, /redoc,
/openapi.json y /health SHALL conservar su comportamiento.

#### Scenario: Abrir el portal
- **WHEN** se abre / o /clases en el servicio de la API
- **THEN** se entrega index.html y Angular muestra la pantalla correspondiente

#### Scenario: API o recurso inexistente
- **WHEN** se pide /v1/no-existe o un archivo estático inexistente
- **THEN** responde 404, sin sustituir el error por HTML

### Requirement: Navegación sin prefijo
Los enlaces y destinos de login SHALL usar rutas de raíz. Las URL /portal y
/portal/... SHALL redirigir a sus equivalentes en la raíz.

#### Scenario: Enlace antiguo
- **WHEN** se navega a /portal/clases
- **THEN** Angular redirige a /clases
