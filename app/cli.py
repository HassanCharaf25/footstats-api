"""
Commandes CLI personnalisées exposées via `flask <command>`.

Disponibles :
    flask seed   -> remplit la base avec le jeu de données de démo
    flask reset  -> supprime toutes les lignes des tables (sans toucher au schéma)
"""
import click
from flask import Flask
from flask.cli import with_appcontext

from app.extensions import db


def register_cli(app: Flask) -> None:
    """Enregistre les commandes CLI sur l'application."""

    @app.cli.command("seed")
    @with_appcontext
    def seed_cmd():
        """Remplit la base avec le jeu de données de démo."""
        from seed.seed_data import seed_database
        result = seed_database(verbose=True)
        click.echo(f"OK : {result}")

    @app.cli.command("reset")
    @click.confirmation_option(prompt="Confirmer la suppression de toutes les données ?")
    @with_appcontext
    def reset_cmd():
        """Vide toutes les tables (sans toucher au schéma)."""
        from app.models import (
            PlayerSeasonStats, PlayerProfile, Player, Club, Season, Competition,
        )
        # Ordre important : d'abord les tables qui dépendent des autres.
        for model in (PlayerSeasonStats, PlayerProfile, Player, Club, Season, Competition):
            count = db.session.query(model).delete()
            click.echo(f"  {model.__tablename__:25s} -> {count} lignes supprimées")
        db.session.commit()
        click.echo("Base vidée.")
