"""
Point d'entrée WSGI de l'application FootStats API.

Utilisé par :
    - Gunicorn en production (`gunicorn wsgi:app`)
    - Flask CLI en développement (`flask run`)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Permet de lancer directement le serveur de dev avec `python wsgi.py`.
    app.run(host="0.0.0.0", port=5000, debug=True)
