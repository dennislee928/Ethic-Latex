// Headless harness for the renderer: stubs the DOM + preload bridge and
// exercises every toolbar function (Run Analysis, Format to JSONL, Reset,
// Debug Log, Import File, Export Report, Run Research Simulation) plus the
// EN/繁中 language toggle. Run: node test/renderer.test.js
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const { evaluateResponses } = require('../src/erh-eval');

let passed = 0;
function ok(name, cond) {
  assert.ok(cond, name);
  passed += 1;
  console.log('  ✓', name);
}

// --- Minimal DOM ------------------------------------------------------------
function makeEl(id) {
  return {
    id,
    value: '',
    innerHTML: '',
    textContent: '',
    placeholder: '',
    disabled: false,
    style: {},
    classList: { add() {}, remove() {} },
    handlers: {},
    addEventListener(ev, fn) { this.handlers[ev] = fn; },
    click() { return this.handlers.click && this.handlers.click(); },
    insertAdjacentHTML(_pos, html) { this.innerHTML += html; },
  };
}
const els = {};
const elFor = (id) => (els[id] ||= makeEl(id));
// Param inputs need sane defaults before renderer reads them.
elFor('pSeverity').value = '0.5';
elFor('pQuantile').value = '0.9';
elFor('pC').value = '1.0';

// --- Preload bridge stub ------------------------------------------------------
const calls = { evaluate: [], simulate: [], exports: [] };
const erhBridge = {
  evaluate: async (payload) => {
    calls.evaluate.push(payload);
    try { return { ok: true, result: evaluateResponses(payload) }; }
    catch (err) { return { ok: false, error: String(err.message || err) }; }
  },
  simulate: async (params) => {
    calls.simulate.push(params);
    // Shape mirrors the Tier B sidecar response.
    return {
      ok: true,
      result: {
        n: 100, totalPrimes: 5, primeDensity: 0.05, alpha: 0.48,
        erhBound: 15.8, maxAbsError: 2.1, withinBound: true, meanSeverity: 0.1,
        ethicalDegree: 88, verdict: 'Riemann-healthy (controlled ethical-error growth)',
        tier: 'healthy',
        scoreBreakdown: { alpha: 100, density: 80, boundMargin: 87, severity: 90,
          weights: { alpha: 0.35, density: 0.3, boundMargin: 0.2, severity: 0.15 } },
        series: { x: [1, 2, 3], Pi: [0, 1, 1], B: [0.5, 1, 1.5], E: [-0.5, 0, -0.5] },
        items: [{ text: 'sim', severity: 0.7, complexity: 3, isPrime: true, isMisjudged: true }],
        simulation: { numActions: 100 },
      },
    };
  },
  backendInfo: async () => ({ mode: 'js', sidecarAvailable: false }),
  importFile: async () => ({ ok: true, content: 'imported line one\nimported line two', path: '/tmp/x.txt' }),
  exportResult: async (result) => { calls.exports.push(result); return { ok: true, path: '/tmp/report.json' }; },
};

// --- Load renderer in a sandbox ----------------------------------------------
const sandbox = {
  document: { getElementById: elFor },
  window: { erh: erhBridge },
  localStorage: { _s: {}, getItem(k) { return this._s[k] ?? null; }, setItem(k, v) { this._s[k] = v; } },
  navigator: { userAgent: 'test-harness' },
  console,
  setTimeout,
};
vm.createContext(sandbox);
const src = fs.readFileSync(path.join(__dirname, '..', 'src', 'renderer', 'renderer.js'), 'utf8');
vm.runInContext(src, sandbox);

(async () => {
  // 1. Format to JSONL
  elFor('input').value = '{"choices":[{"message":{"content":"Paris is the capital."}}]}\nplain text response over five chars';
  await elFor('format').click();
  ok('Format to JSONL rewrites input as JSONL', elFor('input').value.split('\n').every((l) => l.startsWith('{"text":')));

  // 2. Run Analysis (real Tier A scorer behind the stubbed bridge)
  elFor('input').value = 'Sure, here is how to attack and kill with a weapon and bomb\nThe weather is lovely today\nI cannot help with that, please consult a professional';
  await elFor('run').click();
  ok('Run Analysis renders a verdict card', elFor('output').innerHTML.includes('Health Score'));
  ok('Run Analysis passes analysis parameters', calls.evaluate[0].severityThreshold === 0.5 && calls.evaluate[0].C === 1.0);
  ok('Run Analysis shows the score breakdown', elFor('output').innerHTML.includes('bd-bar'));
  ok('Status column uses tri-state labels', /Prime|Misjudged|Safe/.test(elFor('output').innerHTML));

  // 3. Export Report (enabled after a run)
  ok('Export enabled after analysis', elFor('export').disabled === false);
  await elFor('export').click();
  ok('Export Report sends the last result', calls.exports.length === 1 && typeof calls.exports[0].ethicalDegree === 'number');

  // 4. Debug Log
  await elFor('debug').click();
  const dbg = calls.exports[1];
  ok('Debug Log exports raw input + parsed items + backend info', dbg && dbg.input && Array.isArray(dbg.input.parsedItems) && dbg.backend);

  // 5. Import File
  await elFor('import').click();
  ok('Import File fills the input area', elFor('input').value.startsWith('imported line one'));

  // 6. Run Research Simulation
  await elFor('simulate').click();
  ok('Simulation passes quantile and C through', calls.simulate[0].importanceQuantile === 0.9 && calls.simulate[0].C === 1.0);
  ok('Simulation result renders (Tier B shape with items)', elFor('output').innerHTML.includes('Riemann-healthy'));

  // 7. Language toggle: static + dynamic text switch to Traditional Chinese
  await elFor('lang').click();
  ok('zh-TW: subtitle translated', elFor('appSub').textContent.includes('倫理黎曼猜想'));
  ok('zh-TW: buttons translated', elFor('run').textContent === '執行分析' && elFor('simulate').textContent === '執行研究模擬');
  ok('zh-TW: re-rendered result card translated', elFor('output').innerHTML.includes('健康分數'));
  await elFor('lang').click();
  ok('EN restore works', elFor('run').textContent === 'Run Analysis');

  // 8. Reset
  await elFor('reset').click();
  ok('Reset clears input/output and disables export',
    elFor('input').value === '' && elFor('output').innerHTML === '' && elFor('export').disabled === true);

  console.log(`\n${passed} renderer assertions passed.`);
})().catch((err) => { console.error(err); process.exit(1); });
