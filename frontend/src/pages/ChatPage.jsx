/**
 * LinguaChat — Chat Page (Placeholder)
 * Route: /rooms/:roomId   (Architecture Freeze 2026-08-13)
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 *
 * When implementing:
 * - Read roomId from useParams()
 * - Use services/websocket.js to connect to ws://host/ws/{roomId}?token=<jwt>
 * - Send TEXT_MESSAGE, TYPING, HEARTBEAT via WebSocket
 * - Receive JOIN, LEAVE, TEXT_MESSAGE, TYPING, ERROR from server
 * - Display messages — show translated_text, keep original_text available
 * - Show typing indicators
 * - Load message history via api/rooms.js: GET /rooms/:id/messages
 * - Handle WebSocket reconnection (see websocket-contract.md § Reconnect Strategy)
 * - Show connection status indicator
 *
 * See: docs/websocket-contract.md for full message format
 */

import React from 'react'
import { useParams } from 'react-router-dom'

export default function ChatPage() {
  const { roomId } = useParams()

  return (
    <div className="placeholder-page">
      <div className="brand-logo">Lingua<span>Chat</span></div>
      <h1>Chat Room</h1>
      <p>Room: <code style={{ color: 'var(--color-primary)' }}>{roomId}</code></p>
      <span className="placeholder-badge">
        🚧 Chat UI — Pending implementation by Ahmed Alammari
      </span>
      <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
        WebSocket: ws://host/ws/{roomId}?token=&lt;jwt&gt;
      </p>
    </div>
  )
}
