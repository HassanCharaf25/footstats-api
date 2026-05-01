"""
Gestion centralisée des erreurs de l'API.

Toutes les erreurs (HTTP standards + exceptions métier) sont
sérialisées au format JSON cohérent :

    {
        "error": "<NomDeLerreur>",
        "message": "<message lisible>",
        "status": <code HTTP>
    }
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


# ---------------------------------------------------------------------------
# Exceptions métier
# ---------------------------------------------------------------------------

class APIError(Exception):
    """Exception de base pour toutes les erreurs métier de l'API."""

    status_code = 500
    error_name = "InternalError"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        super().__init__(message or self.__class__.__name__)
        self.message = message or "Une erreur est survenue."
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            "error": self.error_name,
            "message": self.message,
            "status": self.status_code,
        }


class NotFoundError(APIError):
    status_code = 404
    error_name = "NotFound"


class ValidationError(APIError):
    status_code = 400
    error_name = "ValidationError"


class ConflictError(APIError):
    status_code = 409
    error_name = "Conflict"


class PlayerNotFound(NotFoundError):
    error_name = "PlayerNotFound"


class SeasonNotFound(NotFoundError):
    error_name = "SeasonNotFound"


class StatsNotFound(NotFoundError):
    error_name = "StatsNotFound"


class ClubNotFound(NotFoundError):
    error_name = "ClubNotFound"


# ---------------------------------------------------------------------------
# Enregistrement des handlers globaux
# ---------------------------------------------------------------------------

def register_error_handlers(app):
    """Attache tous les handlers d'erreurs à l'application Flask."""

    @app.errorhandler(APIError)
    def handle_api_error(err: APIError):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({
            "error": "BadRequest",
            "message": getattr(err, "description", "Requête mal formée."),
            "status": 400,
        }), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({
            "error": "NotFound",
            "message": getattr(err, "description", "Ressource introuvable."),
            "status": 404,
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify({
            "error": "MethodNotAllowed",
            "message": getattr(err, "description", "Méthode HTTP non autorisée."),
            "status": 405,
        }), 405

    @app.errorhandler(409)
    def conflict(err):
        return jsonify({
            "error": "Conflict",
            "message": getattr(err, "description", "Conflit avec l'état actuel."),
            "status": 409,
        }), 409

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({
            "error": "InternalServerError",
            "message": "Une erreur interne est survenue.",
            "status": 500,
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        # Filet de sécurité pour toute autre erreur HTTP non capturée ci-dessus.
        return jsonify({
            "error": err.name.replace(" ", ""),
            "message": err.description,
            "status": err.code,
        }), err.code
