import { create } from 'zustand'

interface AuthState {
  token: string | null
  setToken: (token: string | null) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('auth_token'),
  setToken: (token: string | null) => {
    if (token) {
      localStorage.setItem('auth_token', token)
    } else {
      localStorage.removeItem('auth_token')
    }
    set({ token })
  },
  clearAuth: () => {
    localStorage.removeItem('auth_token')
    set({ token: null })
  },
}))

