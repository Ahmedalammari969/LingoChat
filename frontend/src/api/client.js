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

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  if (typeof window !== 'undefined') {
    return '/api/v1'
  }
  return 'http://localhost:8000/api/v1'
}

const BASE_URL = getBaseUrl()

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
async function executeFetch(url, options, headers) {
  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    localStorage.removeItem('linguachat_token')
    localStorage.removeItem('linguachat_user')
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({
      error: { code: 'HTTP_ERROR', message: response.statusText || 'Request failed' },
    }))
    const rawMsg = errorBody?.error?.message || errorBody?.detail || response.statusText || 'Request failed'
    const message = Array.isArray(rawMsg) ? rawMsg.map(e => e.msg || JSON.stringify(e)).join(', ') : typeof rawMsg === 'string' ? rawMsg : JSON.stringify(rawMsg)
    const error = new Error(message)
    error.code = errorBody?.error?.code || `HTTP_${response.status}`
    error.status = response.status
    throw error
  }

  if (response.status === 204) return null
  return response.json()
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...authHeaders(),
    ...options.headers,
  }

  const primaryUrl = `${BASE_URL}${path}`

  try {
    return await executeFetch(primaryUrl, options, headers)
  } catch (err) {
    // If network error occurred on relative URL, try direct backend port 8000
    if ((!err.status && !err.code) && typeof window !== 'undefined' && window.location?.hostname) {
      const fallbackUrl = `http://${window.location.hostname}:8000/api/v1${path}`
      try {
        return await executeFetch(fallbackUrl, options, headers)
      } catch (fallbackErr) {
        if (!fallbackErr.status && !fallbackErr.code) {
          fallbackErr.code = 'NETWORK_ERROR'
          fallbackErr.message = 'تعذر الاتصال بالخادم، يرجى التأكد من تشغيل الباك إند.'
        }
        throw fallbackErr
      }
    }

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
