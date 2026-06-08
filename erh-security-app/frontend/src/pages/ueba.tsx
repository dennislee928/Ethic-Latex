import React, { useMemo, useState } from 'react';
import { Layout } from '../components/Layout';
import { DeviationTrajectory } from '../components/DeviationTrajectory';
import type { EngineEvaluateResponse, UEBAEvent } from '../lib/api';
import { evaluateUeba } from '../lib/api';

// A small demo dataset: a user with a normal baseline, then an off-hours bulk
// download of sensitive data (the insider-threat signal). Editable as JSON.
const DEMO_EVENTS: UEBAEvent[] = [
  { user: 'alice', hour: 10, bytes_downloaded: 120, is_baseline: true },
  { user: 'alice', hour: 11, bytes_downloaded: 90, is_baseline: true },
  { user: 'alice', hour: 14, bytes_downloaded: 110, is_baseline: true },
  { user: 'alice', hour: 9, bytes_downloaded: 130 },
  { user: 'alice', hour: 2, bytes_downloaded: 8000, sensitive: true },
  { user: 'alice', hour: 3, bytes_downloaded: 9500, sensitive: true }
];

const UebaPage: React.FC = () => {
  const [raw, setRaw] = useState<string>(JSON.stringify(DEMO_EVENTS, null, 2));
  const [result, setResult] = useState<EngineEvaluateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const riskColor = useMemo(() => {
    if (!result) return 'text-slate-200';
    if (result.risk_score >= 60) return 'text-red-400';
    if (result.risk_score >= 30) return 'text-amber-400';
    return 'text-emerald-400';
  }, [result]);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const events = JSON.parse(raw) as UEBAEvent[];
      const res = await evaluateUeba(events);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to evaluate UEBA events.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1 className="mb-4 text-lg font-semibold text-slate-100">UEBA Insider-Threat (ERH)</h1>
      <p className="mb-4 max-w-2xl text-sm text-slate-400">
        Builds a per-user behavioral convergence domain from baseline events, then measures how far
        subsequent behavior deviates. A rising error trajectory (ERH violated) signals a slow
        insider drift rather than isolated noise.
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <label className="text-sm text-slate-300">Events (JSON)</label>
          <textarea
            className="mt-2 h-72 w-full rounded border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-100"
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
          />
          <button
            className="mt-3 rounded bg-sky-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50"
            onClick={() => void run()}
            disabled={loading}
          >
            {loading ? 'Evaluating…' : 'Evaluate'}
          </button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </div>

        <div className="space-y-4">
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
            <h2 className="text-sm font-medium text-slate-200">Risk verdict</h2>
            {result ? (
              <div className="mt-3 space-y-1 text-sm">
                <p className={`text-2xl font-bold ${riskColor}`}>{result.risk_score.toFixed(1)}</p>
                <p className="text-slate-400">
                  ERH satisfied: <span className="text-slate-200">{String(result.erh_satisfied)}</span>
                </p>
                <p className="text-slate-400">
                  estimated alpha: <span className="text-slate-200">{result.estimated_exponent.toFixed(3)}</span>{' '}
                  (~0.5 healthy)
                </p>
                <p className="text-slate-400">
                  flagged events: <span className="text-slate-200">{result.num_primes}</span> / {result.num_samples}
                </p>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-400">Run an evaluation to see results.</p>
            )}
          </div>
          <DeviationTrajectory curve={result?.error_curve} />
        </div>
      </div>
    </Layout>
  );
};

export default UebaPage;
