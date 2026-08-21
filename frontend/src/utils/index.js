/**
 * LinguaChat — Utility Functions
 * Implementation: Ahmed Alammari
 */

/**
 * Format an ISO 8601 timestamp for display.
 * @param {string} isoString
 * @returns {string} e.g., "3:45 PM"
 */
export function formatTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format an ISO 8601 timestamp as a date + time.
 * @param {string} isoString
 * @returns {string}
 */
export function formatDateTime(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleString()
}

/**
 * Truncate a string to maxLength with ellipsis.
 * @param {string} str
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(str, maxLength = 50) {
  if (!str || str.length <= maxLength) return str
  return str.slice(0, maxLength) + '…'
}

/**
 * Map ISO 639-1 code to a human-readable language name.
 * Extend as needed.
 * @param {string} code
 * @returns {string}
 */
export function langCodeToName(code) {
  const map = {
    ar: 'Arabic',
    en: 'English',
    fr: 'French',
    de: 'German',
    es: 'Spanish',
    zh: 'Chinese',
    ru: 'Russian',
    ja: 'Japanese',
    pt: 'Portuguese',
    it: 'Italian',
  }
  return map[code] || code.toUpperCase()
}

/**
 * Get a flag emoji for common language codes.
 * @param {string} code
 * @returns {string}
 */
export function langCodeToFlag(code) {
  const map = {
    ar: '🇸🇦',
    en: '🇺🇸',
    fr: '🇫🇷',
    de: '🇩🇪',
    es: '🇪🇸',
    zh: '🇨🇳',
    ru: '🇷🇺',
    ja: '🇯🇵',
    pt: '🇧🇷',
    it: '🇮🇹',
  }
  return map[code] || '🌐'
}
