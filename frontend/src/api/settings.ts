import apiClient from './client'
import type { UserSettings, UserPreferences } from '@/types/settings'

export const settingsApi = {
  // Get user settings
  get: async (): Promise<UserSettings> => {
    const response = await apiClient.get('/api/v1/settings/')
    return response.data
  },

  // Update user settings
  update: async (preferences: UserPreferences): Promise<UserSettings> => {
    const response = await apiClient.put('/api/v1/settings/', preferences)
    return response.data
  },
}

