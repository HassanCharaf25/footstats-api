"""
Blueprint Clubs — CRUD complet.

Endpoints :
    GET    /api/clubs            -> liste paginée
    POST   /api/clubs            -> création
    GET    /api/clubs/<id>       -> détail
    PUT    /api/clubs/<id>       -> remplacement
    PATCH  /api/clubs/<id>       -> mise à jour partielle
    DELETE /api/clubs/<id>       -> suppression
"""
from flask import Blueprint, jsonify, request

from app.errors import ClubNotFound
from app.extensions import db
from app.models.club import Club
from app.routes._helpers import (
    commit_or_409,
    get_or_404,
    get_pagination_args,
    load_or_400,
    paginate_response,
)
from app.schemas.club_schema import club_schema, clubs_schema

clubs_bp = Blueprint("clubs", __name__)


@clubs_bp.route("", methods=["GET"])
def list_clubs():
    page, per_page = get_pagination_args()
    query = Club.query.order_by(Club.name.asc())
    return jsonify(paginate_response(query, clubs_schema, page, per_page)), 200


@clubs_bp.route("/<int:club_id>", methods=["GET"])
def get_club(club_id: int):
    club = get_or_404(Club, club_id, ClubNotFound)
    return jsonify(club_schema.dump(club)), 200


@clubs_bp.route("", methods=["POST"])
def create_club():
    new_club = load_or_400(club_schema, request.get_json() or {})
    db.session.add(new_club)
    commit_or_409(message="Un club avec ce nom existe déjà.")
    return jsonify(club_schema.dump(new_club)), 201


@clubs_bp.route("/<int:club_id>", methods=["PUT"])
def replace_club(club_id: int):
    club = get_or_404(Club, club_id, ClubNotFound)
    load_or_400(club_schema, request.get_json() or {}, instance=club)
    commit_or_409(message="Un club avec ce nom existe déjà.")
    return jsonify(club_schema.dump(club)), 200


@clubs_bp.route("/<int:club_id>", methods=["PATCH"])
def update_club(club_id: int):
    club = get_or_404(Club, club_id, ClubNotFound)
    load_or_400(club_schema, request.get_json() or {}, instance=club, partial=True)
    commit_or_409(message="Un club avec ce nom existe déjà.")
    return jsonify(club_schema.dump(club)), 200


@clubs_bp.route("/<int:club_id>", methods=["DELETE"])
def delete_club(club_id: int):
    club = get_or_404(Club, club_id, ClubNotFound)
    db.session.delete(club)
    commit_or_409(
        message="Impossible de supprimer ce club : des statistiques y sont rattachées."
    )
    return "", 204
