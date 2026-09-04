const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const configForm = document.getElementById('config-form');
const configSaved = document.getElementById('config-saved');

let pollHandle = null;

function getToken() {
  return localStorage.getItem('dashboard_token');
}

function setToken(token) {
  localStorage.setItem('dashboard_token', token);
}

function clearToken() {
  localStorage.removeItem('dashboard_token');
}

async function apiFetch(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
      ...(options.headers || {}),
    },
  });
  if (res.status === 401) {
    showLogin();
    throw new Error('Non autorisé');
  }
  return res.json();
}

function showLogin() {
  clearToken();
  if (pollHandle) clearInterval(pollHandle);
  loginScreen.classList.remove('hidden');
  dashboardScreen.classList.add('hidden');
}

function showDashboard() {
  loginScreen.classList.add('hidden');
  dashboardScreen.classList.remove('hidden');
  refreshAll();
  loadConfig().catch(() => {});
  pollHandle = setInterval(refreshAll, 5000);
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';
  const token = document.getElementById('login-token').value.trim();
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });
    const data = await res.json();
    if (data.ok) {
      setToken(token);
      showDashboard();
    } else {
      loginError.textContent = 'Token invalide.';
    }
  } catch (err) {
    loginError.textContent = 'Erreur de connexion au serveur.';
  }
});

logoutBtn.addEventListener('click', showLogin);

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h}h ${m}m ${s}s`;
}

async function refreshStats() {
  const stats = await apiFetch('/api/stats');
  document.getElementById('stat-guilds').textContent = stats.guildCount ?? '—';
  document.getElementById('stat-users').textContent = stats.userCount ?? '—';
  document.getElementById('stat-commands').textContent = stats.commandsUsed ?? '—';
  document.getElementById('stat-uptime').textContent = formatUptime(stats.uptimeSeconds || 0);

  const pill = document.getElementById('status-pill');
  const statusText = document.getElementById('status-text');
  pill.className = `status-pill ${stats.status}`;
  const labels = { online: 'En ligne', offline: 'Hors ligne', error: 'Erreur', starting: 'Démarrage' };
  statusText.textContent = labels[stats.status] || stats.status;
}

async function refreshLogs() {
  const logs = await apiFetch('/api/logs');
  const container = document.getElementById('logs');
  container.innerHTML = logs
    .map((l) => {
      const time = new Date(l.timestamp).toLocaleTimeString('fr-FR');
      return `<div class="log-entry ${l.level}"><span class="log-time">${time}</span>${escapeHtml(l.message)}</div>`;
    })
    .join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function loadConfig() {
  const cfg = await apiFetch('/api/config');
  configForm.prefix.value = cfg.prefix || '';
  configForm.welcomeChannelId.value = cfg.welcomeChannelId || '';
  configForm.welcomeMessage.value = cfg.welcomeMessage || '';
  configForm.embedColor.value = cfg.embedColor || '#5865f2';
  configForm.botStatus.value = cfg.botStatus || '';
  configForm.logCommandUsage.checked = !!cfg.logCommandUsage;
}

configForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    prefix: configForm.prefix.value,
    welcomeChannelId: configForm.welcomeChannelId.value,
    welcomeMessage: configForm.welcomeMessage.value,
    embedColor: configForm.embedColor.value,
    botStatus: configForm.botStatus.value,
    logCommandUsage: configForm.logCommandUsage.checked,
  };
  await apiFetch('/api/config', { method: 'POST', body: JSON.stringify(payload) });
  configSaved.textContent = 'Configuration enregistrée ✅';
  setTimeout(() => (configSaved.textContent = ''), 2500);
});

function refreshAll() {
  refreshStats().catch(() => {});
  refreshLogs().catch(() => {});
}

// --- Démarrage ---
if (getToken()) {
  showDashboard();
} else {
  showLogin();
}
