# 0002: La identidad (nombre y email) vive exclusivamente en Cuentas

Status: accepted (2026-10-19)

Tras ADR 0001, `clientes` conservaba sus propias columnas `nombre` y `email`
heredadas de V1, duplicando la identidad de `users` y permitiendo que ambas
copias divergieran. Decidimos que `users` es la **única** tabla con nombre y
email: la migración `2bf39c12ed06` traslada la identidad de cada cliente a su
Cuenta vinculada (creándole una inactiva e inaccesible si no la tenía) y
borra las columnas de `clientes`.

Consecuencias: `/v1/clientes` acepta y persiste solo el perfil de negocio,
pero sus respuestas (y las de reservas, vía `id_user`) resuelven nombre y
email de la Cunta vinculada en lectura; buscar personas por nombre/email se
hace en `/v1/users`. Los entrenadores inician sesión con su Cuenta staff
vinculada (`users.id_entrenador`). Amplía el ADR 0001, que sigue vigente.
