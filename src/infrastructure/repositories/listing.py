"""Filtros SQL compartidos: se aplican antes del orden y la paginación."""

from sqlalchemy import Select, func, or_

from src.domain.list_filters import ListFilters
from src.infrastructure.database.models.base import Base


def apply_list_filters(
    statement: Select,
    model: type[Base],
    filters: ListFilters | None,
    search_fields: tuple[str, ...] = (),
) -> Select:
    filters = filters or ListFilters()
    for name, value in filters.contains:
        statement = statement.where(
            func.lower(getattr(model, name)).contains(value.lower(), autoescape=True)
        )
    for name, value in filters.equals:
        statement = statement.where(getattr(model, name) == value)
    if filters.date_field is not None:
        column = getattr(model, filters.date_field)
        if filters.date_from is not None:
            statement = statement.where(column >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(column <= filters.date_to)
    if filters.search is not None:
        statement = statement.where(
            or_(
                *(
                    func.lower(getattr(model, name)).contains(
                        filters.search.lower(), autoescape=True
                    )
                    for name in search_fields
                )
            )
        )
    return statement
