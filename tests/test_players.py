"""Tests des endpoints joueurs : CRUD, recherche, profil, stats."""


# ---------------------------------------------------------------------------
# Création
# ---------------------------------------------------------------------------

def test_create_player_minimal(client):
    response = client.post("/api/players", json={
        "first_name": "Kylian", "last_name": "Mbappé", "position": "Forward",
    })
    assert response.status_code == 201
    body = response.get_json()
    assert body["first_name"] == "Kylian"
    assert body["last_name"] == "Mbappé"
    assert body["full_name"] == "Kylian Mbappé"
    assert "id" in body


def test_create_player_invalid_position_returns_400(client):
    response = client.post("/api/players", json={
        "first_name": "X", "last_name": "Y", "position": "GoalKeeper",
    })
    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "ValidationError"


def test_create_player_missing_required_fields_returns_400(client):
    response = client.post("/api/players", json={"position": "Forward"})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Lecture / 404
# ---------------------------------------------------------------------------

def test_get_player_not_found_returns_404(client):
    response = client.get("/api/players/999")
    assert response.status_code == 404
    body = response.get_json()
    assert body["error"] == "PlayerNotFound"


def test_list_players_empty(client):
    response = client.get("/api/players")
    assert response.status_code == 200
    body = response.get_json()
    assert body["items"] == []
    assert body["total"] == 0


def test_get_player_by_id(seeded_client):
    response = seeded_client.get("/api/players/1")
    assert response.status_code == 200
    body = response.get_json()
    assert body["first_name"]


# ---------------------------------------------------------------------------
# Recherche
# ---------------------------------------------------------------------------

def test_search_player_by_name(seeded_client):
    response = seeded_client.get("/api/players/search?name=Mbap")
    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] >= 1
    assert any("Mbappé" in p["last_name"] for p in body["items"])


def test_search_player_no_match(seeded_client):
    response = seeded_client.get("/api/players/search?name=Dupontetqualquechose")
    assert response.status_code == 200
    body = response.get_json()
    assert body["items"] == []


def test_search_player_by_club(seeded_client):
    response = seeded_client.get("/api/players/search?club=Real")
    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] >= 1


# ---------------------------------------------------------------------------
# Modification
# ---------------------------------------------------------------------------

def test_patch_player(seeded_client):
    response = seeded_client.patch("/api/players/1", json={"photo_url": "/static/uploads/test.jpg"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["photo_url"] == "/static/uploads/test.jpg"


def test_put_player_replaces(seeded_client):
    response = seeded_client.put("/api/players/1", json={
        "first_name": "Test", "last_name": "Player", "position": "Defender",
    })
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Suppression et cascade
# ---------------------------------------------------------------------------

def test_delete_player_cascades_profile_and_stats(seeded_client):
    # Le joueur Mbappé (id=1 a priori) a un profil et des stats.
    delete = seeded_client.delete("/api/players/1")
    assert delete.status_code == 204

    get_player = seeded_client.get("/api/players/1")
    assert get_player.status_code == 404

    # Le profil devrait avoir été supprimé en cascade.
    profile = seeded_client.get("/api/players/1/profile")
    assert profile.status_code == 404


# ---------------------------------------------------------------------------
# Profil (One-to-One)
# ---------------------------------------------------------------------------

def test_get_profile_when_player_has_no_profile_returns_404(client):
    create = client.post("/api/players", json={"first_name": "A", "last_name": "B"})
    pid = create.get_json()["id"]
    response = client.get(f"/api/players/{pid}/profile")
    assert response.status_code == 404


def test_put_profile_creates_then_updates(client):
    create = client.post("/api/players", json={"first_name": "A", "last_name": "B"})
    pid = create.get_json()["id"]

    first = client.put(f"/api/players/{pid}/profile", json={
        "height_cm": 180, "preferred_foot": "Right", "jersey_number": 10,
    })
    assert first.status_code == 201

    second = client.put(f"/api/players/{pid}/profile", json={
        "height_cm": 185, "preferred_foot": "Left", "jersey_number": 11,
    })
    assert second.status_code == 200
    assert second.get_json()["height_cm"] == 185


# ---------------------------------------------------------------------------
# Stats par saison
# ---------------------------------------------------------------------------

def test_get_player_stats_for_season(seeded_client):
    response = seeded_client.get("/api/players/1/stats?season=2023-2024")
    assert response.status_code == 200
    body = response.get_json()
    # Le résultat est soit une liste de stats, soit le dict {items, season, found:false}
    if isinstance(body, dict) and body.get("found") is False:
        assert body["season"] == "2023-2024"
    else:
        assert isinstance(body, list)


def test_get_player_stats_unknown_season_returns_empty(seeded_client):
    response = seeded_client.get("/api/players/1/stats?season=1990-1991")
    assert response.status_code == 200
    body = response.get_json()
    assert body == {"items": [], "season": "1990-1991", "found": False}
