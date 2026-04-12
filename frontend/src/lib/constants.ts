export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  EDITOR: '/editor',
  SIMULATION: '/simulation',
  SETTINGS: '/settings',
} as const
