"""
Modèle PlayerProfile.

Relation :
    - One-to-One : Player <-> PlayerProfile

L'unicité de la relation est garantie par la contrainte UNIQUE sur la
colonne `player_id`. Côté ORM, l'attribut `Player.profile` utilise
`uselist=False` pour exposer un objet unique et non une liste.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models._mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.player import Player


class PlayerProfile(TimestampMixin, db.Model):
    __tablename__ = "player_profiles"
    __table_args__ = (
        CheckConstraint("height_cm IS NULL OR height_cm BETWEEN 100 AND 250", name="ck_profile_height"),
        CheckConstraint("weight_kg IS NULL OR weight_kg BETWEEN 30 AND 200", name="ck_profile_weight"),
        CheckConstraint(
            "preferred_foot IS NULL OR preferred_foot IN ('Left', 'Right', 'Both')",
            name="ck_profile_foot",
        ),
        CheckConstraint(
            "jersey_number IS NULL OR jersey_number BETWEEN 1 AND 99",
            name="ck_profile_jersey",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK + UNIQUE : c'est ce qui rend la relation One-to-One.
    # ondelete CASCADE : si le joueur est supprimé, le profil l'est aussi.
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_foot: Mapped[str | None] = mapped_column(String(10), nullable=True)
    jersey_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ----- Relation inverse -----
    player: Mapped["Player"] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"<PlayerProfile id={self.id} player_id={self.player_id}>"
