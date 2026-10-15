## ADDED Requirements

### Requirement: Identidad independiente
La Cuenta SHALL tener id, nombre, email único obligatorio, password_hash, activo,
fecha_creacion UTC, rol admin/staff/cliente e id_cliente opcional y único.

#### Scenario: Esquema aplicado
- **WHEN** se ejecuta la migración
- **THEN** la tabla versions registra 0.3 para que /health/db lea la versión del esquema
- **AND** users existe y rechaza emails duplicados y vínculos repetidos
- **AND** borrar un Cliente vinculado se bloquea; borrar su Cuenta conserva el Cliente

### Requirement: Credenciales protegidas
Las contraseñas SHALL almacenarse con Argon2 y salt individual; los secretos de
configuración SHALL usar SecretStr. Los hashes no aparecen en repr de la entidad.

#### Scenario: Verificación
- **WHEN** se guarda una contraseña y se verifica
- **THEN** solo la contraseña original coincide y el valor almacenado es un hash

### Requirement: Inicialización segura e idempotente
El seed SHALL crear un admin sin Cliente usando ADMIN_EMAIL y ADMIN_PASSWORD
obligatoria para el seed; SHALL crear cuentas inactivas con secretos aleatorios no
compartidos para clientes con email válido. SHALL omitir clientes sin email válido
y conflictos de email sin apropiarse de cuentas existentes. Repetirlo SHALL
conservar datos, hashes y permisos previos.

#### Scenario: Dos ejecuciones
- **WHEN** se ejecuta el seed dos veces
- **THEN** no se duplican cuentas ni se reinician contraseñas

#### Scenario: Administrador sin contraseña configurada
- **WHEN** falta ADMIN_PASSWORD o sigue siendo un marcador
- **THEN** el seed falla antes de escribir datos
