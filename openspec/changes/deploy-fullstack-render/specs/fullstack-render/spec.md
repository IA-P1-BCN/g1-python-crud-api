## ADDED Requirements

### Requirement: Despliegue desde main
El sistema SHALL declarar API y frontend Docker gratuitos con branch main y
autoDeployTrigger commit. MySQL SHALL permanecer en Aiven con sus secretos.

#### Scenario: Integración de una PR
- **WHEN** se actualiza main y los servicios están configurados
- **THEN** Render reconstruye ambos sin sustituir la base de datos

### Requirement: Proxy compatible con ambos entornos
Nginx SHALL reenviar /v1/ conservando URI, query, método y Authorization.
HTTPS SHALL verificar certificados y enviar Host y SNI del destino.

#### Scenario: Compose
- **WHEN** se levanta Compose
- **THEN** la API escucha en 8000 y el frontend usa http://api:8000

#### Scenario: Render
- **WHEN** el frontend usa la URL HTTPS pública de la API
- **THEN** /v1/ se reenvía por HTTPS y las rutas Angular sirven index.html

#### Scenario: API dormida
- **WHEN** la API tarda en despertar
- **THEN** el proxy admite hasta 180 segundos de espera por la respuesta
