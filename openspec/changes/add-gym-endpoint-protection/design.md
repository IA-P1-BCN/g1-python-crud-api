Reutilizar get_current_user al incluir cada router de negocio en main.py.
La identidad se resuelve desde la persistencia en cada petición; no se confía
en roles o estados guardados en el token. Conservar la autorización granular
para #65/#106. Los tests CRUD autentican una Cuenta admin de prueba; los nuevos
tests negativos conservan la dependencia real y prueban todas las operaciones.
