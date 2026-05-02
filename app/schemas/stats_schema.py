"""
Schémas Marshmallow pour PlayerSeasonStats.

En sortie, on niche les références utiles (joueur, club, saison, compétition)
pour que le frontend n'ait pas à faire 4 appels supplémentaires pour résoudre
les FK.
"""
from marshmallow import validate

from app.extensions import ma
from app.models.player_season_stats import PlayerSeasonStats


class PlayerSeasonStatsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PlayerSeasonStats
        load_instance = True
        include_fk = True
        ordered = True
        dump_only = ("id", "created_at", "updated_at")

    # Validation : pas de stats négatives (doublé avec le CHECK SQL).
    goals = ma.Integer(validate=validate.Range(min=0))
    assists = ma.Integer(validate=validate.Range(min=0))
    appearances = ma.Integer(validate=validate.Range(min=0))
    minutes_played = ma.Integer(validate=validate.Range(min=0))
    yellow_cards = ma.Integer(validate=validate.Range(min=0))
    red_cards = ma.Integer(validate=validate.Range(min=0))

    # Sous-objets en lecture seule pour l'output.
    player = ma.Nested(
        "PlayerSchema",
        only=("id", "first_name", "last_name", "position", "photo_url"),
        dump_only=True,
    )
    club = ma.Nested(
        "ClubSchema",
        only=("id", "name", "logo_url"),
        dump_only=True,
    )
    season = ma.Nested(
        "SeasonSchema",
        only=("id", "year_label"),
        dump_only=True,
    )
    competition = ma.Nested(
        "CompetitionSchema",
        only=("id", "name", "country"),
        dump_only=True,
    )


stats_schema = PlayerSeasonStatsSchema()
stats_list_schema = PlayerSeasonStatsSchema(many=True)
