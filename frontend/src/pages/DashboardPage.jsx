/**
 * LinguaChat — Dashboard Page (Placeholder)
 *
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 *
 * When implementing:
 * - Use api/dashboard.js: GET /api/v1/dashboard/stats
 * - Display: total_users, total_rooms, total_messages, total_translations, active_connections
 * - Requires JWT Authorization header
 * - Auto-refresh every 30 seconds or on demand
 */

import React from 'react'

export default function DashboardPage() {
  return (
    <div className="placeholder-page">
      <div className="brand-logo">Lingua<span>Chat</span></div>
      <h1>Dashboard</h1>
      <p>System statistics and monitoring</p>
      <span className="placeholder-badge">
        🚧 Dashboard UI — Pending implementation by Ahmed Alammari
      </span>
      <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
        Route: GET /api/v1/dashboard/stats
      </p>
    </div>
  )
}
