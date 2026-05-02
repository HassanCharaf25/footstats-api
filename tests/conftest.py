"""
Fixtures pytest partagées par tous les tests.

Une nouvelle base SQLite en mémoire est créée pour chaque test, ce qui
garantit l'isolation totale et un temps d'exécution très rapide.
"""
import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db


@pytest.fixture()
def app():
    """Instance d'application Flask configurée pour les tests."""
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Client HTTP Flask pour envoyer des requêtes à l'app."""
    return app.test_client()


@pytest.fixture()
def seeded_app(app):
    """Application avec le jeu de données de démo importé."""
    from seed.seed_data import seed_database
    seed_database(verbose=False)
    return app


@pytest.fixture()
def seeded_client(seeded_app):
    return seeded_app.test_client()
