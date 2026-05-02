"""
Package des schémas Marshmallow.

Importer les schémas ici garantit qu'ils sont enregistrés dans le registre
de classes de Marshmallow, ce qui permet aux références par chaîne dans
les `Nested(...)` (ex. `"ClubSchema"`) de résoudre correctement.
"""
from app.schemas.club_schema import ClubSchema, club_schema, clubs_schema
from app.schemas.competition_schema import (
    CompetitionSchema,
    competition_schema,
    competitions_schema,
)
from app.schemas.player_schema import PlayerSchema, player_schema, players_schema
from app.schemas.profile_schema import PlayerProfileSchema, profile_schema
from app.schemas.season_schema import SeasonSchema, season_schema, seasons_schema
from app.schemas.stats_schema import (
    PlayerSeasonStatsSchema,
    stats_list_schema,
    stats_schema,
)

__all__ = [
    "ClubSchema", "club_schema", "clubs_schema",
    "CompetitionSchema", "competition_schema", "competitions_schema",
    "PlayerSchema", "player_schema", "players_schema",
    "PlayerProfileSchema", "profile_schema",
    "SeasonSchema", "season_schema", "seasons_schema",
    "PlayerSeasonStatsSchema", "stats_schema", "stats_list_schema",
]
