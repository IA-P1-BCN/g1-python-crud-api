"""Errores del negocio independientes de HTTP y de la base de datos."""


class NotFoundError(Exception):
    """La entidad solicitada no existe."""


class ConflictError(Exception):
    """La operación vulnera una regla de negocio o una relación existente."""


class RepositoryUnavailableError(Exception):
    """No se puede acceder a la persistencia."""
