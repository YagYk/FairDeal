/**
 * API service for backend communication.
 * Handles all HTTP requests to the backend API.
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
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
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
    // Handle rate limit errors (429)
    if (error.response?.status === 429) {
      const errorDetail = error.response?.data?.detail || error.message || ''
      const retryAfter = error.response?.headers?.['retry-after'] || '60'
      
      // Store rate limit info for display
      error.rateLimitInfo = {
        message: 'API rate limit exceeded. Please wait before trying again.',
        retryAfter: parseInt(retryAfter),
        detail: errorDetail
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: async (name: string, email: string, password: string) => {
    const response = await api.post('/api/auth/register', {
      name,
      email,
      password,
    })
    return response.data
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

// Profile API
export const profileAPI = {
  getStats: async () => {
    const response = await api.get('/api/profile/stats')
    return response.data
  },

  getAnalyses: async (limit: number = 10) => {
    const response = await api.get(`/api/profile/analyses?limit=${limit}`)
    return response.data
  },
}

// Contract Analysis API
export const contractAPI = {
  analyze: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/contracts/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  ingest: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/contracts/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getKnowledgeBaseStats: async () => {
    const response = await api.get('/api/contracts/stats')
    return response.data
  },

  chat: async (analysisId: string, question: string) => {
    const response = await api.post('/api/contracts/chat', {
      analysis_id: analysisId,
      question: question,
    })
    return response.data
  },
}

export default api
