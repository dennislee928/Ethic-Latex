import axios, { AxiosInstance, AxiosError } from 'axios'
import { API_BASE_URL } from '@/lib/constants'

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data as { detail?: string }
      
      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token')
          break
        case 403:
          console.error('Forbidden:', data.detail || 'Access denied')
          break
        case 404:
          console.error('Not found:', data.detail || 'Resource not found')
          break
        case 500:
          console.error('Server error:', data.detail || 'Internal server error')
          break
        default:
          console.error('Request failed:', data.detail || error.message)
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error:', 'No response from server')
    } else {
      // Something else happened
      console.error('Error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default apiClient

