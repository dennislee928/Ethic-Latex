export type SimulationStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface Simulation {
  id: number
  status: SimulationStatus
  result_path: string | null
  config: SimulationConfig
  created_at: string
  completed_at: string | null
}

export interface SimulationConfig {
  num_actions: number
  complexity_dist: 'zipf' | 'uniform' | 'power_law'
  tau?: number
}

export interface SimulationCreate {
  num_actions?: number
  complexity_dist?: 'zipf' | 'uniform' | 'power_law'
  tau?: number
}

export interface SimulationResult {
  mistake_rate: number
  ethical_primes_count: number
  analysis: SimulationAnalysis
  config: SimulationConfig
}

export interface SimulationAnalysis {
  estimated_exponent: number
  alpha_ci_low: number
  alpha_ci_high: number
  erh_satisfied: boolean
  r_squared: number
  growth_rate: string
}

