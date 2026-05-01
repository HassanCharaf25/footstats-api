"""
Instanciation centralisée des extensions Flask.

Les objets sont créés ici sans application attachée.
La fonction `create_app()` les liera ensuite via `init_app(app)`.

Ce pattern évite les imports circulaires entre les modèles et la factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flasgger import Swagger

# ORM
db = SQLAlchemy()

# Migrations Alembic
migrate = Migrate()

# Sérialisation / validation
ma = Marshmallow()

# CORS pour le frontend local
cors = CORS()

# Documentation Swagger interactive
swagger = Swagger()
