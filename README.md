# ⚽ FootStats API

> **API RESTful conteneurisée** pour consulter et gérer les fiches statistiques de joueurs de football par saison, club et compétition.
> Projet réalisé dans le cadre de la SAE *« Développement & Déploiement d'une Application Web RESTful Conteneurisée »*.

---

## 📋 Sommaire

1. [Présentation](#1-présentation)
2. [Stack technique](#2-stack-technique)
3. [Architecture](#3-architecture)
4. [Modèle relationnel](#4-modèle-relationnel)
5. [Installation et lancement](#5-installation-et-lancement)
6. [Documentation de l'API](#6-documentation-de-lapi)
7. [Exemples d'utilisation (curl)](#7-exemples-dutilisation-curl)
8. [Importer le jeu de données de démo](#8-importer-le-jeu-de-données-de-démo)
9. [Frontend local](#9-frontend-local)
10. [Tests automatisés](#10-tests-automatisés)
11. [Publication sur Docker Hub](#11-publication-sur-docker-hub)
12. [Argumentaire de soutenance](#12-argumentaire-de-soutenance)
13. [Limites et améliorations](#13-limites-et-améliorations)

---

## 1. Présentation

**FootStats API** est une application web complète permettant à un utilisateur de :
- rechercher un joueur de football par nom, club, poste ou nationalité ;
- consulter sa fiche détaillée (identité, photo, profil physique, club actuel) ;
- visualiser ses statistiques pour une saison et une compétition données ;
- créer, modifier et supprimer joueurs, clubs, saisons, compétitions et statistiques via une API REST.

Le projet est entièrement conteneurisé avec Docker Compose (API Flask + base MySQL) et expose une documentation Swagger interactive.

---

## 2. Stack technique

| Couche | Technologie | Version |
|---|---|---|
| Langage | Python | 3.12 |
| Framework web | Flask | 3.0 |
| ORM | SQLAlchemy + Flask-SQLAlchemy | 2.0 / 3.1 |
| Migrations | Flask-Migrate (Alembic) | 4.0 |
| Validation / sérialisation | Marshmallow + flask-marshmallow | 3.22 / 1.2 |
| Documentation | Flasgger (Swagger UI 3) + OpenAPI 3 | 0.9 |
| CORS | Flask-Cors | 4.0 |
| Base de données | MySQL | 8.0 |
| Conteneurisation | Docker + Docker Compose | — |
| Tests | pytest + pytest-flask | 8.3 |
| Serveur prod | Gunicorn | 23 |
| Frontend | HTML / CSS / JavaScript vanilla | — |

---

## 3. Architecture

### Vue d'ensemble

```
┌──────────────────────────────────────────────────────────┐
│                     navigateur (frontend)                │
└───────────────────────┬──────────────────────────────────┘
                        │ HTTP /api/*
┌───────────────────────▼──────────────────────────────────┐
│                Conteneur Docker : api                    │
│  Flask 3 + factory pattern + blueprints REST             │
│  Marshmallow (validation) — Swagger UI                   │
│  SQLAlchemy 2 (ORM, type hints Mapped[...])              │
└───────────────────────┬──────────────────────────────────┘
                        │ mysql+pymysql://
┌───────────────────────▼──────────────────────────────────┐
│                Conteneur Docker : db                     │
│  MySQL 8 + volume persistant footstats_mysql_data        │
└──────────────────────────────────────────────────────────┘
```

### Arborescence

```
footstats-api/
├── app/
│   ├── __init__.py            ← application factory
│   ├── config.py              ← Dev/Test/Prod configurations
│   ├── extensions.py          ← db, ma, migrate, swagger, cors
│   ├── errors.py              ← handlers JSON globaux + exceptions métier
│   ├── cli.py                 ← commandes `flask seed` / `flask reset`
│   ├── models/                ← 6 modèles SQLAlchemy
│   │   ├── _mixins.py
│   │   ├── club.py
│   │   ├── competition.py
│   │   ├── player.py
│   │   ├── player_profile.py
│   │   ├── player_season_stats.py
│   │   └── season.py
│   ├── schemas/               ← schémas Marshmallow (validation + sérialisation)
│   ├── routes/                ← blueprints REST
│   │   ├── _helpers.py
│   │   ├── clubs_bp.py
│   │   ├── competitions_bp.py
│   │   ├── players_bp.py
│   │   ├── seasons_bp.py
│   │   ├── stats_bp.py
│   │   └── utils_bp.py
│   └── docs/openapi.yaml      ← spécification OpenAPI 3
├── frontend/                  ← interface HTML/CSS/JS
│   ├── index.html
│   ├── script.js
│   └── style.css
├── seed/
│   ├── seed_data.py           ← jeu de données de démo (idempotent)
│   └── sample_data.sql        ← équivalent SQL minimal
├── migrations/                ← migrations Alembic (générées)
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_players.py
│   └── test_clubs_and_stats.py
├── static/uploads/            ← photos joueurs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── wsgi.py
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Modèle relationnel

### Schéma

```
            ┌─────────────────┐
            │      Club       │
            │─────────────────│
            │ id (PK)         │
            │ name (UNIQUE)   │
            │ country         │
            │ stadium         │
            └────────┬────────┘
                     │ 1
                     │
                     │ N
            ┌────────▼────────┐  1            1  ┌────────────────────┐
            │     Player      │◄──────────────►│   PlayerProfile    │
            │─────────────────│                │────────────────────│
            │ id (PK)         │                │ id (PK)            │
            │ first_name      │                │ player_id (UNIQUE) │
            │ last_name       │                │ height_cm          │
            │ birth_date      │                │ weight_kg          │
            │ nationality     │                │ preferred_foot     │
            │ position        │                │ jersey_number      │
            │ photo_url       │                │ biography          │
            │ current_club_id │                └────────────────────┘
            └────────┬────────┘
                     │ 1
                     │
                     │ N
        ┌────────────▼─────────────┐  N        1  ┌────────────────┐
        │   PlayerSeasonStats      │◄─────────────│     Season     │
        │──────────────────────────│              │────────────────│
        │ id (PK)                  │              │ id (PK)        │
        │ player_id    (FK)        │              │ year_label (U) │
        │ club_id      (FK)        │              │ start_year     │
        │ season_id    (FK)        │              │ end_year       │
        │ competition_id (FK)      │              └────────────────┘
        │ goals, assists, …        │
        │ UNIQUE(player, season,   │  N        1  ┌────────────────┐
        │        competition)      │◄─────────────│  Competition   │
        └──────────────────────────┘              │────────────────│
                                                  │ id (PK)        │
                                                  │ name (UNIQUE)  │
                                                  │ country, type  │
                                                  └────────────────┘
```

### Les trois relations exigées

| Type | Implémentation |
|---|---|
| **One-to-One** | `Player ↔ PlayerProfile` via FK `player_id` avec contrainte `UNIQUE` dans `player_profiles`, et `relationship(uselist=False, cascade="all, delete-orphan")` côté Player. |
| **One-to-Many** | `Club → Players` via `players.current_club_id` (`ondelete=SET NULL`). `Season → Stats` et `Competition → Stats` via FK avec `ondelete=RESTRICT` pour préserver l'historique. |
| **Many-to-Many** | `Player ↔ Competition` matérialisé par la table d'association enrichie `player_season_stats`. C'est la forme propre d'un Many-to-Many qui porte ses propres données (goals, assists, etc.). |

### Contraintes en base

- `UNIQUE(player_id, season_id, competition_id)` sur `player_season_stats` — empêche les doublons.
- `CHECK` sur les stats positives, sur la cohérence `end_year >= start_year`, sur la taille / le poids / le pied préféré des profils.
- Index composite `ix_players_full_name (last_name, first_name)` pour optimiser la recherche.

---

## 5. Installation et lancement

### Prérequis

- **Docker** ≥ 20.10
- **Docker Compose** ≥ 2.0

### Démarrage en une commande

```bash
git clone <ce-dépôt>
cd footstats-api
cp .env.example .env
docker compose up --build -d
```

### Initialiser la base (première fois uniquement)

```bash
docker compose exec api flask db init
docker compose exec api flask db migrate -m "initial schema"
docker compose exec api flask db upgrade
```

### Importer le jeu de données de démo

```bash
docker compose exec api flask seed
```

### Vérifier que tout marche

```bash
curl http://localhost:5000/api/health
# {"status":"ok","service":"FootStats API","version":"0.1.0"}
```

### Accès aux interfaces

| URL | Description |
|---|---|
| <http://localhost:5000/> | Interface frontend de recherche |
| <http://localhost:5000/api/docs/> | Documentation Swagger interactive |
| <http://localhost:5000/api/health> | Healthcheck |
| <http://localhost:5000/api/db/stats> | Compteurs globaux par table |

### Variables d'environnement (`.env`)

```bash
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=footstats
MYSQL_USER=footuser
MYSQL_PASSWORD=footpass
DATABASE_URL=mysql+pymysql://footuser:footpass@db:3306/footstats
FLASK_ENV=development
FLASK_APP=wsgi.py
SECRET_KEY=change-me-in-production
API_PORT=5000
```

### Commandes utiles

```bash
# Logs
docker compose logs -f api
docker compose logs -f db

# Ouvrir un shell dans le conteneur API
docker compose exec api bash

# Accès direct à MySQL
docker compose exec db mysql -ufootuser -pfootpass footstats

# Tout arrêter
docker compose down

# Tout arrêter ET supprimer le volume MySQL (données perdues)
docker compose down -v
```

---

## 6. Documentation de l'API

Documentation complète et interactive disponible sur **<http://localhost:5000/api/docs/>** une fois le projet lancé.

### Endpoints principaux

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/health` | Healthcheck |
| `GET` | `/api/db/stats` | Compteurs par table |
| `POST` | `/api/import/sample-data` | Import du jeu de données de démo |
| **Joueurs** | | |
| `GET` | `/api/players` | Liste paginée |
| `GET` | `/api/players/search?name=&club=&position=&nationality=` | Recherche multi-critères |
| `GET` | `/api/players/<id>` | Fiche complète (avec profil et club) |
| `POST` | `/api/players` | Création |
| `PUT` | `/api/players/<id>` | Remplacement |
| `PATCH` | `/api/players/<id>` | Modification partielle |
| `DELETE` | `/api/players/<id>` | Suppression (cascade profil + stats) |
| **Profil joueur** | | |
| `GET` | `/api/players/<id>/profile` | Profil détaillé (One-to-One) |
| `PUT` | `/api/players/<id>/profile` | Upsert |
| `PATCH` | `/api/players/<id>/profile` | Modification partielle |
| **Stats joueur** | | |
| `GET` | `/api/players/<id>/stats` | Toutes ses stats |
| `GET` | `/api/players/<id>/stats?season=2023-2024` | Stats filtrées par saison |
| **Clubs / Saisons / Compétitions** | | |
| `GET` `POST` | `/api/clubs`, `/api/seasons`, `/api/competitions` | Listing et création |
| `GET` `PUT` `PATCH` `DELETE` | `/<id>` | CRUD complet |
| **Stats** | | |
| `GET` `POST` | `/api/stats` | Listing et création |
| `GET` `PUT` `PATCH` `DELETE` | `/api/stats/<id>` | CRUD individuel |
| `PUT` | `/api/stats/upsert` | Crée ou met à jour selon le triplet (player, season, competition) |

### Codes HTTP renvoyés

| Code | Signification |
|---|---|
| `200 OK` | Lecture, mise à jour réussie |
| `201 Created` | Ressource créée |
| `204 No Content` | Suppression réussie |
| `400 Bad Request` | Erreur de validation Marshmallow |
| `404 Not Found` | Ressource introuvable (`PlayerNotFound`, `ClubNotFound`, etc.) |
| `409 Conflict` | Doublon UNIQUE ou contrainte FK |
| `500 Internal Server Error` | Erreur inattendue |

Format de réponse d'erreur :

```json
{
    "error": "PlayerNotFound",
    "message": "Player #42 introuvable.",
    "status": 404
}
```

---

## 7. Exemples d'utilisation (curl)

```bash
# 1. Créer un club
curl -X POST http://localhost:5000/api/clubs \
  -H "Content-Type: application/json" \
  -d '{"name":"Real Madrid","country":"Spain","stadium":"Bernabéu"}'

# 2. Créer une saison
curl -X POST http://localhost:5000/api/seasons \
  -H "Content-Type: application/json" \
  -d '{"year_label":"2023-2024","start_year":2023,"end_year":2024}'

# 3. Créer une compétition
curl -X POST http://localhost:5000/api/competitions \
  -H "Content-Type: application/json" \
  -d '{"name":"La Liga","country":"Spain","type":"league"}'

# 4. Créer un joueur
curl -X POST http://localhost:5000/api/players \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Kylian","last_name":"Mbappé","nationality":"France","position":"Forward","current_club_id":1}'

# 5. Ajouter le profil détaillé (One-to-One)
curl -X PUT http://localhost:5000/api/players/1/profile \
  -H "Content-Type: application/json" \
  -d '{"height_cm":178,"weight_kg":73,"preferred_foot":"Right","jersey_number":9}'

# 6. Ajouter des stats
curl -X POST http://localhost:5000/api/stats \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"club_id":1,"season_id":1,"competition_id":1,"goals":22,"assists":5,"appearances":30}'

# 7. Rechercher
curl "http://localhost:5000/api/players/search?name=Mbap"

# 8. Stats par saison
curl "http://localhost:5000/api/players/1/stats?season=2023-2024"

# 9. Mise à jour partielle (PATCH)
curl -X PATCH http://localhost:5000/api/players/1 \
  -H "Content-Type: application/json" \
  -d '{"photo_url":"/static/uploads/mbappe.jpg"}'

# 10. Suppression (cascade profil + stats)
curl -X DELETE http://localhost:5000/api/players/1
```

---

## 8. Importer le jeu de données de démo

Trois méthodes équivalentes :

### A) Via la commande Flask CLI (recommandé)

```bash
docker compose exec api flask seed
```

### B) Via l'endpoint HTTP

```bash
curl -X POST http://localhost:5000/api/import/sample-data
```

### C) Via le bouton du frontend

Sur <http://localhost:5000/>, cliquez sur **« Importer les données de démo »**.

### Contenu du jeu de données

- **5 clubs** : Real Madrid, Paris Saint-Germain, Manchester City, FC Barcelona, Inter Miami CF
- **3 saisons** : 2022-2023, 2023-2024, 2024-2025
- **5 compétitions** : Ligue 1, La Liga, Premier League, Champions League, MLS
- **5 joueurs** avec profil détaillé : Mbappé, Messi, Haaland, Bellingham, Vinícius Jr
- **18 lignes de stats** réparties sur les saisons et compétitions

Le seed est **idempotent** : on peut le relancer sans créer de doublons.

### Réinitialiser la base

```bash
docker compose exec api flask reset
```

---

## 9. Frontend local

L'interface web sert d'**outil de démonstration** et de validation rapide de l'API.

### Fonctionnalités

- 🔍 **Recherche** par nom (debounce sur Entrée)
- 🗓️ **Filtre par saison** (déroulant peuplé via `/api/seasons`)
- 🪪 **Carte joueur** affichant photo, identité, badges (poste, nationalité, club, numéro), bio
- 📊 **Statistiques** organisées par saison puis par compétition
- ⚠️ **Messages clairs** si le joueur ou la saison n'existe pas
- 🌱 **Bouton de seed** pour peupler la base depuis l'interface

### Accès

Ouvrir <http://localhost:5000/> dans un navigateur après avoir lancé `docker compose up`.

---

## 10. Tests automatisés

### Lancer tous les tests

```bash
docker compose exec api pytest
```

### Lancer un fichier spécifique

```bash
docker compose exec api pytest tests/test_players.py -v
```

### Couverture des tests

- **`test_health.py`** : healthcheck, db/stats, accès Swagger
- **`test_players.py`** : création, validation 400, 404, recherche par nom et club, PATCH, PUT, DELETE en cascade, profil One-to-One (création + update), stats par saison
- **`test_clubs_and_stats.py`** : conflit 409 sur doublon de club, CRUD club, chaîne complète création stats, rejet du triplet dupliqué (UNIQUE), upsert, validation saison `end_year >= start_year`

### Configuration des tests

Les tests utilisent une base **SQLite en mémoire** (`TestingConfig`) pour rester rapides et indépendants de MySQL. Chaque test obtient une base fraîche grâce aux fixtures `app` et `client` dans `tests/conftest.py`.

---

## 11. Publication sur Docker Hub

### Construire l'image localement

```bash
docker build -t <votre-username>/footstats-api:1.0 .
```

### Tester l'image

```bash
docker run --rm -p 5000:5000 \
  -e DATABASE_URL="mysql+pymysql://user:pass@host:3306/db" \
  <votre-username>/footstats-api:1.0
```

### Publier

```bash
docker login
docker push <votre-username>/footstats-api:1.0
```

### Récupérer et utiliser l'image publiée

Dans le `docker-compose.yml`, remplacer la section `build:` par :

```yaml
api:
  image: <votre-username>/footstats-api:1.0
```

---

## 12. Argumentaire de soutenance

### Contexte et objectif

Démontrer la capacité à concevoir, développer, conteneuriser et déployer une application web 3-tiers respectant les bonnes pratiques REST, avec persistance relationnelle et documentation interactive.

### Choix techniques justifiés

- **Flask** plutôt que Django : framework léger adapté à une API pure, sans le poids des templates Django ; permet une architecture *factory* claire et testable.
- **SQLAlchemy 2** avec syntaxe `Mapped[...] / mapped_column` : typage statique, meilleure intégration IDE, futur-compatible.
- **MySQL** plutôt que SQLite : moteur relationnel professionnel, gère correctement les contraintes ON DELETE RESTRICT et CASCADE en production.
- **Marshmallow** plutôt que validation manuelle : sépare clairement la validation/sérialisation de la logique métier, permet d'avoir des erreurs 400 cohérentes et localisables.
- **Flasgger + OpenAPI 3** : documentation à jour, testable directement depuis le navigateur — gros plus en soutenance.
- **Docker Compose** : reproductibilité (un seul `docker compose up` pour tout démarrer), isolation, portabilité entre machines.

### Architecture REST défendue

- Routes orientées ressources (`/api/players`, `/api/clubs`, etc.).
- Verbes HTTP utilisés sémantiquement : `GET` (lecture), `POST` (création), `PUT` (remplacement), `PATCH` (modification partielle), `DELETE` (suppression).
- Codes HTTP cohérents (200, 201, 204, 400, 404, 409, 500) avec format d'erreur JSON unifié.
- Sous-ressources (`/api/players/<id>/profile`, `/api/players/<id>/stats`) qui exposent les relations One-to-One et les filtres saison.
- Idempotence : `PUT` et `DELETE` sont idempotents, `POST` ne l'est pas. L'endpoint dédié `/api/stats/upsert` matérialise un upsert idempotent sur le triplet UNIQUE.

### Démonstration possible

1. **Postman / Swagger UI** : parcours complet des endpoints (création → lecture → mise à jour → suppression).
2. **Frontend** : recherche d'un joueur, sélection d'une saison, affichage de la carte.
3. **MySQL** : `docker compose exec db mysql ... -e "SHOW CREATE TABLE player_season_stats;"` pour montrer les contraintes UNIQUE et FK.
4. **Tests** : `docker compose exec api pytest` qui passe en quelques secondes.
5. **Resilience** : tester un POST avec un nom déjà existant → 409 ; un POST avec une position invalide → 400 ; un GET sur un id inexistant → 404.

### Explication des relations

- **One-to-One Player ↔ PlayerProfile** : un joueur n'a qu'un seul profil (taille, poids, etc.). Implémenté par `UNIQUE(player_id)` côté `player_profiles` + cascade DELETE.
- **One-to-Many Club → Players** : un club a plusieurs joueurs ; un joueur n'a qu'un club courant. Si on supprime un club, les joueurs perdent leur club (`SET NULL`) mais sont conservés.
- **Many-to-Many Player ↔ Competition** via `PlayerSeasonStats` : table d'association *enrichie* car elle porte des données (goals, assists, …) sur la relation. C'est la forme académique correcte d'une N-N portant des attributs.

### Docker Compose

- Deux services (`api` + `db`) sur un réseau Docker isolé.
- Volume nommé `footstats_mysql_data` pour la persistance des données.
- Healthcheck MySQL avec `mysqladmin ping` pour que l'API ne démarre que quand la base est prête (`depends_on: condition: service_healthy`).
- Hot-reload Flask en dev grâce au montage du code source en volume.

### Limites et améliorations futures

- Authentification JWT pour les routes en écriture.
- Upload de photos joueur (multipart/form-data).
- Cache Redis sur les listes/recherches.
- Frontend en React + TypeScript.
- Pipeline CI/CD GitHub Actions (tests + build + push Docker Hub auto).
- Sources de données externes (CSV/API ouvertes type *football-data.org*) pour enrichir la base.

---

## 13. Limites et améliorations

### Limites actuelles

- Pas d'authentification : toutes les routes sont publiques (acceptable pour un projet pédagogique local).
- Pas de gestion d'historique de transferts : un joueur a un `current_club_id` simple ; l'historique est reconstruit indirectement via les `PlayerSeasonStats`.
- Pagination basique sans curseur (acceptable pour les volumes du projet).
- Pas de validation des photos (URL libre, pas d'upload réel pour l'instant).

### Pistes d'amélioration

| Axe | Idée |
|---|---|
| Sécurité | JWT avec Flask-JWT-Extended, RBAC sur les routes en écriture |
| Données | Import depuis l'API publique *football-data.org* ou un CSV Kaggle |
| Frontend | Migration vers React + Vite + shadcn/ui |
| DevOps | CI/CD (GitHub Actions), publication automatique sur Docker Hub |
| Observabilité | Sentry pour les erreurs, Prometheus + Grafana pour les métriques |
| Tests | Tests d'intégration MySQL réels, couverture > 90 % via pytest-cov |

---

## Auteurs

Hassan Charaf
Lyes Djemaa

## Licence

Code à but pédagogique. Les marques *Real Madrid*, *PSG*, etc. sont citées à titre purement illustratif.
