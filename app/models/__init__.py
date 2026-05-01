"""
Package des modèles SQLAlchemy.

L'import explicite de chaque modèle ici garantit que SQLAlchemy
enregistre toutes les tables dans son metadata, ce qui est indispensable
pour que Flask-Migrate les détecte automatiquement.

Schéma relationnel :

    Club (1) ----< (N) Player (1) ----- (1) PlayerProfile
                       |
                       | (N)
                       v
                  PlayerSeasonStats (N) >---- (1) Season
                       |
                       | (N)
                       v
                  Competition

Relations exigées par le sujet :
    - One-to-One   : Player <-> PlayerProfile
    - One-to-Many  : Club -> Player ; Season -> PlayerSeasonStats
    - Many-to-Many : Player <-> Competition (via PlayerSeasonStats)
"""
from app.models.club import Club
from app.models.competition import Competition
from app.models.player import Player
from app.models.player_profile import PlayerProfile
from app.models.player_season_stats import PlayerSeasonStats
from app.models.season import Season

__all__ = [
    "Club",
    "Competition",
    "Player",
    "PlayerProfile",
    "PlayerSeasonStats",
    "Season",
]
