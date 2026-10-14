## ADDED Requirements

### Requirement: Códigos semánticos
La API SHALL traducir InvalidQueryError a 400, AuthenticationError a 401 con
WWW-Authenticate Bearer y ForbiddenError a 403. SHALL conservar 404/409/422/500/503.
Los errores de dominio SHALL responder detail como string y no registrarse
como ERROR cuando son errores del cliente.

#### Scenario: Consulta incoherente
- **WHEN** un intervalo de fechas está invertido
- **THEN** responde 400 sin ejecutar la consulta

#### Scenario: Autenticación y acceso
- **WHEN** no se acredita identidad válida
- **THEN** responde 401 con reto Bearer
- **AND** una identidad acreditada inactiva recibe 403 sin reto Bearer

### Requirement: No exposición de secretos
Errores de validación de auth/users y representaciones de errores de settings
SHALL omitir los valores de contraseña y claves sensibles.

#### Scenario: Configuración inválida
- **WHEN** SECRET_KEY es demasiado corta
- **THEN** el error indica el requisito sin imprimir su valor ni otros secretos
