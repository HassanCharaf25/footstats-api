"""
Helpers partagés entre les blueprints REST.

Ces utilitaires factorisent les patterns récurrents :
    - récupération paginée d'une ressource ;
    - chargement d'un payload Marshmallow avec gestion des erreurs ;
    - commit défensif convertissant les erreurs d'intégrité en 409.
"""
from typing import Type

from flask import request
from marshmallow import ValidationError as MaValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.errors import ConflictError, ValidationError


def get_pagination_args() -> tuple[int, int]:
    """Lit `?page=&per_page=` avec des bornes raisonnables."""
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = max(request.args.get("per_page", 20, type=int), 1)
    per_page = min(per_page, 100)
    return page, per_page


def paginate_response(query, schema_many, page: int, per_page: int) -> dict:
    """Retourne un dict standard pour les listes paginées."""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": schema_many.dump(pagination.items),
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def load_or_400(schema, data, **kwargs):
    """
    Charge `data` via `schema.load(...)` et convertit les erreurs Marshmallow
    en `ValidationError` (400) gérée par le handler global JSON.
    """
    try:
        return schema.load(data, **kwargs)
    except MaValidationError as err:
        raise ValidationError(message=str(err.messages))


def commit_or_409(message: str = "Conflit avec une ressource existante."):
    """Commit la session ou lève un 409 propre en cas d'IntegrityError."""
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError(message=message)


def get_or_404(model: Type, obj_id: int, exc_class):
    """Récupère un objet par son ID ou lève une exception métier 404."""
    obj = db.session.get(model, obj_id)
    if obj is None:
        raise exc_class(message=f"{model.__name__} #{obj_id} introuvable.")
    return obj
