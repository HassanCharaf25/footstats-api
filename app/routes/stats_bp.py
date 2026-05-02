"""
Blueprint Stats — CRUD sur les statistiques individuelles.

Endpoints :
    GET    /api/stats                -> liste paginée
    POST   /api/stats                -> création
    GET    /api/stats/<id>           -> détail
    PUT    /api/stats/<id>           -> remplacement
    PATCH  /api/stats/<id>           -> mise à jour partielle
    DELETE /api/stats/<id>           -> suppression
    PUT    /api/stats/upsert         -> crée OU met à jour la stat
                                        identifiée par (player_id, season_id, competition_id).
"""
from flask import Blueprint, jsonify, request

from app.errors import StatsNotFound, ValidationError
from app.extensions import db
from app.models.player_season_stats import PlayerSeasonStats
from app.routes._helpers import (
    commit_or_409,
    get_or_404,
    get_pagination_args,
    load_or_400,
    paginate_response,
)
from app.schemas.stats_schema import stats_list_schema, stats_schema

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("", methods=["GET"])
def list_stats():
    page, per_page = get_pagination_args()
    query = PlayerSeasonStats.query.order_by(PlayerSeasonStats.id.desc())
    return jsonify(paginate_response(query, stats_list_schema, page, per_page)), 200


@stats_bp.route("/<int:stats_id>", methods=["GET"])
def get_stats(stats_id: int):
    stats = get_or_404(PlayerSeasonStats, stats_id, StatsNotFound)
    return jsonify(stats_schema.dump(stats)), 200


@stats_bp.route("", methods=["POST"])
def create_stats():
    new_stats = load_or_400(stats_schema, request.get_json() or {})
    db.session.add(new_stats)
    commit_or_409(
        message="Conflit : des stats existent déjà pour ce triplet (joueur, saison, compétition)."
    )
    return jsonify(stats_schema.dump(new_stats)), 201


@stats_bp.route("/<int:stats_id>", methods=["PUT"])
def replace_stats(stats_id: int):
    stats = get_or_404(PlayerSeasonStats, stats_id, StatsNotFound)
    load_or_400(stats_schema, request.get_json() or {}, instance=stats)
    commit_or_409()
    return jsonify(stats_schema.dump(stats)), 200


@stats_bp.route("/<int:stats_id>", methods=["PATCH"])
def update_stats(stats_id: int):
    stats = get_or_404(PlayerSeasonStats, stats_id, StatsNotFound)
    load_or_400(stats_schema, request.get_json() or {}, instance=stats, partial=True)
    commit_or_409()
    return jsonify(stats_schema.dump(stats)), 200


@stats_bp.route("/<int:stats_id>", methods=["DELETE"])
def delete_stats(stats_id: int):
    stats = get_or_404(PlayerSeasonStats, stats_id, StatsNotFound)
    db.session.delete(stats)
    commit_or_409()
    return "", 204


@stats_bp.route("/upsert", methods=["PUT"])
def upsert_stats():
    """
    Crée OU met à jour la ligne de stats identifiée par le triplet
    (player_id, season_id, competition_id).

    Body attendu (JSON) :
        {
            "player_id": 1, "season_id": 2, "competition_id": 1,
            "club_id": 3, "goals": 27, "assists": 7, ...
        }
    """
    data = request.get_json() or {}
    required = ("player_id", "season_id", "competition_id")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValidationError(message=f"Champs requis manquants : {missing}")

    existing = PlayerSeasonStats.query.filter_by(
        player_id=data["player_id"],
        season_id=data["season_id"],
        competition_id=data["competition_id"],
    ).first()

    if existing is None:
        stats = load_or_400(stats_schema, data)
        db.session.add(stats)
        status = 201
    else:
        stats = load_or_400(stats_schema, data, instance=existing)
        status = 200

    commit_or_409()
    return jsonify(stats_schema.dump(stats)), status
