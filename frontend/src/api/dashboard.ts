import apiClient from './client'
import type {
  AnalysisSummary,
  AnalysisCurves,
  HeatmapResponse,
  DashboardStats,
  JudgeType,
} from '@/types/dashboard'

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

  // Get dashboard stats (placeholder - implement when backend endpoint is ready)
  getStats: async (): Promise<DashboardStats> => {
    // For now, return mock data
    return {
      total_rules: 0,
      active_rules: 0,
      pass_rate: 0.95,
      total_violations: 0,
      critical_violations: 0,
    }
  },
}

