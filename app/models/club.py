"""
Modèle Club.

Relations :
    - One-to-Many : Club -> Player (un club a plusieurs joueurs actuels)
    - One-to-Many : Club -> PlayerSeasonStats (stats d'un joueur sous ce club)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.player_season_stats import PlayerSeasonStats


class Club(TimestampMixin, db.Model):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stadium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ----- Relations -----
    # One-to-Many : un club a plusieurs joueurs (current_club).
    # Si le club est supprimé, le joueur reste mais perd son club (SET NULL côté Player).
    players: Mapped[list["Player"]] = relationship(
        back_populates="current_club",
        lazy="selectin",
    )

    # One-to-Many : stats associées à ce club.
    # ondelete=RESTRICT côté stats : interdit de supprimer un club tant que des stats l'utilisent.
    stats: Mapped[list["PlayerSeasonStats"]] = relationship(
        back_populates="club",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Club id={self.id} name={self.name!r}>"
