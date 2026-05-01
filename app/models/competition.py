"""
Modèle Competition.

Relations :
    - One-to-Many  : Competition -> PlayerSeasonStats
    - Many-to-Many : Player <-> Competition (via la table d'association
      enrichie PlayerSeasonStats : un joueur participe à plusieurs
      compétitions, et une compétition rassemble plusieurs joueurs).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.player_season_stats import PlayerSeasonStats


class Competition(TimestampMixin, db.Model):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Type : "league", "cup", "international", etc. Texte libre pour rester souple.
    type: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # ----- Relations -----
    stats: Mapped[list["PlayerSeasonStats"]] = relationship(
        back_populates="competition",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Competition id={self.id} name={self.name!r}>"
