"""CRUD y reglas de reserva; solo depende de entidades y puertos del dominio."""

from dataclasses import replace

from src.domain.entities.gym import (
    ID_FIELDS,
    Clase,
    Cliente,
    Entrenador,
    GymEntity,
    Pago,
    Reserva,
)
from src.domain.errors import ConflictError, NotFoundError
from src.domain.repositories.gym_port import GymRepository


class GymUseCases:
    def __init__(self, repository: GymRepository) -> None:
        self._repository = repository

    def list[T: GymEntity](
        self, entity_type: type[T], offset: int = 0, limit: int = 100
    ) -> list[T]:
        with self._repository.transaction():
            return self._repository.list(entity_type, offset, limit)

    def get[T: GymEntity](self, entity_type: type[T], entity_id: int) -> T:
        with self._repository.transaction():
            return self._require(entity_type, entity_id)

    def create[T: GymEntity](self, entity: T) -> T:
        with self._repository.transaction():
            self._validate(entity)
            return self._repository.add(entity)

    def update[T: GymEntity](self, entity_type: type[T], entity_id: int, data: T) -> T:
        with self._repository.transaction():
            previous = self._require(entity_type, entity_id, lock=True)
            entity = replace(data, **{ID_FIELDS[entity_type]: entity_id})
            if isinstance(entity, Reserva):
                entity = replace(entity, fecha_reserva=previous.fecha_reserva)
            self._validate(entity, previous)
            return self._repository.update(entity)

    def delete(self, entity_type: type[GymEntity], entity_id: int) -> None:
        with self._repository.transaction():
            entity = self._require(entity_type, entity_id, lock=True)
            self._repository.delete(entity)

    def _require[T: GymEntity](
        self, entity_type: type[T], entity_id: int, *, lock: bool = False
    ) -> T:
        entity = self._repository.get(entity_type, entity_id, lock=lock)
        if entity is None:
            raise NotFoundError(f"{entity_type.__name__} con id {entity_id} no existe")
        return entity

    def _validate(self, entity: GymEntity, previous: GymEntity | None = None) -> None:
        if isinstance(entity, Cliente):
            if entity.estado_membresia not in {"Activo", "Inactivo", "Suspendido"}:
                raise ConflictError(
                    "La membresía debe ser Activo, Inactivo o Suspendido"
                )
        elif isinstance(entity, Clase):
            self._require(Entrenador, entity.id_entrenador)
            if entity.capacidad_max <= 0:
                raise ConflictError("La capacidad debe ser mayor que cero")
            if previous is not None:
                ocupacion = self._repository.count_reservas(entity.id_clase)
                if entity.capacidad_max < ocupacion:
                    raise ConflictError(
                        "La capacidad no puede ser menor que las reservas"
                    )
        elif isinstance(entity, Pago):
            self._require(Cliente, entity.id_cliente, lock=True)
            if entity.monto <= 0:
                raise ConflictError("El monto debe ser mayor que cero")
            if entity.metodo_pago not in {None, "Tarjeta", "Transferencia", "Efectivo"}:
                raise ConflictError(
                    "El método debe ser Tarjeta, Transferencia o Efectivo"
                )
        elif isinstance(entity, Reserva):
            # Modificar solo la asistencia conserva una reserva histórica aunque
            # el cliente haya pasado a estar inactivo después de reservar.
            if (
                isinstance(previous, Reserva)
                and previous.id_cliente == entity.id_cliente
                and previous.id_clase == entity.id_clase
            ):
                return
            cliente = self._require(Cliente, entity.id_cliente, lock=True)
            # El bloqueo de la clase serializa admisiones y cambios de aforo.
            # Se adquiere antes de consultar pagos/ocupación para evitar una
            # lectura obsoleta con el aislamiento REPEATABLE READ de MySQL.
            clase = self._require(Clase, entity.id_clase, lock=True)
            if cliente.estado_membresia != "Activo":
                raise ConflictError("Solo los clientes activos pueden reservar")
            if not self._repository.has_pago(entity.id_cliente):
                raise ConflictError("El cliente debe tener al menos un pago registrado")
            if self._repository.has_reserva(
                entity.id_cliente, entity.id_clase, entity.id_reserva
            ):
                raise ConflictError("El cliente ya tiene una reserva para esta clase")
            ocupacion = self._repository.count_reservas(
                entity.id_clase, entity.id_reserva
            )
            if ocupacion >= clase.capacidad_max:
                raise ConflictError("La clase no tiene plazas disponibles")
