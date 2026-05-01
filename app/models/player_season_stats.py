"""
Modèle PlayerSeasonStats.

C'est la table d'association enrichie qui matérialise :
    - Many-to-One vers Player, Club, Season, Competition
    - Many-to-Many entre Player et Competition (via cette table)

Contraintes :
    - UNIQUE composite (player_id, season_id, competition_id) :
      un joueur n'a qu'une seule ligne de stats par saison ET par compétition.
    - CheckConstraint pour interdire les valeurs négatives.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.competition import Competition
    from app.models.player import Player
    from app.models.season import Season


class PlayerSeasonStats(TimestampMixin, db.Model):
    __tablename__ = "player_season_stats"
    __table_args__ = (
        UniqueConstraint(
            "player_id", "season_id", "competition_id",
            name="uq_player_season_competition",
        ),
        CheckConstraint("goals >= 0", name="ck_stats_goals_positive"),
        CheckConstraint("assists >= 0", name="ck_stats_assists_positive"),
        CheckConstraint("appearances >= 0", name="ck_stats_appearances_positive"),
        CheckConstraint("minutes_played >= 0", name="ck_stats_minutes_positive"),
        CheckConstraint("yellow_cards >= 0", name="ck_stats_yellow_positive"),
        CheckConstraint("red_cards >= 0", name="ck_stats_red_positive"),
        # Index combiné utile pour la route /api/players/{id}/stats?season=...
        Index("ix_stats_player_season", "player_id", "season_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # ----- Clés étrangères -----
    # Player : suppression cascade (si on supprime le joueur, on supprime ses stats).
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Club : SET NULL (le club peut disparaître, on garde l'historique de stats).
    club_id: Mapped[int | None] = mapped_column(
        ForeignKey("clubs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # Season : RESTRICT (on protège l'intégrité historique).
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    # Competition : RESTRICT (idem).
    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # ----- Statistiques (default=0 pour faciliter les inserts partiels) -----
    goals: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assists: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    appearances: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minutes_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    yellow_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    red_cards: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ----- Relations inverses -----
    player: Mapped["Player"] = relationship(back_populates="stats", lazy="joined")
    club: Mapped["Club | None"] = relationship(back_populates="stats", lazy="joined")
    season: Mapped["Season"] = relationship(back_populates="stats", lazy="joined")
    competition: Mapped["Competition"] = relationship(back_populates="stats", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<PlayerSeasonStats id={self.id} "
            f"player_id={self.player_id} season_id={self.season_id} "
            f"competition_id={self.competition_id} "
            f"goals={self.goals} assists={self.assists}>"
        )
