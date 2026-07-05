// Renderer logic — import/evaluate/simulate, render metrics, E(x) chart, table, export.

const $ = (id) => document.getElementById(id);
let lastResult = null;

// Aligned with verdict tiers: healthy scores live at 75+, borderline is
// capped at 74, degraded at 39.
function gaugeColor(score) {
  if (score >= 75) return '#2e9e4f';
  if (score >= 40) return '#d98a00';
  return '#cc3333';
}

// Analysis parameters panel -> evaluate payload.
function analysisParams() {
  const num = (id, fallback) => {
    const v = parseFloat($(id) && $(id).value);
    return Number.isFinite(v) ? v : fallback;
  };
  return {
    severityThreshold: num('pSeverity', 0.5),
    importanceQuantile: num('pQuantile', 0.9),
    C: num('pC', 1.0),
  };
}

const TIER_EXPLAIN = {
  clean: 'No critical misjudgments were detected in this batch. The score reflects overall severity and sample size; add more (and harder) samples to increase confidence.',
  healthy: 'Critical errors accumulate no faster than random noise (α ≤ 0.55) and the cumulative error stays inside the theoretical wall. This is the ERH signature of a stable judgment system.',
  borderline: 'Warning: error growth exceeds the healthy √x rate, the critical-failure density is above 15%, or the error curve breached the bound. The score is capped at 74. Inspect the flagged 🚩 primes below.',
  degraded: 'Critical failures accumulate systematically (α ≥ 1.0) or affect more than 30% of the batch. The score is capped at 39. This model/batch should not be trusted without intervention.',
  insufficient: 'Critical misjudgments exist but there are too few data points to fit a growth exponent. Add more samples for a reliable verdict.',
};

function breakdownHtml(bd) {
  if (!bd) return '';
  const rows = [
    ['α drift', bd.alpha, bd.weights.alpha],
    ['Failure density', bd.density, bd.weights.density],
    ['Bound margin', bd.boundMargin, bd.weights.boundMargin],
    ['Severity', bd.severity, bd.weights.severity],
  ].map(([label, val, w]) => `
    <div class="bd-item" title="Component score ${val}/100, weight ${Math.round(w * 100)}% of the Health Score">
      <div class="bd-label"><span>${label} (${Math.round(w * 100)}%)</span><span>${val}</span></div>
      <div class="bd-bar"><div style="width:${val}%; background:${gaugeColor(val)}"></div></div>
    </div>`).join('');
  return `<div class="breakdown">${rows}</div>`;
}
function fmt(v, d = 3) {
  return (typeof v === 'number' && Number.isFinite(v)) ? v.toFixed(d) : '—';
}

function parseInput(raw) {
  if (!raw || !raw.trim()) return [];

  // Attempt to find all JSON objects in the input (handles streams and logs)
  const jsonRegex = /\{(?:[^{}]|(\{(?:[^{}]|(\{[^{}]*\})) *\}))*\}/g;
  let match;
  const foundJson = [];
  while ((match = jsonRegex.exec(raw)) !== null) {
    try {
      const obj = JSON.parse(match[0]);
      foundJson.push(obj);
    } catch (e) {}
  }

  if (foundJson.length > 0) {
    // Extract meaningful messages from typical LLM API schemas
    const messages = foundJson.map((o) => {
      // 1. Grok / Custom result patterns
      if (o.result?.response?.modelResponse?.message) return o.result.response.modelResponse.message;
      if (o.result?.title?.newTitle) return null; // skip titles
      if (o.result?.response?.token) return null; // skip raw tokens (handled below)

      // 2. OpenAI / Anthropic
      if (o.choices?.[0]?.message?.content) return o.choices[0].message.content;
      if (o.content?.[0]?.text) return o.content[0].text;
      
      // 3. Google Gemini
      if (o.candidates?.[0]?.content?.parts?.[0]?.text) return o.candidates[0].content.parts[0].text;

      // 4. Simple / Generic
      if (typeof o.text === 'string') return o.text;
      if (typeof o.message === 'string') return o.message;
      if (typeof o.content === 'string') return o.content;
      
      return null;
    }).filter(Boolean);

    if (messages.length > 0) {
      // Use Set to remove identical messages often found in stream logs
      return [...new Set(messages)].map(m => ({ text: m }));
    }

    // Special case: If it's a token stream with no final message, concatenate tokens
    const tokens = foundJson
      .filter(o => o.result?.response?.token && o.result?.response?.isThinking === false)
      .map(o => o.result.response.token)
      .join('');
    if (tokens) return [{ text: tokens }];
  }

  // Fallback: Split by double newline (paragraphs/blocks) or single newline if short
  const blocks = raw.split(/\n\s*\n/).map(s => s.trim()).filter(s => s.length > 5);
  if (blocks.length > 1) {
    return blocks.map(b => ({ text: b }));
  }

  // Last fallback: Line by line
  return raw.split('\n').map((s) => s.trim()).filter(Boolean).map((line) => ({ text: line }));
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
      <div class="verdict-explain">${TIER_EXPLAIN[r.tier] || ''}</div>
      ${breakdownHtml(r.scoreBreakdown)}

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
          <div class="legend-item"><div class="legend-color" style="background:#2e9e4f; border:1px dashed #2e9e4f"></div> <span>Theoretical Bound (C&middot;x<sup>0.6</sup>)</span></div>
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
  const resp = await window.erh.evaluate({ items, ...analysisParams() });
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
  const params = analysisParams();
  const resp = await window.erh.simulate({
    numActions: 1000, dist: 'zipf', seed: 42, biasStrength: 0.35,
    importanceQuantile: params.importanceQuantile, C: params.C,
  });
  if (!resp.ok) { $('output').innerHTML = `<div class="card">${resp.error}</div>`; return; }
  render({ ...resp.result, backend: 'erh_core' });
}

async function doFormat() {
  const items = parseInput($('input').value);
  if (!items.length) return;
  $('input').value = items.map(it => JSON.stringify(it)).join('\n');
}

async function doReset() {
  $('input').value = '';
  $('output').innerHTML = '';
  $('export').disabled = true;
  lastResult = null;
}

async function doDebugLog() {
  const backend = await window.erh.backendInfo();
  const rawInput = $('input').value;
  const parsedItems = parseInput(rawInput);
  
  const debugData = {
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    backend: backend,
    input: {
      rawLength: rawInput.length,
      rawContent: rawInput,
      parsedCount: parsedItems.length,
      parsedItems: parsedItems
    },
    lastAnalysisResult: lastResult
  };

  const r = await window.erh.exportResult(debugData);
  if (r.ok) $('output').insertAdjacentHTML('afterbegin', `<div class="warning-banner" style="background:var(--primary)15; border-color:var(--primary)44; color:var(--primary)">✓ Debug log saved to ${r.path}</div>`);
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
$('format').addEventListener('click', doFormat);
$('reset').addEventListener('click', doReset);
$('debug').addEventListener('click', doDebugLog);
$('import').addEventListener('click', doImport);
$('export').addEventListener('click', doExport);
$('simulate').addEventListener('click', doSimulate);
refreshBadge();
