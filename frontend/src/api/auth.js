/**
 * LinguaChat — Auth API
 *
 * Wraps POST /auth/register and POST /auth/login.
 * See: docs/api-contract.md § 1 & 2
 * Implementation: Ahmed Alammari
 */

import { apiClient } from './client.js'

/**
 * Register a new user.
 * @param {{ username: string, password: string, preferred_language: string }} data
 * @returns {Promise<{ id, username, preferred_language, created_at }>}
 */
export async function register(data) {
  return apiClient.post('/auth/register', data)
}

/**
 * Login and receive a JWT token.
 * @param {{ username: string, password: string }} data
 * @returns {Promise<{ access_token, token_type, expires_in }>}
 */
export async function login(data) {
  return apiClient.post('/auth/login', data)
}
