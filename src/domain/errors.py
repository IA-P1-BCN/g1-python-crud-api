"""Errores de aplicación sin dependencias de HTTP ni del ORM."""


class AuthenticationError(Exception):
    """Credenciales o sesión no válidas."""


class ForbiddenError(Exception):
    """El usuario no tiene permiso para la operación."""


class NotFoundError(Exception):
    """No existe el registro solicitado."""


class ConflictError(Exception):
    """La operación entra en conflicto con datos existentes."""


class RepositoryUnavailableError(Exception):
    """No se puede acceder a la base de datos."""
