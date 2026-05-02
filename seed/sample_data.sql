-- ============================================================================
-- FootStats API - Jeu de données minimal (alternative SQL au script Python)
-- ============================================================================
-- Usage :
--   docker compose exec -T db mysql -ufootuser -pfootpass footstats < seed/sample_data.sql
--
-- Ce fichier reproduit l'essentiel de seed_data.py en SQL pur.
-- Il est idempotent grâce aux INSERT IGNORE et REPLACE.
-- ============================================================================

-- Clubs
INSERT IGNORE INTO clubs (name, country, stadium, founded_year, created_at, updated_at) VALUES
('Real Madrid',          'Spain',   'Santiago Bernabéu', 1902, NOW(), NOW()),
('Paris Saint-Germain',  'France',  'Parc des Princes',  1970, NOW(), NOW()),
('Manchester City',      'England', 'Etihad Stadium',    1880, NOW(), NOW()),
('FC Barcelona',         'Spain',   'Camp Nou',          1899, NOW(), NOW()),
('Inter Miami CF',       'USA',     'Chase Stadium',     2018, NOW(), NOW());

-- Saisons
INSERT IGNORE INTO seasons (year_label, start_year, end_year, created_at, updated_at) VALUES
('2022-2023', 2022, 2023, NOW(), NOW()),
('2023-2024', 2023, 2024, NOW(), NOW()),
('2024-2025', 2024, 2025, NOW(), NOW());

-- Compétitions
INSERT IGNORE INTO competitions (name, country, type, created_at, updated_at) VALUES
('Ligue 1',          'France',  'league',        NOW(), NOW()),
('La Liga',          'Spain',   'league',        NOW(), NOW()),
('Premier League',   'England', 'league',        NOW(), NOW()),
('Champions League', 'Europe',  'international', NOW(), NOW()),
('MLS',              'USA',     'league',        NOW(), NOW());

-- Joueurs
INSERT IGNORE INTO players (first_name, last_name, birth_date, nationality, position, photo_url, current_club_id, created_at, updated_at) VALUES
('Kylian',  'Mbappé',     '1998-12-20', 'France',    'Forward',    '/static/uploads/mbappe.jpg',     (SELECT id FROM clubs WHERE name='Real Madrid'),         NOW(), NOW()),
('Lionel',  'Messi',      '1987-06-24', 'Argentina', 'Forward',    '/static/uploads/messi.jpg',      (SELECT id FROM clubs WHERE name='Inter Miami CF'),      NOW(), NOW()),
('Erling',  'Haaland',    '2000-07-21', 'Norway',    'Forward',    '/static/uploads/haaland.jpg',    (SELECT id FROM clubs WHERE name='Manchester City'),     NOW(), NOW()),
('Jude',    'Bellingham', '2003-06-29', 'England',   'Midfielder', '/static/uploads/bellingham.jpg', (SELECT id FROM clubs WHERE name='Real Madrid'),         NOW(), NOW()),
('Vinícius','Júnior',     '2000-07-12', 'Brazil',    'Forward',    '/static/uploads/vinicius.jpg',   (SELECT id FROM clubs WHERE name='Real Madrid'),         NOW(), NOW());

-- NOTE : Pour les profils et les stats, utilisez plutôt `flask seed` qui
-- résout proprement les FK. Ce fichier SQL est volontairement minimal
-- (joueurs + clubs + saisons + compétitions) pour servir d'exemple.
