"""
Blueprint utilitaire.

Endpoints :
    POST /api/import/sample-data     -> import du jeu de données de démo
                                        (équivalent HTTP de `flask seed`).
    GET  /api/db/stats               -> stats globales sur la base
                                        (utile pour la soutenance).
"""
from flask import Blueprint, jsonify

from app.extensions import db
from app.models import (
    Club, Competition, Player, PlayerProfile, PlayerSeasonStats, Season,
)

utils_bp = Blueprint("utils", __name__)


@utils_bp.route("/import/sample-data", methods=["POST"])
def import_sample_data():
    """Lance le seed depuis HTTP. Idempotent."""
    from seed.seed_data import seed_database
    counters = seed_database(verbose=False)
    return jsonify({
        "status": "ok",
        "message": "Données de démo importées avec succès.",
        "created": counters,
    }), 201


@utils_bp.route("/db/stats", methods=["GET"])
def db_stats():
    """Compteurs globaux par table."""
    return jsonify({
        "clubs": db.session.query(Club).count(),
        "seasons": db.session.query(Season).count(),
        "competitions": db.session.query(Competition).count(),
        "players": db.session.query(Player).count(),
        "player_profiles": db.session.query(PlayerProfile).count(),
        "player_season_stats": db.session.query(PlayerSeasonStats).count(),
    }), 200
