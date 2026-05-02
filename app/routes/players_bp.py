"""
Blueprint Players — CRUD + recherche + sous-ressources profil et stats.

Endpoints :
    GET    /api/players                       -> liste paginée
    GET    /api/players/search?name=&club=    -> recherche multi-critères
    POST   /api/players                       -> création
    GET    /api/players/<id>                  -> fiche complète
    PUT    /api/players/<id>                  -> remplacement
    PATCH  /api/players/<id>                  -> mise à jour partielle
    DELETE /api/players/<id>                  -> suppression

    GET    /api/players/<id>/profile          -> récupère le profil détaillé
    PUT    /api/players/<id>/profile          -> upsert du profil
    PATCH  /api/players/<id>/profile          -> mise à jour partielle

    GET    /api/players/<id>/stats            -> toutes les stats
    GET    /api/players/<id>/stats?season=... -> stats filtrées par saison
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.errors import PlayerNotFound, ValidationError
from app.extensions import db
from app.models.club import Club
from app.models.player import Player
from app.models.player_profile import PlayerProfile
from app.models.player_season_stats import PlayerSeasonStats
from app.models.season import Season
from app.routes._helpers import (
    commit_or_409,
    get_or_404,
    get_pagination_args,
    load_or_400,
    paginate_response,
)
from app.schemas.player_schema import player_schema, players_schema
from app.schemas.profile_schema import profile_schema
from app.schemas.stats_schema import stats_list_schema

players_bp = Blueprint("players", __name__)


# ---------------------------------------------------------------------------
# Liste / recherche / création
# ---------------------------------------------------------------------------

@players_bp.route("", methods=["GET"])
def list_players():
    page, per_page = get_pagination_args()
    query = Player.query.order_by(Player.last_name.asc(), Player.first_name.asc())
    return jsonify(paginate_response(query, players_schema, page, per_page)), 200


@players_bp.route("/search", methods=["GET"])
def search_players():
    """
    Recherche multi-critères :
        - name      : recherche LIKE sur first_name OU last_name
        - club      : recherche LIKE sur le nom du club courant
        - position  : égalité stricte
        - nationality : égalité stricte
    """
    name = request.args.get("name", type=str)
    club = request.args.get("club", type=str)
    position = request.args.get("position", type=str)
    nationality = request.args.get("nationality", type=str)

    query = Player.query

    if name:
        like = f"%{name}%"
        query = query.filter(or_(Player.first_name.ilike(like), Player.last_name.ilike(like)))
    if club:
        query = query.join(Club, Player.current_club_id == Club.id).filter(
            Club.name.ilike(f"%{club}%")
        )
    if position:
        query = query.filter(Player.position == position)
    if nationality:
        query = query.filter(Player.nationality == nationality)

    page, per_page = get_pagination_args()
    query = query.order_by(Player.last_name.asc(), Player.first_name.asc())
    return jsonify(paginate_response(query, players_schema, page, per_page)), 200


@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    return jsonify(player_schema.dump(player)), 200


@players_bp.route("", methods=["POST"])
def create_player():
    new_player = load_or_400(player_schema, request.get_json() or {})
    db.session.add(new_player)
    commit_or_409(message="Conflit : ce joueur existe déjà ou un FK est invalide.")
    return jsonify(player_schema.dump(new_player)), 201


@players_bp.route("/<int:player_id>", methods=["PUT"])
def replace_player(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    load_or_400(player_schema, request.get_json() or {}, instance=player)
    commit_or_409()
    return jsonify(player_schema.dump(player)), 200


@players_bp.route("/<int:player_id>", methods=["PATCH"])
def update_player(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    load_or_400(player_schema, request.get_json() or {}, instance=player, partial=True)
    commit_or_409()
    return jsonify(player_schema.dump(player)), 200


@players_bp.route("/<int:player_id>", methods=["DELETE"])
def delete_player(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    db.session.delete(player)
    commit_or_409()
    return "", 204


# ---------------------------------------------------------------------------
# Sous-ressource : Profile (relation One-to-One)
# ---------------------------------------------------------------------------

@players_bp.route("/<int:player_id>/profile", methods=["GET"])
def get_player_profile(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    if player.profile is None:
        raise PlayerNotFound(message=f"Aucun profil pour le joueur #{player_id}.")
    return jsonify(profile_schema.dump(player.profile)), 200


@players_bp.route("/<int:player_id>/profile", methods=["PUT"])
def upsert_player_profile(player_id: int):
    """Crée le profil s'il n'existe pas, le remplace sinon."""
    player = get_or_404(Player, player_id, PlayerNotFound)
    payload = request.get_json() or {}
    payload["player_id"] = player_id  # garantit la cohérence

    if player.profile is None:
        new_profile = load_or_400(profile_schema, payload)
        db.session.add(new_profile)
        status = 201
        result = new_profile
    else:
        load_or_400(profile_schema, payload, instance=player.profile)
        status = 200
        result = player.profile

    commit_or_409(message="Conflit : un profil existe déjà pour ce joueur.")
    return jsonify(profile_schema.dump(result)), status


@players_bp.route("/<int:player_id>/profile", methods=["PATCH"])
def patch_player_profile(player_id: int):
    player = get_or_404(Player, player_id, PlayerNotFound)
    if player.profile is None:
        raise PlayerNotFound(message=f"Aucun profil pour le joueur #{player_id}.")
    payload = request.get_json() or {}
    payload.pop("player_id", None)  # immuable
    load_or_400(profile_schema, payload, instance=player.profile, partial=True)
    commit_or_409()
    return jsonify(profile_schema.dump(player.profile)), 200


# ---------------------------------------------------------------------------
# Sous-ressource : Stats du joueur
# ---------------------------------------------------------------------------

@players_bp.route("/<int:player_id>/stats", methods=["GET"])
def get_player_stats(player_id: int):
    """Retourne toutes les stats du joueur, filtrables par saison via ?season=label."""
    player = get_or_404(Player, player_id, PlayerNotFound)

    query = PlayerSeasonStats.query.filter_by(player_id=player.id)

    season_label = request.args.get("season", type=str)
    if season_label:
        season = Season.query.filter_by(year_label=season_label).first()
        if season is None:
            # On retourne une liste vide plutôt qu'un 404 pour faciliter le frontend.
            return jsonify({"items": [], "season": season_label, "found": False}), 200
        query = query.filter_by(season_id=season.id)

    stats = query.all()
    return jsonify(stats_list_schema.dump(stats)), 200
