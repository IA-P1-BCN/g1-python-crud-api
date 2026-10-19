"""CRUD y reglas de reserva; solo depende de entidades y puertos del dominio."""

from dataclasses import replace

from src.domain.entities.cuenta import Cuenta
from src.domain.entities.gym import (
    ID_FIELDS,
    Clase,
    Cliente,
    CupoClase,
    Entrenador,
    GymEntity,
    IdentidadCliente,
    Pago,
    Reserva,
)
from src.domain.errors import (
    ConflictError,
    ForbiddenError,
    InvalidQueryError,
    NotFoundError,
)
from src.domain.gym_scope import GymScope
from src.domain.list_filters import ListFilters
from src.domain.repositories.gym_port import GymRepository


class GymUseCases:
    def __init__(self, repository: GymRepository, actor: Cuenta) -> None:
        self._repository = repository
        self._actor = actor

    def _check_operation(
        self, entity_type: type[GymEntity], *, write: bool = False
    ) -> None:
        if not self._actor.activo:
            raise ForbiddenError("La Cuenta está inactiva")
        if self._actor.rol == "admin":
            return
        allowed = (
            self._actor.rol == "cliente" and (not write or entity_type is Reserva)
        ) or (
            self._actor.rol == "staff"
            and entity_type
            in ((Clase, Reserva) if write else (Clase, Reserva, Entrenador))
        )
        if not allowed:
            raise ForbiddenError("No tienes permisos para esta operación")

    def _scope(self, entity_type: type[GymEntity]) -> GymScope | None:
        if self._actor.rol == "admin":
            return None
        if self._actor.rol == "cliente":
            if entity_type in (Clase, Entrenador):
                return None
            return GymScope(id_cliente=self._actor.id_cliente or -1)
        return GymScope(id_entrenador=self._actor.id_entrenador or -1)

    def _ensure_visible(self, entity: GymEntity, *, lock: bool = False) -> None:
        if self._actor.rol == "admin":
            return
        if self._actor.rol == "cliente":
            visible = isinstance(entity, (Clase, Entrenador)) or (
                self._actor.id_cliente is not None
                and entity.id_cliente == self._actor.id_cliente
            )
        else:
            owner = entity
            if isinstance(entity, Reserva):
                owner = self._repository.get(Clase, entity.id_clase, lock=lock)
            visible = (
                self._actor.id_entrenador is not None
                and owner is not None
                and owner.id_entrenador == self._actor.id_entrenador
            )
        if not visible:
            entity_id = getattr(entity, ID_FIELDS[type(entity)])
            raise NotFoundError(f"{type(entity).__name__} con id {entity_id} no existe")

    def _authorize_values(
        self, entity: GymEntity, previous: GymEntity | None = None
    ) -> None:
        if self._actor.rol == "admin":
            return
        if self._actor.rol == "staff":
            owner = entity
            if isinstance(entity, Reserva):
                owner = self._require(Clase, entity.id_clase, lock=True)
            if (
                self._actor.id_entrenador is None
                or owner.id_entrenador != self._actor.id_entrenador
            ):
                raise ForbiddenError("Solo puedes gestionar tus Clases y Reservas")
        elif isinstance(entity, Reserva):
            if (
                self._actor.id_cliente is None
                or entity.id_cliente != self._actor.id_cliente
            ):
                raise ForbiddenError("Solo puedes reservar para tu Cliente vinculado")
            attended = previous.asistio if isinstance(previous, Reserva) else False
            if entity.asistio != attended or (
                attended and entity.id_clase != previous.id_clase
            ):
                raise ForbiddenError("El Cliente no puede modificar la asistencia")

    def list[T: GymEntity](
        self,
        entity_type: type[T],
        offset: int = 0,
        limit: int = 100,
        filters: ListFilters | None = None,
    ) -> list[T]:
        self._check_operation(entity_type)
        if (
            filters is not None
            and filters.date_from is not None
            and filters.date_to is not None
            and filters.date_from > filters.date_to
        ):
            raise InvalidQueryError("El inicio del intervalo no puede superar el final")
        with self._repository.transaction():
            return self._repository.list(
                entity_type, offset, limit, filters, self._scope(entity_type)
            )

    def list_all[T: GymEntity](self, entity_type: type[T]) -> list[T]:
        self._check_operation(entity_type)
        if self._actor.rol != "admin":
            raise ForbiddenError("La exportación requiere rol admin")
        with self._repository.transaction():
            return self._repository.list_all(entity_type)

    def identities_for_clientes(
        self, id_clientes: list[int]
    ) -> dict[int, IdentidadCliente]:
        """Enriquece respuestas con la identidad de `users` (solo lectura)."""
        with self._repository.transaction():
            return self._repository.identities_for_clientes(id_clientes)

    def get[T: GymEntity](self, entity_type: type[T], entity_id: int) -> T:
        self._check_operation(entity_type)
        with self._repository.transaction():
            entity = self._require(entity_type, entity_id)
            self._ensure_visible(entity)
            return entity

    def class_capacity(self, id_clase: int) -> CupoClase:
        self._check_operation(Clase)
        with self._repository.transaction():
            clase = self._require(Clase, id_clase)
            self._ensure_visible(clase)
            count = self._repository.count_reservas(id_clase)
            return CupoClase(
                id_clase=id_clase,
                capacidad_max=clase.capacidad_max,
                reservas=count,
                plazas_disponibles=max(0, clase.capacidad_max - count),
            )

    def create[T: GymEntity](self, entity: T) -> T:
        self._check_operation(type(entity), write=True)
        with self._repository.transaction():
            self._authorize_values(entity)
            self._validate(entity)
            return self._repository.add(entity)

    def update[T: GymEntity](self, entity_type: type[T], entity_id: int, data: T) -> T:
        self._check_operation(entity_type, write=True)
        with self._repository.transaction():
            previous = self._require(entity_type, entity_id, lock=True)
            self._ensure_visible(previous, lock=True)
            entity = replace(data, **{ID_FIELDS[entity_type]: entity_id})
            if isinstance(entity, Reserva):
                entity = replace(entity, fecha_reserva=previous.fecha_reserva)
            self._authorize_values(entity, previous)
            self._validate(entity, previous)
            return self._repository.update(entity)

    def delete(self, entity_type: type[GymEntity], entity_id: int) -> None:
        self._check_operation(entity_type, write=True)
        with self._repository.transaction():
            entity = self._require(entity_type, entity_id, lock=True)
            self._ensure_visible(entity, lock=True)
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
