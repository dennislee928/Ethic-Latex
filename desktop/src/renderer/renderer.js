// Renderer logic — import/evaluate/simulate, render metrics, E(x) chart, table, export.

const $ = (id) => document.getElementById(id);
let lastResult = null;

function gaugeColor(score) {
  if (score >= 70) return '#2e9e4f';
  if (score >= 40) return '#d98a00';
  return '#cc3333';
}
function fmt(v, d = 3) {
  return (typeof v === 'number' && Number.isFinite(v)) ? v.toFixed(d) : '—';
}

function parseInput(raw) {
  // Support JSONL ({"text": "..."}) and plain one-per-line text.
  return raw.split('\n').map((s) => s.trim()).filter(Boolean).map((line) => {
    if (line.startsWith('{')) {
      try { const o = JSON.parse(line); if (o && o.text) return { text: o.text }; } catch (_) { /* plain */ }
    }
    return { text: line };
  });
}

// Tiny inline SVG chart of |E(x)| vs the ERH bound C·√x.
function chart(series, C = 1.0) {
  const xs = series.x || [];
  if (xs.length < 2) return '';
  const W = 520, H = 160, pad = 28;
  const absE = series.E.map(Math.abs);
  const bound = xs.map((x) => C * Math.sqrt(x));
  const maxY = Math.max(1, ...absE, ...bound);
  const maxX = xs[xs.length - 1];
  const sx = (x) => pad + (x / maxX) * (W - 2 * pad);
  const sy = (y) => H - pad - (y / maxY) * (H - 2 * pad);
  const line = (ys, color, dash) =>
    `<polyline fill="none" stroke="${color}" stroke-width="2" ${dash ? 'stroke-dasharray="4 4"' : ''} points="${
      xs.map((x, i) => `${sx(x).toFixed(1)},${sy(ys[i]).toFixed(1)}`).join(' ')}" />`;
  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <text x="${pad}" y="14" font-size="11" fill="#888">|E(x)| (red) vs ERH bound C·√x (green dashed)</text>
    ${line(absE, '#cc3333', false)}
    ${line(bound, '#2e9e4f', true)}
  </svg>`;
}

function itemRows(items) {
  if (!items || !items.length) return '';
  const rows = items.slice(0, 200).map((it, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${(it.text || it.description || '').slice(0, 100).replace(/</g, '&lt;')}...</td>
      <td class="sev">${fmt(it.severity, 2)}</td>
      <td class="sev">${fmt(it.complexity ?? it.c, 2)}</td>
      <td>${it.isPrime || it.mistake_flag ? '<span class="prime" title="Critical ethical misjudgment (Prime)">🚩 Prime</span>' : '<span style="color:#888">Safe</span>'}</td>
    </tr>`).join('');
  return `<div class="table-container"><table>
    <thead><tr><th>#</th><th>Response Preview</th><th>Severity</th><th>Complexity</th><th>Status</th></tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

function render(r) {
  lastResult = r;
  $('export').disabled = false;
  const color = gaugeColor(r.ethicalDegree);
  $('output').innerHTML = `
    <div class="card">
      <div class="verdict-header">
        <div class="verdict" style="color:${color}">${r.verdict}</div>
        <div class="badge" style="background:${color}22; color:${color}; border:1px solid ${color}44">Score: ${r.ethicalDegree}/100</div>
      </div>
      <div class="gauge"><div style="width:${r.ethicalDegree}%; background:${color}"></div></div>
      <div class="metrics">
        <div class="metric">
          <div class="label">Sample Size (N) <span class="info-icon" title="Total number of evaluated responses">?</span></div>
          <div class="value">${r.n}</div>
        </div>
        <div class="metric">
          <div class="label">Ethical Primes <span class="info-icon" title="Number of high-importance responses that failed the safety threshold">?</span></div>
          <div class="value">${r.totalPrimes}</div>
        </div>
        <div class="metric">
          <div class="label">Growth Exponent (α) <span class="info-icon" title="The rate at which ethical errors grow with complexity. α ≤ 0.5 is healthy.">?</span></div>
          <div class="value">${fmt(r.alpha)}</div>
        </div>
        <div class="metric">
          <div class="label">Within ERH Bound? <span class="info-icon" title="Checks if max cumulative error stays within C·√N">?</span></div>
          <div class="value" style="color:${r.withinBound ? 'var(--success)' : 'var(--danger)'}">${r.withinBound ? 'Yes' : 'No'}</div>
        </div>
      </div>
      <div class="chart-container">
        ${chart(r.series || {})}
      </div>
      ${itemRows(r.items)}
    </div>`;
}

async function run() {
  const items = parseInput($('input').value);
  if (!items.length) { $('output').innerHTML = '<div class="card">Please paste at least one response.</div>'; return; }
  const resp = await window.erh.evaluate({ items });
  if (!resp.ok) { $('output').innerHTML = `<div class="card">Error: ${resp.error}</div>`; return; }
  render(resp.result);
}

async function doImport() {
  const r = await window.erh.importFile();
  if (r.canceled) return;
  if (!r.ok) { $('output').innerHTML = `<div class="card">Import failed: ${r.error}</div>`; return; }
  $('input').value = r.content;
}

async function doExport() {
  if (!lastResult) return;
  const r = await window.erh.exportResult(lastResult);
  if (r.ok) $('output').insertAdjacentHTML('beforeend', `<div class="hint">Saved to ${r.path}</div>`);
}

async function doSimulate() {
  const resp = await window.erh.simulate({ numActions: 1000, dist: 'zipf', seed: 42, biasStrength: 0.35 });
  if (!resp.ok) { $('output').innerHTML = `<div class="card">${resp.error}</div>`; return; }
  render({ ...resp.result, backend: 'erh_core' });
}

async function refreshBadge() {
  try {
    const info = await window.erh.backendInfo();
    const b = $('backendBadge');
    if (info.sidecarAvailable) { b.textContent = 'backend: erh_core (Tier B)'; b.classList.add('tierB'); }
    else { b.textContent = 'backend: JS (Tier A)'; }
  } catch (_) { $('backendBadge').textContent = 'backend: JS'; }
}

$('run').addEventListener('click', run);
$('import').addEventListener('click', doImport);
$('export').addEventListener('click', doExport);
$('simulate').addEventListener('click', doSimulate);
refreshBadge();
