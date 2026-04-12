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



