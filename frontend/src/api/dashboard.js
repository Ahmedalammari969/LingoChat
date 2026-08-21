/**
 * LinguaChat — Dashboard API
 *
 * See: docs/api-contract.md § 7
 * Implementation: Ahmed Alammari
 */

import { apiClient } from './client.js'

/** GET /dashboard/stats */
export async function getStats() {
  return apiClient.get('/dashboard/stats')
}
