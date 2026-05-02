"""Blueprint Competitions — CRUD complet."""
from flask import Blueprint, jsonify, request

from app.errors import NotFoundError
from app.extensions import db
from app.models.competition import Competition
from app.routes._helpers import (
    commit_or_409,
    get_or_404,
    get_pagination_args,
    load_or_400,
    paginate_response,
)
from app.schemas.competition_schema import competition_schema, competitions_schema


class CompetitionNotFound(NotFoundError):
    error_name = "CompetitionNotFound"


competitions_bp = Blueprint("competitions", __name__)


@competitions_bp.route("", methods=["GET"])
def list_competitions():
    page, per_page = get_pagination_args()
    query = Competition.query.order_by(Competition.name.asc())
    return jsonify(paginate_response(query, competitions_schema, page, per_page)), 200


@competitions_bp.route("/<int:comp_id>", methods=["GET"])
def get_competition(comp_id: int):
    comp = get_or_404(Competition, comp_id, CompetitionNotFound)
    return jsonify(competition_schema.dump(comp)), 200


@competitions_bp.route("", methods=["POST"])
def create_competition():
    new_comp = load_or_400(competition_schema, request.get_json() or {})
    db.session.add(new_comp)
    commit_or_409(message="Cette compétition existe déjà.")
    return jsonify(competition_schema.dump(new_comp)), 201


@competitions_bp.route("/<int:comp_id>", methods=["PUT"])
def replace_competition(comp_id: int):
    comp = get_or_404(Competition, comp_id, CompetitionNotFound)
    load_or_400(competition_schema, request.get_json() or {}, instance=comp)
    commit_or_409(message="Cette compétition existe déjà.")
    return jsonify(competition_schema.dump(comp)), 200


@competitions_bp.route("/<int:comp_id>", methods=["PATCH"])
def update_competition(comp_id: int):
    comp = get_or_404(Competition, comp_id, CompetitionNotFound)
    load_or_400(
        competition_schema, request.get_json() or {}, instance=comp, partial=True
    )
    commit_or_409(message="Cette compétition existe déjà.")
    return jsonify(competition_schema.dump(comp)), 200


@competitions_bp.route("/<int:comp_id>", methods=["DELETE"])
def delete_competition(comp_id: int):
    comp = get_or_404(Competition, comp_id, CompetitionNotFound)
    db.session.delete(comp)
    commit_or_409(
        message="Impossible de supprimer cette compétition : des statistiques y sont rattachées."
    )
    return "", 204
