import apiClient from './client'
import type {
  AnalysisSummary,
  AnalysisCurves,
  HeatmapResponse,
  HealthMonitorResponse,
  DashboardStats,
  JudgeType,
} from '@/types/dashboard'
import type { LatexRule } from '@/types/latex'

export const dashboardApi = {
  // Get analysis summary
  getSummary: async (judgeType: JudgeType = 'COMBINED'): Promise<AnalysisSummary> => {
    const response = await apiClient.get('/analysis/summary', {
      params: { judge_type: judgeType },
    })
    return response.data
  },

  // Get analysis curves
  getCurves: async (judgeType: JudgeType = 'COMBINED'): Promise<AnalysisCurves> => {
    const response = await apiClient.get('/analysis/curves', {
      params: { judge_type: judgeType },
    })
    return response.data
  },

  // Get heatmap data
  getHeatmap: async (judgeType: JudgeType = 'COMBINED', bins: number = 10): Promise<HeatmapResponse> => {
    const response = await apiClient.get('/analysis/heatmap', {
      params: { judge_type: judgeType, bins },
    })
    return response.data
  },

  getHealth: async (judgeType: JudgeType = 'COMBINED'): Promise<HealthMonitorResponse> => {
    const response = await apiClient.get('/analysis/health', {
      params: { judge_type: judgeType },
    })
    return response.data
  },

  getStats: async (): Promise<DashboardStats> => {
    const [summaryResponse, rulesResponse] = await Promise.all([
      apiClient.get<AnalysisSummary>('/analysis/summary', {
        params: { judge_type: 'COMBINED' },
      }),
      apiClient.get<LatexRule[]>('/api/v1/rules/'),
    ])

    const summary = summaryResponse.data
    const rules = rulesResponse.data
    const totalRules = rules.length
    const activeRules = rules.filter((rule) => rule.is_active).length
    const passRate = summary.num_samples > 0
      ? Math.max(0, (summary.num_samples - summary.num_primes) / summary.num_samples)
      : 0

    return {
      total_rules: totalRules,
      active_rules: activeRules,
      pass_rate: passRate,
      total_violations: summary.num_primes,
      critical_violations: summary.num_primes,
    }
  },
}
