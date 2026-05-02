"""Blueprint Seasons — CRUD complet."""
from flask import Blueprint, jsonify, request

from app.errors import SeasonNotFound
from app.extensions import db
from app.models.season import Season
from app.routes._helpers import (
    commit_or_409,
    get_or_404,
    get_pagination_args,
    load_or_400,
    paginate_response,
)
from app.schemas.season_schema import season_schema, seasons_schema

seasons_bp = Blueprint("seasons", __name__)


@seasons_bp.route("", methods=["GET"])
def list_seasons():
    page, per_page = get_pagination_args()
    query = Season.query.order_by(Season.start_year.desc())
    return jsonify(paginate_response(query, seasons_schema, page, per_page)), 200


@seasons_bp.route("/<int:season_id>", methods=["GET"])
def get_season(season_id: int):
    season = get_or_404(Season, season_id, SeasonNotFound)
    return jsonify(season_schema.dump(season)), 200


@seasons_bp.route("", methods=["POST"])
def create_season():
    new_season = load_or_400(season_schema, request.get_json() or {})
    db.session.add(new_season)
    commit_or_409(message="Cette saison existe déjà.")
    return jsonify(season_schema.dump(new_season)), 201


@seasons_bp.route("/<int:season_id>", methods=["PUT"])
def replace_season(season_id: int):
    season = get_or_404(Season, season_id, SeasonNotFound)
    load_or_400(season_schema, request.get_json() or {}, instance=season)
    commit_or_409(message="Cette saison existe déjà.")
    return jsonify(season_schema.dump(season)), 200


@seasons_bp.route("/<int:season_id>", methods=["PATCH"])
def update_season(season_id: int):
    season = get_or_404(Season, season_id, SeasonNotFound)
    load_or_400(season_schema, request.get_json() or {}, instance=season, partial=True)
    commit_or_409(message="Cette saison existe déjà.")
    return jsonify(season_schema.dump(season)), 200


@seasons_bp.route("/<int:season_id>", methods=["DELETE"])
def delete_season(season_id: int):
    season = get_or_404(Season, season_id, SeasonNotFound)
    db.session.delete(season)
    commit_or_409(
        message="Impossible de supprimer cette saison : des statistiques y sont rattachées."
    )
    return "", 204
