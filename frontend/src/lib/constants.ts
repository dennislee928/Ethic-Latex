export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ROUTES = {
  DASHBOARD: '/',
  EDITOR: '/editor',
  SIMULATION: '/simulation',
  SETTINGS: '/settings',
} as const

