import React from 'react';
import type { AnalysisCurves } from '../lib/api';

type Props = {
  curves: AnalysisCurves | null;
  loading: boolean;
  error: string | null;
};

export const ErhCurveChart: React.FC<Props> = ({ curves, loading, error }) => {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 shadow-sm">
      <h2 className="text-sm font-medium text-slate-200">ERH Curves</h2>
      {loading && <p className="mt-3 text-sm text-slate-400">Loading curves…</p>}
      {error && !loading && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {!loading && !error && curves && (
        <div className="mt-3 space-y-2 text-xs text-slate-300">
          <p className="text-slate-400">Pi(x) points: {curves.pi_curve.length}</p>
          <p className="truncate text-slate-400">
            First Pi(x):{' '}
            {curves.pi_curve.length > 0 ? `(${curves.pi_curve[0].x}, ${curves.pi_curve[0].y})` : '—'}
          </p>
          <p className="text-slate-400">E(x) points: {curves.error_curve.length}</p>
          <p className="truncate text-slate-400">
            First E(x):{' '}
            {curves.error_curve.length > 0
              ? `(${curves.error_curve[0].x}, ${curves.error_curve[0].y})`
              : '—'}
          </p>
          <p className="mt-2 text-slate-500">
            For production, replace this block with a proper chart library (e.g. lightweight canvas or SVG).
          </p>
        </div>
      )}
    </div>
  );
};


