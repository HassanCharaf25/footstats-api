"""
Mixin de timestamps réutilisable.

Ajoute automatiquement les colonnes `created_at` et `updated_at` à tout
modèle qui en hérite. Utile pour l'audit et le debug en soutenance.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Ajoute created_at et updated_at à un modèle SQLAlchemy."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
