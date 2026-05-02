"""
Script de seed : remplit la base avec un jeu de données minimal mais réaliste.

Données :
    - 6 clubs (Real Madrid, PSG, Manchester City, Barcelona, Inter Miami,Al-Nasr)
    - 3 saisons (2022-2023, 2023-2024, 2024-2025)
    - 3 compétitions (Ligue 1, La Liga, Champions League)
    - 6 joueurs avec leur profil détaillé
    - ~10 lignes de stats par joueur sur plusieurs saisons et compétitions

Idempotent : peut être lancé plusieurs fois sans créer de doublons.
"""
from datetime import date

from app import create_app
from app.extensions import db
from app.models.club import Club
from app.models.competition import Competition
from app.models.player import Player
from app.models.player_profile import PlayerProfile
from app.models.player_season_stats import PlayerSeasonStats
from app.models.season import Season


# ----- Données -----

CLUBS = [
    {"name": "Real Madrid", "country": "Spain", "stadium": "Santiago Bernabéu", "founded_year": 1902},
    {"name": "Paris Saint-Germain", "country": "France", "stadium": "Parc des Princes", "founded_year": 1970},
    {"name": "Manchester City", "country": "England", "stadium": "Etihad Stadium", "founded_year": 1880},
    {"name": "FC Barcelona", "country": "Spain", "stadium": "Camp Nou", "founded_year": 1899},
    {"name": "Inter Miami CF", "country": "USA", "stadium": "Chase Stadium", "founded_year": 2018},
    {"name": "Al-Nassr FC", "country": "Saudi Arabia", "stadium": "Al-Awwal Park", "founded_year": 1955},
]

SEASONS = [
    {"year_label": "2022-2023", "start_year": 2022, "end_year": 2023},
    {"year_label": "2023-2024", "start_year": 2023, "end_year": 2024},
    {"year_label": "2024-2025", "start_year": 2024, "end_year": 2025},
]

COMPETITIONS = [
    {"name": "Ligue 1", "country": "France", "type": "league"},
    {"name": "La Liga", "country": "Spain", "type": "league"},
    {"name": "Premier League", "country": "England", "type": "league"},
    {"name": "Champions League", "country": "Europe", "type": "international"},
    {"name": "MLS", "country": "USA", "type": "league"},
    {"name": "Saudi Pro League", "country": "Saudi Arabia", "type": "league"},
]

# Joueurs : (data, profile_data, current_club_name)
PLAYERS = [
    (
        {
            "first_name": "Kylian", "last_name": "Mbappé",
            "birth_date": date(1998, 12, 20), "nationality": "France",
            "position": "Forward", "photo_url": "/static/uploads/mbappe.jpg",
        },
        {"height_cm": 178, "weight_kg": 73, "preferred_foot": "Right", "jersey_number": 9,
         "biography": "Champion du monde 2018 avec la France."},
        "Real Madrid",
    ),
    (
        {
            "first_name": "Lionel", "last_name": "Messi",
            "birth_date": date(1987, 6, 24), "nationality": "Argentina",
            "position": "Forward", "photo_url": "/static/uploads/messi.jpg",
        },
        {"height_cm": 170, "weight_kg": 72, "preferred_foot": "Left", "jersey_number": 10,
         "biography": "Champion du monde 2022, 8 Ballons d'Or."},
        "Inter Miami CF",
    ),
    (
        {
            "first_name": "Erling", "last_name": "Haaland",
            "birth_date": date(2000, 7, 21), "nationality": "Norway",
            "position": "Forward", "photo_url": "/static/uploads/haaland.jpg",
        },
        {"height_cm": 195, "weight_kg": 88, "preferred_foot": "Left", "jersey_number": 9,
         "biography": "Phénomène buteur, soulier d'or européen."},
        "Manchester City",
    ),
    (
        {
            "first_name": "Jude", "last_name": "Bellingham",
            "birth_date": date(2003, 6, 29), "nationality": "England",
            "position": "Midfielder", "photo_url": "/static/uploads/bellingham.jpg",
        },
        {"height_cm": 186, "weight_kg": 75, "preferred_foot": "Right", "jersey_number": 5,
         "biography": "Milieu box-to-box, leader technique du Real."},
        "Real Madrid",
    ),
    (
        {
            "first_name": "Vinícius", "last_name": "Júnior",
            "birth_date": date(2000, 7, 12), "nationality": "Brazil",
            "position": "Forward", "photo_url": "/static/uploads/vinicius.jpg",
        },
        {"height_cm": 176, "weight_kg": 73, "preferred_foot": "Right", "jersey_number": 7,
         "biography": "Ailier explosif, finaliste Ballon d'Or 2024."},
        "Real Madrid",
    ),
    (
        {
            "first_name": "Cristiano", "last_name": "Ronaldo",
            "birth_date": date(1985, 2, 5), "nationality": "Portugal",
            "position": "Forward", "photo_url": "/static/uploads/cr7.jpg",
        },
        {"height_cm": 187, "weight_kg": 83, "preferred_foot": "Right", "jersey_number": 7,
         "biography": "5 Ballons d'Or, recordman de buts en sélection."},
        "Al-Nassr FC",
    ),
]

