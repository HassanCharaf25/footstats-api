/* ============================================================
   FootStats Frontend — vanilla JS
   ============================================================ */

const API_BASE = '/api';

const $ = (id) => document.getElementById(id);
const searchInput = $('search-input');
const seasonSelect = $('season-select');
const searchBtn = $('search-btn');
const resultsEl = $('results');
const detailEl = $('player-detail');
const seedBtn = $('seed-btn');
const seedResult = $('seed-result');

// ---------------------------------------------------------------------------
// Initialisation : charger les saisons
// ---------------------------------------------------------------------------

async function loadSeasons() {
    try {
        const res = await fetch(`${API_BASE}/seasons?per_page=100`);
        if (!res.ok) return;
        const body = await res.json();
        for (const s of body.items) {
            const opt = document.createElement('option');
            opt.value = s.year_label;
            opt.textContent = s.year_label;
            seasonSelect.appendChild(opt);
        }
    } catch (e) {
        console.error('Erreur lors du chargement des saisons :', e);
    }
}

// ---------------------------------------------------------------------------
// Recherche
// ---------------------------------------------------------------------------

async function searchPlayers() {
    const name = searchInput.value.trim();
    detailEl.classList.add('hidden');
    detailEl.innerHTML = '';

    let url;
    if (name === '') {
        url = `${API_BASE}/players?per_page=20`;
    } else {
        url = `${API_BASE}/players/search?name=${encodeURIComponent(name)}`;
    }

    resultsEl.innerHTML = '<p class="empty">Recherche en cours…</p>';

    try {
        const res = await fetch(url);
        const body = await res.json();
        renderResults(body);
    } catch (e) {
        resultsEl.innerHTML = `<div class="error">Erreur réseau : ${e.message}</div>`;
    }
}

function renderResults(body) {
    if (!body.items || body.items.length === 0) {
        resultsEl.innerHTML = `
            <h2>Résultats</h2>
            <p class="empty">Aucun joueur trouvé. Vérifiez l'orthographe ou importez les données de démo ci-dessous.</p>
        `;
        return;
    }

    const cards = body.items.map(p => {
        const club = p.current_club ? p.current_club.name : 'Sans club';
        return `
            <div class="result-card" data-player-id="${p.id}">
                <div class="name">${escapeHtml(p.full_name || (p.first_name + ' ' + p.last_name))}</div>
                <div class="meta">${escapeHtml(p.position || '—')} · ${escapeHtml(club)}</div>
            </div>
        `;
    }).join('');

    resultsEl.innerHTML = `
        <h2>Résultats (${body.total})</h2>
        <div class="results-grid">${cards}</div>
    `;

    resultsEl.querySelectorAll('.result-card').forEach(card => {
        card.addEventListener('click', () => loadPlayerDetail(card.dataset.playerId));
    });
}

// ---------------------------------------------------------------------------
// Fiche joueur
// ---------------------------------------------------------------------------

async function loadPlayerDetail(playerId) {
    detailEl.classList.remove('hidden');
    detailEl.innerHTML = '<p class="empty">Chargement de la fiche…</p>';
    detailEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

    try {
        const playerRes = await fetch(`${API_BASE}/players/${playerId}`);
        if (!playerRes.ok) {
            const err = await playerRes.json();
            detailEl.innerHTML = `<div class="error">${escapeHtml(err.message || 'Joueur introuvable')}</div>`;
            return;
        }
        const player = await playerRes.json();

        const selectedSeason = seasonSelect.value;
        const statsUrl = selectedSeason
            ? `${API_BASE}/players/${playerId}/stats?season=${encodeURIComponent(selectedSeason)}`
            : `${API_BASE}/players/${playerId}/stats`;
        const statsRes = await fetch(statsUrl);
        const statsBody = await statsRes.json();

        renderPlayerDetail(player, statsBody, selectedSeason);
    } catch (e) {
        detailEl.innerHTML = `<div class="error">Erreur : ${escapeHtml(e.message)}</div>`;
    }
}

