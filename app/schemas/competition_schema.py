"""Schémas Marshmallow pour Competition."""
from app.extensions import ma
from app.models.competition import Competition


class CompetitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Competition
        load_instance = True
        include_fk = True
        ordered = True
        dump_only = ("id", "created_at", "updated_at")


competition_schema = CompetitionSchema()
competitions_schema = CompetitionSchema(many=True)
