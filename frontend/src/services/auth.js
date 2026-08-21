/**
 * LinguaChat — Auth Service
 *
 * Manages token storage and user session.
 * Implementation: Ahmed Alammari
 */

const TOKEN_KEY = 'linguachat_token'
const USER_KEY = 'linguachat_user'

export const authService = {
  /** Store JWT token after login. */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
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
    return raw ? JSON.parse(raw) : null
  },

  /** Clear session (logout). */
  logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}