function renderPlayerDetail(player, statsBody, selectedSeason) {
    const profile = player.profile || {};
    const club = player.current_club;

    // Cas particulier : la route /stats?season=... renvoie {items, season, found:false}
    // si la saison n'existe pas en base.
    let stats;
    if (Array.isArray(statsBody)) {
        stats = statsBody;
    } else if (statsBody && statsBody.found === false) {
        stats = [];
    } else {
        stats = [];
    }

    const photoBlock = player.photo_url
        ? `<img src="${escapeAttr(player.photo_url)}" alt="${escapeAttr(player.full_name)}" onerror="this.replaceWith(document.createTextNode('👤'))" />`
        : '👤';

    const badges = [];
    if (player.position) badges.push(`<span class="badge">${escapeHtml(player.position)}</span>`);
    if (player.nationality) badges.push(`<span class="badge">🌍 ${escapeHtml(player.nationality)}</span>`);
    if (club) badges.push(`<span class="badge club">${escapeHtml(club.name)}</span>`);
    if (profile.jersey_number) badges.push(`<span class="badge">#${profile.jersey_number}</span>`);

    let statsContent;
    if (stats.length === 0) {
        statsContent = selectedSeason
            ? `<p class="empty">Aucune statistique pour ${escapeHtml(selectedSeason)}.</p>`
            : `<p class="empty">Aucune statistique enregistrée pour ce joueur.</p>`;
    } else {
        // Regrouper par saison pour un affichage plus clair
        const bySeason = {};
        for (const s of stats) {
            const label = s.season ? s.season.year_label : 'Saison inconnue';
            (bySeason[label] = bySeason[label] || []).push(s);
        }

        statsContent = Object.entries(bySeason).map(([season, lines]) => {
            const competitionTiles = lines.map(line => {
                const compName = line.competition ? line.competition.name : 'Compétition';
                return `
                    <div class="season-block">
                        <h4>${escapeHtml(compName)}</h4>
                        <div class="stats-grid">
                            <div class="stat-tile"><div class="value">${line.goals}</div><div class="label">Buts</div></div>
                            <div class="stat-tile"><div class="value">${line.assists}</div><div class="label">Passes D.</div></div>
                            <div class="stat-tile"><div class="value">${line.appearances}</div><div class="label">Matchs</div></div>
                            <div class="stat-tile"><div class="value">${line.minutes_played}</div><div class="label">Minutes</div></div>
                            <div class="stat-tile"><div class="value">${line.yellow_cards}</div><div class="label">🟨 Jaunes</div></div>
                            <div class="stat-tile"><div class="value">${line.red_cards}</div><div class="label">🟥 Rouges</div></div>
                        </div>
                    </div>
                `;
            }).join('');
            return `<h3 style="margin-top:1rem;">Saison ${escapeHtml(season)}</h3>${competitionTiles}`;
        }).join('');
    }

    detailEl.innerHTML = `
        <div class="player-header">
            <div class="player-photo">${photoBlock}</div>
            <div class="player-info">
                <h3>${escapeHtml(player.full_name)}</h3>
                <div class="badges">${badges.join('')}</div>
                ${profile.biography ? `<p class="hint" style="margin-top:0.5rem;">${escapeHtml(profile.biography)}</p>` : ''}
            </div>
        </div>
        <div class="season-stats">${statsContent}</div>
    `;
}

// ---------------------------------------------------------------------------
// Seed
// ---------------------------------------------------------------------------

async function importSampleData() {
    seedResult.classList.remove('hidden');
    seedResult.textContent = 'Import en cours…';
    try {
        const res = await fetch(`${API_BASE}/import/sample-data`, { method: 'POST' });
        const body = await res.json();
        seedResult.textContent = JSON.stringify(body, null, 2);
        // Recharger les saisons (qui peuvent avoir été créées)
        seasonSelect.innerHTML = '<option value="">Toutes les saisons</option>';
        await loadSeasons();
    } catch (e) {
        seedResult.textContent = 'Erreur : ' + e.message;
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function escapeAttr(str) { return escapeHtml(str); }

// ---------------------------------------------------------------------------
// Bindings
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', async () => {
    await loadSeasons();

    searchBtn.addEventListener('click', searchPlayers);
    searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') searchPlayers(); });
    seedBtn.addEventListener('click', importSampleData);
    seasonSelect.addEventListener('change', () => {
        // Si une fiche joueur est ouverte, on la recharge avec la nouvelle saison.
        const openCard = detailEl.querySelector('.player-info h3');
        const openId = resultsEl.querySelector('.result-card[data-player-id]');
        if (openCard && openId) {
            loadPlayerDetail(openId.dataset.playerId);
        }
    });

    // Charger une liste initiale
    searchPlayers();
});
