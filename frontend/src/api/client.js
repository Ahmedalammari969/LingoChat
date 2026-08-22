/**
 * LinguaChat — API Base Client
 *
 * Centralized HTTP client for all REST API calls.
 * Uses native fetch. Token is read from localStorage.
 *
 * Base URL is read from VITE_API_BASE_URL env var (default: /api/v1).
 * See: docs/api-contract.md for all endpoints.
 * Implementation: Ahmed Alammari — TASK-01-AHMED
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * Get stored JWT token.
 * @returns {string|null}
 */
function getToken() {
  return localStorage.getItem('linguachat_token')
}

/**
 * Build Authorization header if token exists.
 * @returns {object}
 */
function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Generic request helper.
 * @param {string} path - API path (e.g., '/auth/login')
 * @param {object} options - fetch options
 * @returns {Promise<any>}
 * @throws {Error} with error.code and error.message from API contract
 */
async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const headers = {
    'Content-Type': 'application/json',
    ...authHeaders(),
    ...options.headers,
  }

  try {
    const response = await fetch(url, { ...options, headers })

    if (response.status === 401) {
      // Clean expired session
      localStorage.removeItem('linguachat_token')
      localStorage.removeItem('linguachat_user')
    }

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({
        error: { code: 'HTTP_ERROR', message: response.statusText || 'Request failed' },
      }))
      const message = errorBody?.detail || errorBody?.error?.message || response.statusText || 'Request failed'
      const error = new Error(typeof message === 'string' ? message : JSON.stringify(message))
      error.code = errorBody?.error?.code || `HTTP_${response.status}`
      error.status = response.status
      throw error
    }

    // 204 No Content
    if (response.status === 204) return null

    return response.json()
  } catch (err) {
    if (!err.status && !err.code) {
      err.code = 'NETWORK_ERROR'
      err.message = 'تعذر الاتصال بالخادم، يرجى التأكد من تشغيل الباك إند.'
    }
    throw err
  }
}

export const apiClient = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: 'DELETE' }),
}
