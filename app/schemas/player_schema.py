"""
Schémas Marshmallow pour Player.

En sortie, on enrichit la réponse avec :
    - `current_club` : un sous-objet club (lecture seule, sans ses propres relations
      pour éviter les boucles infinies).
    - `profile`      : un sous-objet profil (lecture seule).
    - `full_name`    : champ calculé pratique pour le frontend.

En entrée, le payload accepte uniquement les champs propres au joueur,
y compris `current_club_id`. Le profil et les stats sont gérés par leurs
propres endpoints.
"""
from marshmallow import validate

from app.extensions import ma
from app.models.player import Player


class PlayerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True
        include_fk = True
        ordered = True
        dump_only = ("id", "created_at", "updated_at")

    # Validation soft du poste : on accepte n'importe quoi mais on
    # documente les valeurs canoniques (utile pour le frontend / Swagger).
    position = ma.String(
        validate=validate.OneOf(
            ["Goalkeeper", "Defender", "Midfielder", "Forward"]
        ),
        allow_none=True,
    )

    # Champ calculé exposé en lecture.
    full_name = ma.String(dump_only=True)

    # Relations exposées en sortie uniquement.
    # `only=` limite la profondeur de sérialisation (pas de boucles infinies).
    current_club = ma.Nested(
        "ClubSchema",
        only=("id", "name", "country", "logo_url"),
        dump_only=True,
    )
    profile = ma.Nested(
        "PlayerProfileSchema",
        exclude=("player_id", "created_at", "updated_at"),
        dump_only=True,
    )


player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
