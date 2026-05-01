"""
Modèle Season.

Relations :
    - One-to-Many : Season -> PlayerSeasonStats
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.player_season_stats import PlayerSeasonStats


class Season(TimestampMixin, db.Model):
    __tablename__ = "seasons"
    __table_args__ = (
        CheckConstraint("end_year >= start_year", name="ck_season_year_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Libellé lisible (ex. "2023-2024"). Unique pour éviter les doublons.
    year_label: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # ----- Relations -----
    # ondelete=RESTRICT côté stats : impossible de supprimer une saison utilisée par des stats.
    stats: Mapped[list["PlayerSeasonStats"]] = relationship(
        back_populates="season",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Season id={self.id} label={self.year_label!r}>"
