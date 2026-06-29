const SALUS_HEADERS = {
  "X-Salus-Passphrase": "salus-secure"
};

// ── Clock ────────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('sys-clock').textContent =
    now.toUTCString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, '$1') + ' UTC  |  ' +
    now.toLocaleDateString('en-US', { weekday:'short', year:'numeric', month:'short', day:'numeric' });
}
setInterval(updateClock, 1000);
updateClock();

// ── Helpers ───────────────────────────────────────────────────────────
function priorityBadge(p) {
  const map = { High: 'badge-red', Medium: 'badge-yellow', Low: 'badge-muted' };
  return `<span class="badge ${map[p] || 'badge-muted'}">${p}</span>`;
}

function statusBadge(s) {
  const map = { Active: 'badge-green', Standby: 'badge-yellow', Offline: 'badge-red', Completed: 'badge-cyan' };
  return `<span class="badge ${map[s] || 'badge-muted'}">${s}</span>`;
}

function agentDotClass(s) {
  const map = { Active: 'dot-active', Standby: 'dot-standby', Offline: 'dot-offline' };
  return map[s] || 'dot-standby';
}

function formatTs(ts) {
  if (!ts) return '';
  const d = new Date(ts.replace(' ', 'T') + 'Z');
  return d.toLocaleString('en-US', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
}

// ── Missions ──────────────────────────────────────────────────────────
async function loadMissions() {
  const el = document.getElementById('missions');
  try {
    const res = await fetch('/missions', { headers: SALUS_HEADERS });
    const data = await res.json();
    if (!data.missions.length) { el.innerHTML = '<span class="loading">No missions found.</span>'; return; }
    el.innerHTML = data.missions.map(m => `
      <div class="mission-item">
        <div class="mission-title">${m.title}</div>
        <div class="mission-meta">
          ${statusBadge(m.status)}
          ${priorityBadge(m.priority)}
        </div>
        <div class="mission-next">&#x25B8; ${m.next_action}</div>
      </div>`).join('');
  } catch {
    el.innerHTML = '<span class="error">Failed to load missions.</span>';
  }
}

// ── Agents ────────────────────────────────────────────────────────────
async function loadAgents() {
  const el = document.getElementById('agents');
  try {
    const res = await fetch('/agents', { headers: SALUS_HEADERS });
    const data = await res.json();
    if (!data.agents.length) { el.innerHTML = '<span class="loading">No agents found.</span>'; return; }
    el.innerHTML = data.agents.map(a => `
      <div class="agent-item">
        <span class="agent-dot ${agentDotClass(a.status)}"></span>
        <div>
          <div class="agent-name">${a.name}</div>
          <div class="agent-mission">${a.mission}</div>
        </div>
        <div style="margin-left:auto">${statusBadge(a.status)}</div>
      </div>`).join('');
  } catch {
    el.innerHTML = '<span class="error">Failed to load agents.</span>';
  }
}

// ── Core Status ──────────────────────────────────────────────────────
async function loadCoreStatus() {
  const el = document.getElementById('core-status');
  try {
    const res = await fetch('/core/status', { headers: SALUS_HEADERS });
    const data = await res.json();
    const components = data.components || {};
    const plugins = Array.isArray(data.plugins) ? data.plugins : [];
    el.innerHTML = `
      <div class="core-status-grid">
        <div class="core-status-item">
          <div class="core-status-label">System</div>
          <div class="core-status-value">${data.status || 'unknown'}</div>
        </div>
        <div class="core-status-item">
          <div class="core-status-label">Memory</div>
          <div class="core-status-value">${components.memory?.status || 'unknown'}</div>
        </div>
        <div class="core-status-item">
          <div class="core-status-label">Agents</div>
          <div class="core-status-value">${components.agent_registry?.count || 0}</div>
        </div>
        <div class="core-status-item">
          <div class="core-status-label">Plugins</div>
          <div class="core-status-value">${plugins.length}</div>
        </div>
      </div>
      <div class="core-status-footer">
        ${plugins.slice(0, 3).map(plugin => `<span class="badge ${plugin.status === 'active' ? 'badge-green' : 'badge-yellow'}">${plugin.name}</span>`).join('')}
      </div>`;
  } catch {
    el.innerHTML = '<span class="error">Failed to load core status.</span>';
  }
}

// ── SITREPs ───────────────────────────────────────────────────────────
async function loadSitreps() {
  const el = document.getElementById('sitreps');
  try {
    const res = await fetch('/sitreps', { headers: SALUS_HEADERS });
    const data = await res.json();
    if (!data.sitreps.length) {
      el.innerHTML = '<span class="loading">No SITREPs filed yet.</span>';
      return;
    }
    el.innerHTML = data.sitreps.map(s => `
      <div class="sitrep-entry">
        <div class="sitrep-priority">${s.top_priority || '—'}</div>
        ${s.blocker ? `<div class="sitrep-blocker">&#x26A0; ${s.blocker}</div>` : ''}
        <ul class="sitrep-actions">
          ${[s.action_1, s.action_2, s.action_3].filter(Boolean).map(a => `<li>${a}</li>`).join('')}
        </ul>
        <div class="sitrep-ts">${formatTs(s.created_at)}</div>
      </div>`).join('');
  } catch {
    el.innerHTML = '<span class="error">Failed to load SITREPs.</span>';
  }
}

async function createSitrep() {
  const feedback = document.getElementById('sitrep-feedback');
  const payload = {
    top_priority: document.getElementById('top_priority').value.trim(),
    blocker: document.getElementById('blocker').value.trim(),
    action_1: document.getElementById('action_1').value.trim(),
    action_2: document.getElementById('action_2').value.trim(),
    action_3: document.getElementById('action_3').value.trim(),
  };

  if (!payload.top_priority) {
    feedback.style.color = 'var(--red)';
    feedback.textContent = 'Top priority is required.';
    return;
  }

  try {
    const res = await fetch('/sitreps', {
      method: 'POST',
      headers: {
        ...SALUS_HEADERS,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error();

    ['top_priority','blocker','action_1','action_2','action_3'].forEach(id => {
      document.getElementById(id).value = '';
    });

    feedback.style.color = 'var(--green)';
    feedback.textContent = 'SITREP filed successfully.';
    setTimeout(() => { feedback.textContent = ''; }, 3000);
    loadSitreps();
  } catch {
    feedback.style.color = 'var(--red)';
    feedback.textContent = 'Failed to submit SITREP.';
  }
}

// ── Init ──────────────────────────────────────────────────────────────
loadMissions();
loadAgents();
loadCoreStatus();
loadSitreps();