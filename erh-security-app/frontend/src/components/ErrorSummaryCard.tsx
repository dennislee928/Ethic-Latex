import React from 'react';
import type { AnalysisSummary, JudgeType } from '../lib/api';

type Props = {
  summary: AnalysisSummary | null;
  judgeType: JudgeType;
  loading: boolean;
  error: string | null;
};

export const ErrorSummaryCard: React.FC<Props> = ({ summary, judgeType, loading, error }) => {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-slate-200">Judge Summary</h2>
        <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">{judgeType}</span>
      </div>
      {loading && <p className="mt-3 text-sm text-slate-400">Loading summary…</p>}
      {error && !loading && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {!loading && !error && summary && (
        <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-slate-400">Samples</p>
            <p className="text-lg font-semibold">{summary.num_samples}</p>
          </div>
          <div>
            <p className="text-slate-400">Ethical primes</p>
            <p className="text-lg font-semibold">{summary.num_primes}</p>
          </div>
          <div>
            <p className="text-slate-400">Estimated α</p>
            <p className="text-lg font-semibold">
              {summary.estimated_alpha != null ? summary.estimated_alpha.toFixed(3) : '—'}
            </p>
          </div>
          <div>
            <p className="text-slate-400">R²</p>
            <p className="text-lg font-semibold">
              {summary.r_squared != null ? summary.r_squared.toFixed(3) : '—'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};


