/**
 * LinguaChat — Dashboard API
 *
 * See: docs/api-contract.md § 7. GET /dashboard/stats
 * Implementation: Ahmed Alammari — TASK-05-AHMED
 */

import { apiClient } from './client.js'

/** GET /dashboard/stats */
export async function getStats() {
  return apiClient.get('/dashboard/stats')
}

/** Alias matching TASK-05 specification: getDashboardStats */
export async function getDashboardStats() {
  return apiClient.get('/dashboard/stats')
}
