/**
 * LinguaChat — Rooms Page (Placeholder)
 *
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 *
 * When implementing:
 * - Use api/rooms.js for GET /rooms and POST /rooms
 * - Show list of available rooms with member count
 * - Allow creating a new room (name input)
 * - Show invitation link after room creation
 * - On room click → navigate to /chat/:roomId
 * - Requires JWT in Authorization header
 */

import React from 'react'

export default function RoomsPage() {
  return (
    <div className="placeholder-page">
      <div className="brand-logo">Lingua<span>Chat</span></div>
      <h1>Rooms</h1>
      <p>Create or join a chat room</p>
      <span className="placeholder-badge">
        🚧 Rooms UI — Pending implementation by Ahmed Alammari
      </span>
      <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
        Routes: GET /api/v1/rooms · POST /api/v1/rooms · POST /api/v1/rooms/:id/join
      </p>
    </div>
  )
}