# Stats : (player_last_name, club_name, season_label, competition_name, dict de stats)
STATS = [
    # Mbappé
    ("Mbappé", "Paris Saint-Germain", "2022-2023", "Ligue 1",
     {"goals": 29, "assists": 6, "appearances": 34, "minutes_played": 2840, "yellow_cards": 4, "red_cards": 0}),
    ("Mbappé", "Paris Saint-Germain", "2022-2023", "Champions League",
     {"goals": 7, "assists": 1, "appearances": 8, "minutes_played": 720, "yellow_cards": 1, "red_cards": 0}),
    ("Mbappé", "Paris Saint-Germain", "2023-2024", "Ligue 1",
     {"goals": 27, "assists": 7, "appearances": 29, "minutes_played": 2400, "yellow_cards": 3, "red_cards": 0}),
    ("Mbappé", "Real Madrid", "2024-2025", "La Liga",
     {"goals": 22, "assists": 5, "appearances": 30, "minutes_played": 2550, "yellow_cards": 5, "red_cards": 0}),
    ("Mbappé", "Real Madrid", "2024-2025", "Champions League",
     {"goals": 9, "assists": 3, "appearances": 11, "minutes_played": 950, "yellow_cards": 2, "red_cards": 0}),

    # Messi
    ("Messi", "Inter Miami CF", "2023-2024", "MLS",
     {"goals": 20, "assists": 16, "appearances": 19, "minutes_played": 1620, "yellow_cards": 2, "red_cards": 0}),
    ("Messi", "Inter Miami CF", "2024-2025", "MLS",
     {"goals": 18, "assists": 12, "appearances": 22, "minutes_played": 1800, "yellow_cards": 1, "red_cards": 0}),

    # Haaland
    ("Haaland", "Manchester City", "2022-2023", "Premier League",
     {"goals": 36, "assists": 8, "appearances": 35, "minutes_played": 2769, "yellow_cards": 5, "red_cards": 0}),
    ("Haaland", "Manchester City", "2022-2023", "Champions League",
     {"goals": 12, "assists": 2, "appearances": 11, "minutes_played": 906, "yellow_cards": 1, "red_cards": 0}),
    ("Haaland", "Manchester City", "2023-2024", "Premier League",
     {"goals": 27, "assists": 5, "appearances": 31, "minutes_played": 2526, "yellow_cards": 2, "red_cards": 0}),
    ("Haaland", "Manchester City", "2024-2025", "Premier League",
     {"goals": 25, "assists": 4, "appearances": 32, "minutes_played": 2680, "yellow_cards": 3, "red_cards": 0}),

    # Bellingham
    ("Bellingham", "Real Madrid", "2023-2024", "La Liga",
     {"goals": 19, "assists": 6, "appearances": 28, "minutes_played": 2380, "yellow_cards": 6, "red_cards": 1}),
    ("Bellingham", "Real Madrid", "2023-2024", "Champions League",
     {"goals": 4, "assists": 2, "appearances": 13, "minutes_played": 1100, "yellow_cards": 3, "red_cards": 0}),
    ("Bellingham", "Real Madrid", "2024-2025", "La Liga",
     {"goals": 11, "assists": 8, "appearances": 33, "minutes_played": 2780, "yellow_cards": 7, "red_cards": 0}),

    # Vinicius
    ("Júnior", "Real Madrid", "2022-2023", "La Liga",
     {"goals": 10, "assists": 9, "appearances": 33, "minutes_played": 2700, "yellow_cards": 8, "red_cards": 1}),
    ("Júnior", "Real Madrid", "2023-2024", "La Liga",
     {"goals": 15, "assists": 6, "appearances": 26, "minutes_played": 2150, "yellow_cards": 7, "red_cards": 0}),
    ("Júnior", "Real Madrid", "2023-2024", "Champions League",
     {"goals": 6, "assists": 4, "appearances": 11, "minutes_played": 945, "yellow_cards": 2, "red_cards": 0}),
    ("Júnior", "Real Madrid", "2024-2025", "La Liga",
     {"goals": 12, "assists": 7, "appearances": 28, "minutes_played": 2310, "yellow_cards": 5, "red_cards": 0}),

    # CR7
    ("Ronaldo", "Al-Nassr FC", "2023-2024", "Saudi Pro League",
     {"goals": 35, "assists": 11, "appearances": 31, "minutes_played": 2750, "yellow_cards": 6, "red_cards": 1}),
    ("Ronaldo", "Al-Nassr FC", "2024-2025", "Saudi Pro League",
     {"goals": 25, "assists": 8, "appearances": 28, "minutes_played": 2400, "yellow_cards": 4, "red_cards": 0}),
]


