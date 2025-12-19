export type JudgeType = 'PIPELINE' | 'HUMAN' | 'COMBINED'

export interface AnalysisSummary {
  judge_type: JudgeType
  num_samples: number
  num_primes: number
  estimated_alpha: number | null
  r_squared: number | null
}

export interface CurvePoint {
  x: number
  y: number
}

export interface AnalysisCurves {
  pi_curve: CurvePoint[]
  error_curve: CurvePoint[]
}

export interface HeatmapCell {
  complexity_bin: number
  delta_mean: number
  count: number
}

export interface HeatmapResponse {
  judge_type: JudgeType
  cells: HeatmapCell[]
}

export interface DashboardStats {
  total_rules: number
  active_rules: number
  pass_rate: number
  total_violations: number
  critical_violations: number
}

export interface ActivityLog {
  id: number
  timestamp: string
  type: string
  message: string
  severity: 'info' | 'warning' | 'error'
}

