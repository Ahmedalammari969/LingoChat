/**
 * LinguaChat — Auth Service
 *
 * Manages token storage and user session.
 * Decodes JWT payload to guarantee user ID, username, and preferred language are always present.
 * Implementation: Ahmed Alammari
 */

const TOKEN_KEY = 'linguachat_token'
const USER_KEY = 'linguachat_user'

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1]
    if (!base64Url) return null
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (e) {
    try {
      return JSON.parse(atob(token.split('.')[1]))
    } catch {
      return null
    }
  }
}

export const authService = {
  /** Store JWT token after login and extract user payload. */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
    const payload = parseJwt(token)
    if (payload) {
      const user = {
        id: payload.sub || payload.user_id || payload.id,
        username: payload.username || payload.sub,
        preferred_language: payload.preferred_language || 'ar',
      }
      this.setUser(user)
    }
  },

  /** Get stored JWT token. */
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  },

  /** Check if user is logged in. */
  isAuthenticated() {
    return !!localStorage.getItem(TOKEN_KEY)
  },

  /** Store user profile. */
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  /** Get stored user profile. */
  getUser() {
    const raw = localStorage.getItem(USER_KEY)
    if (raw) {
      try {
        const u = JSON.parse(raw)
        if (u && (u.id || u.username)) return u
      } catch {}
    }
    const token = this.getToken()
    if (token) {
      const payload = parseJwt(token)
      if (payload) {
        return {
          id: payload.sub || payload.user_id || payload.id,
          username: payload.username || payload.sub,
          preferred_language: payload.preferred_language || 'ar',
        }
      }
    }
    return null
  },

  /** Clear session (logout). */
  logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}
