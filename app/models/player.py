"""
Modèle Player (joueur).

Relations :
    - One-to-One  : Player <-> PlayerProfile
    - Many-to-One : Player -> Club (current_club_id)
    - One-to-Many : Player -> PlayerSeasonStats
    - Many-to-Many: Player <-> Competition (via PlayerSeasonStats)
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.player_profile import PlayerProfile
    from app.models.player_season_stats import PlayerSeasonStats


class Player(TimestampMixin, db.Model):
    __tablename__ = "players"
    __table_args__ = (
        # Index composite pour accélérer les recherches par nom complet.
        Index("ix_players_full_name", "last_name", "first_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    # Position : "Goalkeeper", "Defender", "Midfielder", "Forward". Texte libre côté DB,
    # validation gérée plus tard par Marshmallow.
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ----- FK vers le club actuel (Many-to-One) -----
    # SET NULL : si le club est supprimé, le joueur reste mais devient "sans club".
    current_club_id: Mapped[int | None] = mapped_column(
        ForeignKey("clubs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ----- Relations -----
    # Many-to-One vers Club.
    current_club: Mapped["Club | None"] = relationship(
        back_populates="players",
        lazy="joined",
    )

    # One-to-One vers PlayerProfile.
    # cascade="all, delete-orphan" : supprimer un joueur supprime son profil.
    # uselist=False : SQLAlchemy traite cette relation comme un objet unique, pas une liste.
    profile: Mapped["PlayerProfile | None"] = relationship(
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
    )

    # One-to-Many vers PlayerSeasonStats.
    # cascade : supprimer un joueur supprime ses stats (car elles n'ont plus de sens).
    stats: Mapped[list["PlayerSeasonStats"]] = relationship(
        back_populates="player",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.full_name!r}>"
