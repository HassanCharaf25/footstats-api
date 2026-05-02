"""Tests des endpoints clubs et stats : CRUD, conflits, contraintes."""


# ---------------------------------------------------------------------------
# Clubs
# ---------------------------------------------------------------------------

def test_create_club_then_duplicate_returns_409(client):
    first = client.post("/api/clubs", json={"name": "Real Madrid", "country": "Spain"})
    assert first.status_code == 201

    second = client.post("/api/clubs", json={"name": "Real Madrid", "country": "Spain"})
    assert second.status_code == 409
    assert second.get_json()["error"] == "Conflict"


def test_list_and_patch_club(client):
    create = client.post("/api/clubs", json={"name": "PSG"})
    cid = create.get_json()["id"]

    listing = client.get("/api/clubs")
    assert listing.status_code == 200
    assert listing.get_json()["total"] == 1

    patch = client.patch(f"/api/clubs/{cid}", json={"founded_year": 1970})
    assert patch.status_code == 200
    assert patch.get_json()["founded_year"] == 1970


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def test_create_stats_full_chain(client):
    """Test bout-en-bout : crée tout ce qu'il faut puis ajoute des stats."""
    club = client.post("/api/clubs", json={"name": "PSG"}).get_json()
    season = client.post("/api/seasons", json={
        "year_label": "2023-2024", "start_year": 2023, "end_year": 2024
    }).get_json()
    comp = client.post("/api/competitions", json={"name": "Ligue 1", "type": "league"}).get_json()
    player = client.post("/api/players", json={
        "first_name": "K", "last_name": "M", "position": "Forward",
        "current_club_id": club["id"],
    }).get_json()

    response = client.post("/api/stats", json={
        "player_id": player["id"], "club_id": club["id"],
        "season_id": season["id"], "competition_id": comp["id"],
        "goals": 27, "assists": 7, "appearances": 29,
    })
    assert response.status_code == 201
    body = response.get_json()
    assert body["goals"] == 27


def test_create_stats_duplicate_triplet_returns_409(seeded_client):
    """La contrainte UNIQUE (player, season, competition) doit rejeter le doublon."""
    # On récupère une stat existante puis on tente de la recréer
    listing = seeded_client.get("/api/stats").get_json()
    if not listing["items"]:
        return  # impossible à tester si aucune stat
    sample = listing["items"][0]

    response = seeded_client.post("/api/stats", json={
        "player_id": sample["player_id"],
        "season_id": sample["season_id"],
        "competition_id": sample["competition_id"],
        "club_id": sample["club_id"],
        "goals": 99,
    })
    assert response.status_code == 409


def test_upsert_stats(client):
    """L'endpoint /api/stats/upsert doit créer puis mettre à jour."""
    club = client.post("/api/clubs", json={"name": "Real"}).get_json()
    season = client.post("/api/seasons", json={
        "year_label": "2024-2025", "start_year": 2024, "end_year": 2025
    }).get_json()
    comp = client.post("/api/competitions", json={"name": "La Liga"}).get_json()
    player = client.post("/api/players", json={"first_name": "V", "last_name": "J"}).get_json()

    payload = {
        "player_id": player["id"], "club_id": club["id"],
        "season_id": season["id"], "competition_id": comp["id"],
        "goals": 10, "assists": 5,
    }
    first = client.put("/api/stats/upsert", json=payload)
    assert first.status_code == 201

    payload["goals"] = 25
    second = client.put("/api/stats/upsert", json=payload)
    assert second.status_code == 200
    assert second.get_json()["goals"] == 25


def test_modify_stats_via_patch(seeded_client):
    listing = seeded_client.get("/api/stats").get_json()
    if not listing["items"]:
        return
    sid = listing["items"][0]["id"]

    response = seeded_client.patch(f"/api/stats/{sid}", json={"goals": 99})
    assert response.status_code == 200
    assert response.get_json()["goals"] == 99


def test_delete_stats(seeded_client):
    listing = seeded_client.get("/api/stats").get_json()
    if not listing["items"]:
        return
    sid = listing["items"][0]["id"]

    delete = seeded_client.delete(f"/api/stats/{sid}")
    assert delete.status_code == 204

    get_after = seeded_client.get(f"/api/stats/{sid}")
    assert get_after.status_code == 404


# ---------------------------------------------------------------------------
# Saisons
# ---------------------------------------------------------------------------

def test_create_season_invalid_year_range_returns_400(client):
    response = client.post("/api/seasons", json={
        "year_label": "BAD", "start_year": 2025, "end_year": 2024
    })
    assert response.status_code == 400
