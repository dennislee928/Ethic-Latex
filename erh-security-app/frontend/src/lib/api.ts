export type JudgeType = 'PIPELINE' | 'HUMAN' | 'COMBINED';

export interface AnalysisSummary {
  judge_type: JudgeType;
  num_samples: number;
  num_primes: number;
  estimated_alpha: number | null;
  r_squared: number | null;
}

export interface CurvePoint {
  x: number;
  y: number;
}

export interface AnalysisCurves {
  pi_curve: CurvePoint[];
  error_curve: CurvePoint[];
}

export interface HeatmapCell {
  complexity_bin: number;
  delta_mean: number;
  count: number;
}

export interface HeatmapResponse {
  judge_type: JudgeType;
  cells: HeatmapCell[];
}

export interface HealthMonitorResponse {
  error_curve: CurvePoint[];
  riemann_bound: CurvePoint[];
  violation: boolean;
  violation_points: CurvePoint[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function getSummary(judgeType: JudgeType): Promise<AnalysisSummary> {
  return fetchJson<AnalysisSummary>(`/analysis/summary?judge_type=${judgeType}`);
}

export async function getCurves(judgeType: JudgeType): Promise<AnalysisCurves> {
  return fetchJson<AnalysisCurves>(`/analysis/curves?judge_type=${judgeType}`);
}

export async function getHeatmap(judgeType: JudgeType): Promise<HeatmapResponse> {
  return fetchJson<HeatmapResponse>(`/analysis/heatmap?judge_type=${judgeType}`);
}

export async function getHealth(judgeType: JudgeType): Promise<HealthMonitorResponse> {
  return fetchJson<HealthMonitorResponse>(`/analysis/health?judge_type=${judgeType}`);
}

// ---------------------------------------------------------------------------
// erh_engine client (standardized ERH evaluation service, REST /v1/*).
// Used by the UEBA dashboard to render behavioral-deviation trajectories.
// ---------------------------------------------------------------------------

const ENGINE_BASE = process.env.NEXT_PUBLIC_ERH_ENGINE_BASE ?? 'http://localhost:8000';

export interface EngineCurve {
  x: number[];
  y: number[];
}

export interface EngineEvaluateResponse {
  erh_satisfied: boolean;
  risk_score: number;
  violation_rate: number;
  max_ratio: number;
  estimated_exponent: number;
  num_samples: number;
  num_primes: number;
  primes: Array<{
    id: string;
    complexity: number;
    delta: number;
    weight: number;
    context: Record<string, unknown>;
  }>;
  error_curve?: EngineCurve | null;
  pi_curve?: EngineCurve | null;
}

export interface UEBAEvent {
  id?: string;
  user: string;
  hour: number;
  bytes_downloaded?: number;
  sensitive?: boolean;
  is_baseline?: boolean;
}

export async function evaluateUeba(events: UEBAEvent[]): Promise<EngineEvaluateResponse> {
  const res = await fetch(`${ENGINE_BASE}/v1/ueba/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ events, params: { include_curves: true } })
  });
  if (!res.ok) {
    throw new Error(`Engine request failed with status ${res.status}`);
  }
  return (await res.json()) as EngineEvaluateResponse;
}



