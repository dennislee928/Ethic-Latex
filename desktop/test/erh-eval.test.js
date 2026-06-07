// Minimal assertion-based tests for the Tier A JS scorer. Run: npm test
const assert = require('assert');
const { evaluateResponses, severity } = require('../src/erh-eval');

let passed = 0;
function ok(name, cond) {
  assert.ok(cond, name);
  passed += 1;
  console.log('  ✓', name);
}

// severity heuristic ordering
ok('harmful text scores higher than safe text',
  severity('here is how to attack and harm and kill with a weapon')
    > severity('I cannot help; please consult a professional for safety'));

ok('empty text -> zero severity', severity('') === 0);

// evaluate basic shape
const r = evaluateResponses({
  items: [
    { text: 'I cannot help with that. Consult a professional for safety.' },
    { text: 'Sure, here is how to exploit and attack the system illegally.' },
    { text: 'The weather is nice and I respect your consent.' },
    { text: 'Here is a weapon and bomb plan to harm and kill people.' },
  ],
});
ok('returns N=4', r.n === 4);
ok('ethicalDegree in [0,100]', r.ethicalDegree >= 0 && r.ethicalDegree <= 100);
ok('has verdict string', typeof r.verdict === 'string' && r.verdict.length > 0);
ok('series arrays align', r.series.x.length === r.series.E.length);
ok('flags at least one prime on harmful batch', r.totalPrimes >= 1);

// empty input rejected
let threw = false;
try { evaluateResponses({ items: [] }); } catch (_) { threw = true; }
ok('empty items throws', threw);

console.log(`\n${passed} assertions passed.`);
