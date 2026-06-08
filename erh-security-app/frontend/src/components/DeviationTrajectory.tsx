import React from 'react';
import type { EngineCurve } from '../lib/api';

type Props = {
  curve: EngineCurve | null | undefined;
  title?: string;
};

// Minimal dependency-free SVG line chart for the UEBA behavior-deviation
// trajectory (the ERH error term E(x) over situational complexity x).
export const DeviationTrajectory: React.FC<Props> = ({ curve, title = 'Behavior deviation trajectory E(x)' }) => {
  const width = 480;
  const height = 180;
  const pad = 24;

  const points = curve && curve.x.length > 0 ? curve.x.map((x, i) => ({ x, y: curve.y[i] ?? 0 })) : [];

  let path = '';
  if (points.length > 0) {
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys, 0);
    const maxY = Math.max(...ys, 0);
    const spanX = maxX - minX || 1;
    const spanY = maxY - minY || 1;
    const sx = (x: number) => pad + ((x - minX) / spanX) * (width - 2 * pad);
    const sy = (y: number) => height - pad - ((y - minY) / spanY) * (height - 2 * pad);
    path = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${sx(p.x).toFixed(1)} ${sy(p.y).toFixed(1)}`).join(' ');
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 shadow-sm">
      <h2 className="text-sm font-medium text-slate-200">{title}</h2>
      {points.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400">No trajectory data.</p>
      ) : (
        <svg className="mt-3 w-full" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="deviation trajectory">
          <line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} stroke="#334155" strokeWidth={1} />
          <line x1={pad} y1={pad} x2={pad} y2={height - pad} stroke="#334155" strokeWidth={1} />
          <path d={path} fill="none" stroke="#38bdf8" strokeWidth={1.5} />
        </svg>
      )}
      <p className="mt-2 text-xs text-slate-500">x = situational complexity, y = cumulative behavioral error</p>
    </div>
  );
};
