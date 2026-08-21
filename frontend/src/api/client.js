/**
 * LinguaChat — API Base Client
 *
 * Centralized HTTP client for all REST API calls.
 * Uses native fetch. Token is read from localStorage.
 *
 * Base URL is read from VITE_API_BASE_URL env var.
 * See: docs/api-contract.md for all endpoints.
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

  const response = await fetch(url, { ...options, headers })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({
      error: { code: 'NETWORK_ERROR', message: 'Request failed' },
    }))
    const error = new Error(errorBody?.error?.message || 'Request failed')
    error.code = errorBody?.error?.code
    error.status = response.status
    throw error
  }

  // 204 No Content
  if (response.status === 204) return null

  return response.json()
}

export const apiClient = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: 'DELETE' }),
}
