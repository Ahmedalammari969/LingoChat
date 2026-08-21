/**
 * LinguaChat — Type Definitions (JSDoc)
 *
 * Shared type documentation for frontend data shapes.
 * Mirrors the contracts in docs/api-contract.md and docs/websocket-contract.md.
 * Implementation: Ahmed Alammari
 */

/**
 * @typedef {Object} User
 * @property {string} id - UUID
 * @property {string} username
 * @property {string} preferred_language - ISO 639-1 code
 * @property {string} created_at - ISO 8601
 */

/**
 * @typedef {Object} Room
 * @property {string} id - UUID
 * @property {string} name
 * @property {string} invitation_link
 * @property {string} created_by - User UUID
 * @property {string} created_at - ISO 8601
 */

/**
 * @typedef {Object} ChatMessage
 * @property {string} id - UUID
 * @property {string} room_id - UUID
 * @property {string} sender_id - UUID
 * @property {string} sender_username
 * @property {string} original_text
 * @property {string} original_language - ISO 639-1
 * @property {string} translated_text
 * @property {string} target_language - ISO 639-1
 * @property {string} translation_source - 'libretranslate' | 'google' | 'cache' | 'none'
 * @property {string} sent_at - ISO 8601
 */

/**
 * @typedef {Object} WSMessage
 * @property {'JOIN'|'LEAVE'|'TEXT_MESSAGE'|'TYPING'|'HEARTBEAT'|'ERROR'} type
 * @property {Object} payload
 * @property {string} timestamp - ISO 8601
 * @property {string} room_id - UUID
 */

/**
 * @typedef {Object} DashboardStats
 * @property {number} total_users
 * @property {number} total_rooms
 * @property {number} total_messages
 * @property {number} total_translations
 * @property {number} active_connections
 */

/**
 * @typedef {Object} ApiError
 * @property {string} code
 * @property {string} message
 * @property {number} status - HTTP status code
 */
