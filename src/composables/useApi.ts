// src/composables/useApi.ts
import { ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export function useApi() {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
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
