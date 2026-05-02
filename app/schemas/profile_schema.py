"""Schémas Marshmallow pour PlayerProfile."""
from marshmallow import validate

from app.extensions import ma
from app.models.player_profile import PlayerProfile


class PlayerProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PlayerProfile
        load_instance = True
        include_fk = True
        ordered = True
        dump_only = ("id", "created_at", "updated_at")

    # Surcharge pour ajouter des validateurs Marshmallow (au-delà du CHECK SQL).
    preferred_foot = ma.String(
        validate=validate.OneOf(["Left", "Right", "Both"]),
        allow_none=True,
    )
    height_cm = ma.Integer(validate=validate.Range(min=100, max=250), allow_none=True)
    weight_kg = ma.Integer(validate=validate.Range(min=30, max=200), allow_none=True)
    jersey_number = ma.Integer(validate=validate.Range(min=1, max=99), allow_none=True)


profile_schema = PlayerProfileSchema()