# ----- Logique de seed -----

def _get_or_create(model, lookup: dict, defaults: dict | None = None):
    """Récupère un objet par les critères `lookup`, le crée sinon."""
    obj = model.query.filter_by(**lookup).first()
    if obj is not None:
        return obj, False
    params = {**lookup, **(defaults or {})}
    obj = model(**params)
    db.session.add(obj)
    db.session.flush()
    return obj, True


def seed_database(verbose: bool = True) -> dict:
    """Insère le jeu de données. Retourne un récap des compteurs."""
    counters = {"clubs": 0, "seasons": 0, "competitions": 0,
                "players": 0, "profiles": 0, "stats": 0}

    # Clubs
    clubs_by_name: dict[str, Club] = {}
    for data in CLUBS:
        obj, created = _get_or_create(Club, lookup={"name": data["name"]}, defaults=data)
        clubs_by_name[obj.name] = obj
        counters["clubs"] += int(created)

    # Saisons
    seasons_by_label: dict[str, Season] = {}
    for data in SEASONS:
        obj, created = _get_or_create(Season, lookup={"year_label": data["year_label"]}, defaults=data)
        seasons_by_label[obj.year_label] = obj
        counters["seasons"] += int(created)

    # Compétitions
    competitions_by_name: dict[str, Competition] = {}
    for data in COMPETITIONS:
        obj, created = _get_or_create(Competition, lookup={"name": data["name"]}, defaults=data)
        competitions_by_name[obj.name] = obj
        counters["competitions"] += int(created)

    # Joueurs et profils
    players_by_lastname: dict[str, Player] = {}
    for player_data, profile_data, club_name in PLAYERS:
        player, created = _get_or_create(
            Player,
            lookup={"first_name": player_data["first_name"], "last_name": player_data["last_name"]},
            defaults={**player_data, "current_club_id": clubs_by_name[club_name].id},
        )
        # Si le joueur existait déjà, on rafraîchit son club courant
        if not created:
            player.current_club_id = clubs_by_name[club_name].id
        players_by_lastname[player.last_name] = player
        counters["players"] += int(created)

        # Profil (One-to-One)
        if player.profile is None:
            profile = PlayerProfile(player_id=player.id, **profile_data)
            db.session.add(profile)
            counters["profiles"] += 1

    db.session.flush()

    # Stats
    for last_name, club_name, season_label, comp_name, payload in STATS:
        player = players_by_lastname[last_name]
        season = seasons_by_label[season_label]
        comp = competitions_by_name[comp_name]
        club = clubs_by_name[club_name]

        existing = PlayerSeasonStats.query.filter_by(
            player_id=player.id, season_id=season.id, competition_id=comp.id,
        ).first()
        if existing is not None:
            # Met à jour les chiffres si déjà présent
            for key, value in payload.items():
                setattr(existing, key, value)
            existing.club_id = club.id
        else:
            db.session.add(PlayerSeasonStats(
                player_id=player.id, club_id=club.id,
                season_id=season.id, competition_id=comp.id,
                **payload,
            ))
            counters["stats"] += 1

    db.session.commit()

    if verbose:
        print("--- Seed terminé ---")
        for key, value in counters.items():
            print(f"  {key}: +{value}")
    return counters


if __name__ == "__main__":
    # Permet de lancer `python seed/seed_data.py` en standalone.
    app = create_app()
    with app.app_context():
        seed_database()
