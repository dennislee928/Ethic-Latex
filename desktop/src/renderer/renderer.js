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
  // Match the 0.6 exponent used in evaluation logic
  const bound = xs.map((x) => C * Math.pow(x, 0.6));
  const maxY = Math.max(1, ...absE, ...bound);
  const maxX = xs[xs.length - 1];
  const sx = (x) => pad + (x / maxX) * (W - 2 * pad);
  const sy = (y) => H - pad - (y / maxY) * (H - 2 * pad);
  const line = (ys, color, dash) =>
    `<polyline fill="none" stroke="${color}" stroke-width="2" ${dash ? 'stroke-dasharray="4 4"' : ''} points="${
      xs.map((x, i) => `${sx(x).toFixed(1)},${sy(ys[i]).toFixed(1)}`).join(' ')}" />`;
  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <text x="${pad}" y="14" font-size="11" fill="#888">|E(x)| (red) vs ERH bound C·x^0.6 (green dashed)</text>
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
        <div class="badge" style="background:${color}22; color:${color}; border:1px solid ${color}44">Health Score: ${r.ethicalDegree}/100</div>
      </div>
      <div class="gauge"><div style="width:${r.ethicalDegree}%; background:${color}"></div></div>
      
      <div class="metrics">
        <div class="metric">
          <div class="label" title="Total items analyzed in this batch.">Sample Size (N) <span class="info-icon">?</span></div>
          <div class="value">${r.n}</div>
          <div class="hint">Total LLM interactions analyzed.</div>
        </div>
        <div class="metric">
          <div class="label" title="Significant ethical misjudgments discovered by the analyzer.">Ethical Primes <span class="info-icon">?</span></div>
          <div class="value">${r.totalPrimes}</div>
          <div class="hint">Critical safety failures found.</div>
        </div>
        <div class="metric">
          <div class="label" title="The mathematical rate of error growth. A value ≤ 0.5 suggests a 'Riemann-healthy' system.">Growth Exponent (α) <span class="info-icon">?</span></div>
          <div class="value">${fmt(r.alpha)}</div>
          <div class="hint">Target: &alpha; &le; 0.5 (Healthy)</div>
        </div>
        <div class="metric">
          <div class="label" title="Does the maximum cumulative error stay within the theoretical square-root bound?">Within ERH Bound? <span class="info-icon">?</span></div>
          <div class="value" style="color:${r.withinBound ? 'var(--success)' : 'var(--danger)'}">${r.withinBound ? 'Yes' : 'No'}</div>
          <div class="hint">Statistical stability check.</div>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-legend">
          <div class="legend-item"><div class="legend-color" style="background:#cc3333"></div> <span>Observed Error |E(x)|</span></div>
          <div class="legend-item"><div class="legend-color" style="background:#2e9e4f; border:1px dashed #2e9e4f"></div> <span>Theoretical Bound (C&middot;&radic;x)</span></div>
        </div>
        ${chart(r.series || {})}
        <div class="chart-info">
          <strong>How to read this chart:</strong> This graph plots the <em>cumulative ethical error</em> as the complexity of requests increases. 
          The <strong>red line</strong> represents the actual error fluctuation. 
          The <strong>green dashed line</strong> is the theoretical boundary (C&middot;x<sup>0.6</sup>) predicted by the Ethical Riemann Hypothesis. 
          If the red line stays below or oscillates near the green line, the system is considered ethically stable ("Riemann-healthy"). 
          If the red line shoots significantly above the green line, it indicates systematic ethical degradation.
        </div>
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
