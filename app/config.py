"""
Configuration de l'application FootStats API.

Trois profils :
    - DevelopmentConfig : développement local (Docker Compose).
    - TestingConfig    : tests pytest, base SQLite en mémoire.
    - ProductionConfig : exécution en production (image Docker publiée).

Le profil est sélectionné via la variable d'environnement FLASK_ENV.
"""
import os
from datetime import timedelta


class BaseConfig:
    """Configuration commune à tous les environnements."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JSON_SORT_KEYS = False

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,  # < wait_timeout MySQL par défaut (8h, mais on reste prudent)
    }

    # Swagger / API doc
    SWAGGER = {
        "title": "FootStats API",
        "uiversion": 3,
        "specs_route": "/api/docs/",
    }

    # Pagination par défaut
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(BaseConfig):
    """Développement local : verbeux, base MySQL conteneurisée."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://footuser:footpass@db:3306/footstats",
    )
    SQLALCHEMY_ECHO = False  # passe à True pour voir les requêtes SQL


class TestingConfig(BaseConfig):
    """Tests automatisés : SQLite en mémoire, isolé de la base réelle."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production : pas de debug, secrets exclusivement via variables d'env."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        # Vérifications de garde-fous au démarrage en prod.
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("DATABASE_URL doit être défini en production.")
        if app.config["SECRET_KEY"] in (None, "change-me"):
            raise RuntimeError("SECRET_KEY doit être défini en production.")


# Mapping FLASK_ENV -> classe de config
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Retourne la classe de configuration adaptée au FLASK_ENV courant."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)
