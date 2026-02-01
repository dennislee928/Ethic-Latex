import apiClient from './client'
import type { LatexRule, LatexRuleCreate, LatexRuleUpdate } from '@/types/latex'

export const rulesApi = {
  // Get all rules
  list: async (): Promise<LatexRule[]> => {
    const response = await apiClient.get('/api/v1/rules/')
    return response.data
  },

  // Get a specific rule
  get: async (id: number): Promise<LatexRule> => {
    const response = await apiClient.get(`/api/v1/rules/${id}`)
    return response.data
  },

  // Create a new rule
  create: async (rule: LatexRuleCreate): Promise<LatexRule> => {
    const response = await apiClient.post('/api/v1/rules/', rule)
    return response.data
  },

  // Update a rule
  update: async (id: number, rule: LatexRuleUpdate): Promise<LatexRule> => {
    const response = await apiClient.put(`/api/v1/rules/${id}`, rule)
    return response.data
  },

  // Delete a rule
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/rules/${id}`)
  },
}

