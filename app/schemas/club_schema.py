"""
Schémas Marshmallow pour Club.

`SQLAlchemyAutoSchema` génère automatiquement les champs depuis le modèle.
- `load_instance=True`  : `schema.load(data)` retourne directement un objet Club.
- `include_fk=True`     : expose les FK (utile pour les sous-ressources).
- `ordered=True`        : conserve l'ordre des champs dans la sortie JSON.
"""
from app.extensions import ma
from app.models.club import Club


class ClubSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Club
        load_instance = True
        include_fk = True
        ordered = True
        # Champs en lecture seule : générés par la base, ne doivent pas
        # arriver dans le payload d'entrée.
        dump_only = ("id", "created_at", "updated_at")


# Instances réutilisables (pattern recommandé pour la perf).
club_schema = ClubSchema()
clubs_schema = ClubSchema(many=True)
