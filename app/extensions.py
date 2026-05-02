"""
Instanciation centralisée des extensions Flask.

Les objets sont créés ici sans application attachée.
La fonction `create_app()` les liera ensuite via `init_app(app)`.

Ce pattern évite les imports circulaires entre les modèles et la factory.
"""
from pathlib import Path

import yaml
from flasgger import Swagger
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# ORM
db = SQLAlchemy()

# Migrations Alembic
migrate = Migrate()

# Sérialisation / validation
ma = Marshmallow()

# CORS pour le frontend local
cors = CORS()

# ----- Swagger : on charge la spec OpenAPI depuis le YAML -----
_OPENAPI_PATH = Path(__file__).resolve().parent / "docs" / "openapi.yaml"

if _OPENAPI_PATH.exists():
    with open(_OPENAPI_PATH, "r", encoding="utf-8") as fh:
        _spec = yaml.safe_load(fh)
else:
    _spec = {"openapi": "3.0.3", "info": {"title": "FootStats API", "version": "0.0.0"}}

swagger = Swagger(template=_spec, config={
    "headers": [],
    "specs": [{"endpoint": "apispec_1", "route": "/apispec_1.json",
               "rule_filter": lambda rule: True, "model_filter": lambda tag: True}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
})
