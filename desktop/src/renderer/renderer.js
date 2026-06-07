// Renderer logic — collects responses, calls the ERH evaluator over IPC, renders results.

const $ = (id) => document.getElementById(id);

function gaugeColor(score) {
  if (score >= 70) return '#2e9e4f';
  if (score >= 40) return '#d98a00';
  return '#cc3333';
}

function fmt(v, d = 3) {
  return (typeof v === 'number' && Number.isFinite(v)) ? v.toFixed(d) : '—';
}

async function run() {
  const raw = $('input').value;
  const items = raw
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((text) => ({ text }));

  if (items.length === 0) {
    $('output').innerHTML = '<div class="card">Please paste at least one response.</div>';
    return;
  }

  const resp = await window.erh.evaluate({ items });
  if (!resp.ok) {
    $('output').innerHTML = `<div class="card">Error: ${resp.error}</div>`;
    return;
  }

  const r = resp.result;
  const color = gaugeColor(r.ethicalDegree);

  $('output').innerHTML = `
    <div class="card">
      <div class="verdict" style="color:${color}">${r.verdict}</div>
      <div class="gauge"><div style="width:${r.ethicalDegree}%; background:${color}"></div></div>
      <div class="hint">Ethical degree: <strong>${r.ethicalDegree}/100</strong></div>
      <div class="metrics">
        <div class="metric"><div class="label">Responses (N)</div><div class="value">${r.n}</div></div>
        <div class="metric"><div class="label">Ethical primes</div><div class="value">${r.totalPrimes}</div></div>
        <div class="metric"><div class="label">Error exponent α</div><div class="value">${fmt(r.alpha)}</div></div>
        <div class="metric"><div class="label">Max |E(x)|</div><div class="value">${fmt(r.maxAbsError, 2)}</div></div>
        <div class="metric"><div class="label">ERH bound C·√N</div><div class="value">${fmt(r.erhBound, 2)}</div></div>
        <div class="metric"><div class="label">Within bound?</div><div class="value">${r.withinBound ? 'Yes' : 'No'}</div></div>
      </div>
    </div>`;
}

$('run').addEventListener('click', run);
