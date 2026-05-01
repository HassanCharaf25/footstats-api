"""
Application factory de FootStats API.

Le pattern factory permet :
    - d'instancier plusieurs applications (utile en tests),
    - d'appliquer dynamiquement la configuration,
    - d'éviter les imports circulaires,
    - de structurer proprement l'enregistrement des extensions et blueprints.
"""
from flask import Flask, jsonify, send_from_directory
from pathlib import Path

from app.config import get_config
from app.extensions import db, migrate, ma, cors, swagger
from app.errors import register_error_handlers


def create_app(config_class=None) -> Flask:
    """
    Crée et configure une instance Flask.

    Args:
        config_class: classe de configuration optionnelle (utile en tests).

    Returns:
        Application Flask prête à être servie.
    """
    # Le frontend statique est servi depuis /frontend
    project_root = Path(__file__).resolve().parent.parent
    frontend_dir = project_root / "frontend"
    static_dir = project_root / "static"

    app = Flask(
        __name__,
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    # ----- Configuration -----
    app.config.from_object(config_class or get_config())

    # ----- Extensions -----
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    swagger.init_app(app)

    # ----- Modèles (import après init pour enregistrer les tables) -----
    # L'import déclenche l'enregistrement des modèles dans db.metadata,
    # ce qui permet à Flask-Migrate de générer correctement les migrations.
    from app import models  # noqa: F401

    # ----- Blueprints -----
    # NOTE : à décommenter au fur et à mesure.
    # from app.routes.players_bp import players_bp
    # from app.routes.clubs_bp import clubs_bp
    # from app.routes.seasons_bp import seasons_bp
    # from app.routes.competitions_bp import competitions_bp
    # from app.routes.stats_bp import stats_bp
    # from app.routes.utils_bp import utils_bp
    # app.register_blueprint(players_bp, url_prefix="/api/players")
    # app.register_blueprint(clubs_bp, url_prefix="/api/clubs")
    # app.register_blueprint(seasons_bp, url_prefix="/api/seasons")
    # app.register_blueprint(competitions_bp, url_prefix="/api/competitions")
    # app.register_blueprint(stats_bp, url_prefix="/api/stats")
    # app.register_blueprint(utils_bp, url_prefix="/api")

    # ----- Gestion d'erreurs JSON -----
    register_error_handlers(app)

    # ----- Routes minimales (en attendant les blueprints) -----
    @app.route("/api/health", methods=["GET"])
    def health():
        """Endpoint de healthcheck. Utilisé par Docker et le monitoring."""
        return jsonify({
            "status": "ok",
            "service": "FootStats API",
            "version": "0.1.0",
        }), 200

    @app.route("/", methods=["GET"])
    def index():
        """Sert la page principale du frontend si présente."""
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return send_from_directory(str(frontend_dir), "index.html")
        return jsonify({
            "service": "FootStats API",
            "message": "Bienvenue. Voir /api/docs pour la documentation.",
        }), 200

    @app.route("/frontend/<path:filename>", methods=["GET"])
    def frontend_assets(filename):
        """Sert les fichiers statiques du frontend (CSS, JS)."""
        return send_from_directory(str(frontend_dir), filename)

    # Hook utile au debug : log des routes au démarrage en mode debug
    if app.config.get("DEBUG"):
        with app.app_context():
            app.logger.info("Routes enregistrées :")
            for rule in app.url_map.iter_rules():
                app.logger.info("  %s -> %s", rule.rule, rule.endpoint)

    return app