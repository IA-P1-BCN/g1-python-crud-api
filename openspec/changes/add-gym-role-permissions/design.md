Inyectar GymUseCases con Cuenta actual en el wiring; controllers traducen schemas
y llaman a casos de uso. El caso de uso comprueba tipo de operación, propiedad
del registro anterior y del nuevo dentro de la transacción. No confiar en IDs
o filtros del cliente para delimitar acceso. La propiedad del staff se comprueba
con id_entrenador explícito, nunca por nombre/email ni igualdad accidental de IDs.

GymScope es un contrato de dominio separado de filtros de usuario. SQLAlchemy
lo combina antes de paginar; Reservas del staff usan una subconsulta de Clases.
Las lecturas internas de reglas de aforo/pago conservan su alcance necesario.
La exportación completa es administrativa. Cuenta sin vínculo usa alcance vacío.

Mantener bloqueo de Reserva y de Clases implicadas para escrituras autorizadas;
denegar cambios de propietario o de asistencia de cliente antes de persistir.
Admin gestiona Clientes/Pagos/Entrenadores; staff solo Clases/Reservas propias,
y consulta su Entrenador. Clientes consultan catálogo de Clases/Entrenadores.

Migración incremental sobre la cuenta demo de main, con id_entrenador nullable
UNIQUE/FK RESTRICT y versión de esquema 0.4. Sin asociaciones automáticas ni
credenciales nuevas. PUT dedicado permite un id positivo o null y exige admin;
la Cuenta de destino debe ser staff. Cambiar el rol invalida su alcance anterior.

El frontend calculaba cupo descargando reservas por clase. Con el aislamiento
eso contaría solo las propias: se sustituye por cupo agregado autorizado, que no
incluye datos de clientes y conserva la validación final de aforo en la reserva.
