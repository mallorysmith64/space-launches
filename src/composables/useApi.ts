// src/composables/useApi.ts
import { ref } from 'vue'

// In production, use relative URLs (same domain)
// In development, check for VITE_API_URL env var, otherwise use localhost:5000
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:5000' : '')

export function useApi() {
  const data = ref<unknown>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        credentials: 'include', // Include cookies for sessions
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.text() // Some endpoints return HTML
      try {
        data.value = JSON.parse(result)
      } catch {
        data.value = result // Fall back to raw text
      }

      return data.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetchApi }
}
