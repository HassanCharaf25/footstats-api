"""Tests des endpoints utilitaires (health, db/stats)."""


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert "FootStats" in body["service"]


def test_db_stats_empty(client):
    response = client.get("/api/db/stats")
    assert response.status_code == 200
    body = response.get_json()
    assert body["players"] == 0
    assert body["clubs"] == 0


def test_db_stats_after_seed(seeded_client):
    response = seeded_client.get("/api/db/stats")
    body = response.get_json()
    assert body["players"] == 6
    assert body["clubs"] == 6
    assert body["seasons"] == 3
    assert body["competitions"] == 6
    assert body["player_season_stats"] >= 18


def test_swagger_doc_accessible(client):
    response = client.get("/api/docs/")
    assert response.status_code in (200, 308)  # 308 = redirect autorisé