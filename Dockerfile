# =============================================================
# FootStats API - Dockerfile
# Image Python slim, utilisateur non-root, dépendances cachées,
# point d'entrée Gunicorn pour la production (override en dev).
# =============================================================

FROM python:3.12-slim

# ----- Variables d'environnement Python -----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ----- Dépendances système minimales -----
# default-libmysqlclient-dev : utile si on bascule un jour sur mysqlclient.
# curl : pratique pour le healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# ----- Répertoire de travail -----
WORKDIR /app

# ----- Installation des dépendances Python (cache layer) -----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ----- Copie du code applicatif -----
COPY . .

# ----- Utilisateur non-root pour la sécurité -----
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# ----- Exposition du port HTTP -----
EXPOSE 5000

# ----- Healthcheck applicatif -----
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:5000/api/health || exit 1

# ----- Commande de démarrage (production) -----
# En développement, docker-compose surcharge cette commande pour activer
# l'auto-reload de Flask.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--access-logfile", "-", "wsgi:app"]
