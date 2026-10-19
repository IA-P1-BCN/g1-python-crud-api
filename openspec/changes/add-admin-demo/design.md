Añadir seed_admin_demo junto a seed_staff y llamarlo dentro de la transacción
de seed_gym. Mantener separado seed_accounts, que gestiona ADMIN_EMAIL y
ADMIN_PASSWORD privados. No restablecer claves existentes ni elevar roles.
Comprobar también email de Cliente para no apropiarse de una identidad.
Contadores y mensaje de alta/omisión, sin imprimir passwords ni hashes.
La contraseña demo es deliberadamente pública, no un secreto de despliegue.
No se requieren variables adicionales ni migración; Render ejecuta el seed
existente al arrancar, una vez integrado y desplegado el cambio.
