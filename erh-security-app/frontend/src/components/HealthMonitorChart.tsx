import React from 'react';
import type { HealthMonitorResponse, JudgeType } from '../lib/api';

type Props = {
  data: HealthMonitorResponse | null;
  judgeType: JudgeType;
  loading: boolean;
  error: string | null;
};

export const HealthMonitorChart: React.FC<Props> = ({
  data,
  judgeType,
  loading,
  error,
}) => {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 shadow-sm">
      <h2 className="text-sm font-medium text-slate-200">Health Monitor</h2>
      <p className="mt-1 text-xs text-slate-400">
        E(x) vs Riemann bound x<sup>1/2</sup>. Alert if |E(x)| violates bound.
      </p>
      {loading && <p className="mt-3 text-sm text-slate-400">Loading…</p>}
      {error && !loading && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {!loading && !error && data && (
        <div className="mt-3 space-y-2 text-xs text-slate-300">
          <div
            className={`inline-flex items-center gap-2 rounded px-2 py-1 ${
              data.violation
                ? 'bg-red-900/40 text-red-300'
                : 'bg-emerald-900/40 text-emerald-300'
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                data.violation ? 'bg-red-400' : 'bg-emerald-400'
              }`}
            />
            {data.violation
              ? `Alert: E(x) violates Riemann bound at ${data.violation_points.length} point(s)`
              : 'OK: E(x) within Riemann bound'}
          </div>
          <p className="text-slate-400">
            E(x) points: {data.error_curve.length} | Riemann bound: {data.riemann_bound.length}
          </p>
        </div>
      )}
    </div>
  );
};
