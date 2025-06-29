from __future__ import annotations

from django.db.models import query


class SafeDeleteQueryset(query.QuerySet):
    """Queryset для мягкого удаления."""

    def delete(self) -> None:
        return super().update(deleted=True)
