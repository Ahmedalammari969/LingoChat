/**
 * LinguaChat — Rooms API
 *
 * Wraps room-related REST endpoints.
 * See: docs/api-contract.md § 3, 4, 5, 6
 * Implementation: Ahmed Alammari
 */

import { apiClient } from './client.js'

/** POST /rooms — Create a new room. */
export async function createRoom(name, isPrivate = false) {
  return apiClient.post('/rooms', { name, is_private: isPrivate })
}

/** GET /rooms — List rooms. */
export async function listRooms(limit = 20, offset = 0) {
  return apiClient.get(`/rooms?limit=${limit}&offset=${offset}`)
}

/** POST /rooms/:roomId/join — Join a room. */
export async function joinRoom(roomId) {
  return apiClient.post(`/rooms/${roomId}/join`, {})
}

/**
 * GET /rooms/:roomId/messages — Load message history.
 * @param {string} roomId
 * @param {number} limit
 * @param {string|null} before - ISO8601 cursor for pagination
 */
export async function getRoomMessages(roomId, limit = 50, before = null) {
  const query = [`limit=${limit}`, before ? `before=${before}` : null]
    .filter(Boolean)
    .join('&')
  return apiClient.get(`/rooms/${roomId}/messages?${query}`)
}
