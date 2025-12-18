import React from 'react';
import type { HeatmapResponse } from '../lib/api';

type Props = {
  data: HeatmapResponse | null;
  loading: boolean;
  error: string | null;
};

export const ComplexityHeatmap: React.FC<Props> = ({ data, loading, error }) => {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 shadow-sm">
      <h2 className="text-sm font-medium text-slate-200">Complexity–Δ Heatmap</h2>
      {loading && <p className="mt-3 text-sm text-slate-400">Loading heatmap…</p>}
      {error && !loading && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {!loading && !error && data && (
        <div className="mt-3 text-xs text-slate-300">
          <div className="mb-2 flex justify-between text-slate-400">
            <span>Bins: {data.cells.length}</span>
            <span>Judge: {data.judge_type}</span>
          </div>
          <div className="grid grid-cols-4 gap-1">
            {data.cells.map((cell) => {
              const intensity = Math.min(1, Math.abs(cell.delta_mean));
              const bg =
                cell.delta_mean >= 0
                  ? `rgba(34,197,94,${0.2 + 0.7 * intensity})`
                  : `rgba(248,113,113,${0.2 + 0.7 * intensity})`;
              return (
                <div
                  key={cell.complexity_bin}
                  className="rounded px-1 py-1 text-[10px]"
                  style={{ backgroundColor: bg }}
                >
                  <div>c≈{cell.complexity_bin.toFixed(1)}</div>
                  <div>Δ̄={cell.delta_mean.toFixed(2)}</div>
                  <div>n={cell.count}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};


