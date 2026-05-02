"""Schémas Marshmallow pour Season."""
from marshmallow import validates_schema, ValidationError as MaValidationError

from app.extensions import ma
from app.models.season import Season


class SeasonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Season
        load_instance = True
        include_fk = True
        ordered = True
        dump_only = ("id", "created_at", "updated_at")

    @validates_schema
    def validate_year_range(self, data, **kwargs):
        """Assure que end_year >= start_year (côté applicatif)."""
        start = data.get("start_year")
        end = data.get("end_year")
        if start is not None and end is not None and end < start:
            raise MaValidationError(
                {"end_year": ["end_year doit être >= start_year"]}
            )


season_schema = SeasonSchema()
seasons_schema = SeasonSchema(many=True)
