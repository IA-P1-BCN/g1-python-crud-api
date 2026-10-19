## MODIFIED Requirements

### Requirement: Rutas del portal sin 404
El servidor SHALL servir `index.html` al refrescar o enlazar en profundidad
cualquier ruta del portal: las secciones `auth`, `marketplace`, `staff` y
`admin`, además de las ya conocidas. Las peticiones a rutas de API siguen
devolviendo JSON.

#### Scenario: Refresco en ruta nueva
- **WHEN** se abre `/staff/reservas` o `/marketplace/clases/5` directamente
- **THEN** se sirve la app (no un 404 JSON)

#### Scenario: Ruta de API desconocida
- **WHEN** se pide `/v1/no-existe`
- **THEN** se devuelve el 404 JSON habitual
