import apiClient from './client'
import type { Simulation, SimulationCreate, SimulationFigure, SimulationResult } from '@/types/simulation'

export const simulateApi = {
  // Create a new simulation
  create: async (config: SimulationCreate): Promise<Simulation> => {
    const response = await apiClient.post('/api/v1/simulations/', config)
    return response.data
  },

  // List all simulations
  list: async (): Promise<Simulation[]> => {
    const response = await apiClient.get('/api/v1/simulations/')
    return response.data
  },

  // Get a specific simulation
  get: async (id: number): Promise<Simulation> => {
    const response = await apiClient.get(`/api/v1/simulations/${id}`)
    return response.data
  },

  // Get simulation results
  getResults: async (id: number): Promise<SimulationResult> => {
    const response = await apiClient.get(`/api/v1/simulations/${id}/results`)
    return response.data
  },

  // Get simulation figures
  getFigures: async (id: number): Promise<{ figures: Array<{ name: string; path: string }> }> => {
    const response = await apiClient.get<{ figures: SimulationFigure[] }>(`/api/v1/simulations/${id}/figures`)
    return response.data
  },
}
