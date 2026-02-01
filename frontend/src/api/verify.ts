import apiClient from './client'
import type { ValidationResult } from '@/types/latex'

export const verifyApi = {
  // Verify LaTeX content
  verify: async (latexContent: string, ruleId?: number): Promise<ValidationResult> => {
    const response = await apiClient.post('/api/v1/verify/', { latex_content: latexContent }, {
      params: ruleId ? { rule_id: ruleId } : {},
    })
    return response.data
  },

  // Verify a rule by ID
  verifyRule: async (ruleId: number): Promise<ValidationResult> => {
    const response = await apiClient.post(`/api/v1/verify/rule/${ruleId}`)
    return response.data
  },

  // Get validation result for a rule
  getValidation: async (ruleId: number): Promise<ValidationResult> => {
    const response = await apiClient.get(`/api/v1/verify/rule/${ruleId}/validate`)
    return response.data
  },
}

