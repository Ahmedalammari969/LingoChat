/**
 * LinguaChat — useAuth Hook
 *
 * Provides auth state and login/logout actions.
 * Implementation: Ahmed Alammari — TASK-02-AHMED
 */

import { useState, useCallback } from 'react'
import { authService } from '../services/auth.js'
import { login as apiLogin, register as apiRegister } from '../api/auth.js'

export function useAuth() {
  const [user, setUser] = useState(() => authService.getUser())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const login = useCallback(async (username, password) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiLogin({ username, password })
      authService.setToken(result.access_token)
      const userData = { username }
      authService.setUser(userData)
      setUser(userData)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (username, password, preferred_language) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiRegister({ username, password, preferred_language })
      authService.setUser(result)
      setUser(result)
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  return { user, loading, error, login, register, logout, isAuthenticated: authService.isAuthenticated() }
}
