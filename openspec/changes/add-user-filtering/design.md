# Decisiones
- CuentaQuery convierte a ListFilters; no pasa schemas a aplicación.
- Reutilizar constructor SQL de filtros con el CRUD V1, sin cambiar su contrato.
- Se mantiene el contrato de autenticación #56/#57 y salida sin credenciales.
- Campos filtrables no permiten elegir SQL arbitrario ni acceder a password_hash.
