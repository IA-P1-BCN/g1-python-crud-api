## ADDED Requirements

### Requirement: Entorno preparado en un comando
`task env` SHALL dejar un `.env` válido para arrancar la app: copia
`.env.example` si no existe y rellena SECRET_KEY (≥32 caracteres) y
ADMIN_PASSWORD (12–128, sin marcadores) solo cuando faltan, están vacías o
son marcadores. SHALL conservar intacto cualquier valor ya configurado.

#### Scenario: Sin .env
- **WHEN** no existe `.env`
- **THEN** se crea desde `.env.example` con SECRET_KEY y ADMIN_PASSWORD generadas

#### Scenario: .env heredado de V1
- **WHEN** `.env` existe sin SECRET_KEY y con ADMIN_PASSWORD=change-me
- **THEN** se rellenan ambas claves y el resto de valores se conserva

#### Scenario: Todo configurado
- **WHEN** `.env` ya tiene SECRET_KEY y ADMIN_PASSWORD válidas
- **THEN** el fichero no cambia ninguno de sus valores

### Requirement: Puerto MySQL disponible
El bootstrap SHALL comprobar si el puerto MySQL preferido (MYSQL_PORT, por
defecto 3306) está libre en 127.0.0.1; si está ocupado, SHALL fijar el
primer puerto libre de 3307–3316 y avisar por consola.

#### Scenario: 3306 ocupado por un túnel
- **WHEN** 3306 está en uso y 3307 libre
- **THEN** `.env` queda con MYSQL_PORT=3307 y el aviso lo explica

#### Scenario: Puerto preferido libre
- **WHEN** MYSQL_PORT=3307 configurado y libre
- **THEN** no se cambia el valor ni se emite aviso
