/**
 * LinguaChat — Login Page (Placeholder)
 *
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 * 
 * When implementing:
 * - Use api/auth.js for POST /auth/login and POST /auth/register
 * - Store JWT in localStorage or context (decide with team)
 * - Redirect to /rooms on success
 * - Handle errors using the standard error format from api-contract.md
 * - Collect: username, password, preferred_language
 */

import React from 'react'
import { Link } from 'react-router-dom'

export default function LoginPage() {
  return (
    <div className="placeholder-page">
      <div className="brand-logo">
        Lingua<span>Chat</span>
      </div>
      <h1>Welcome</h1>
      <p>Real-time multilingual messaging</p>
      <span className="placeholder-badge">
        🚧 Login UI — Pending implementation by Ahmed Alammari
      </span>
      <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
        Routes: POST /api/v1/auth/login · POST /api/v1/auth/register
      </p>
    </div>
  )
}
