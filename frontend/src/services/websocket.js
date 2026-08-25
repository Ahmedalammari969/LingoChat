/**
 * LinguaChat — WebSocket Service
 *
 * Manages the WebSocket connection lifecycle.
 * See: docs/websocket-contract.md for message formats and protocol.
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 *
 * Usage:
 *   const ws = createWebSocketService(roomId, token, handlers)
 *   ws.connect()
 *   ws.sendMessage(text)
 *   ws.sendTyping(isTyping)
 *   ws.disconnect()
 */

const getWsBaseUrl = () => {
  const envUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws'
  if (typeof window !== 'undefined' && window.location?.hostname && window.location.hostname !== 'localhost') {
    return envUrl.replace('localhost', window.location.hostname).replace('127.0.0.1', window.location.hostname)
  }
  return envUrl
}

const WS_BASE_URL = getWsBaseUrl()

// Reconnection constants — see docs/websocket-contract.md § Reconnect Strategy
const RECONNECT_BASE_MS = 1000
const RECONNECT_MAX_MS = 30000
const RECONNECT_MAX_ATTEMPTS = 10
const HEARTBEAT_INTERVAL_MS = 30000

/**
 * Create a WebSocket service for a room.
 *
 * @param {string} roomId
 * @param {string} token - JWT access token
 * @param {object} handlers
 * @param {function} handlers.onMessage - Called with parsed message object
 * @param {function} handlers.onConnect - Called on successful connection
 * @param {function} handlers.onDisconnect - Called on disconnection
 * @param {function} handlers.onError - Called with error code and message
 * @returns {{ connect, disconnect, sendMessage, sendTyping }}
 */
export function createWebSocketService(roomId, token, handlers = {}) {
  let socket = null
  let reconnectAttempts = 0
  let heartbeatTimer = null

  function getTimestamp() {
    return new Date().toISOString()
  }

  function buildEnvelope(type, payload = {}) {
    return JSON.stringify({
      type,
      payload,
      timestamp: getTimestamp(),
      room_id: roomId,
    })
  }

  function startHeartbeat() {
    heartbeatTimer = setInterval(() => {
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(buildEnvelope('HEARTBEAT'))
      }
    }, HEARTBEAT_INTERVAL_MS)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  function connect() {
    const url = `${WS_BASE_URL}/${roomId}?token=${encodeURIComponent(token)}`
    socket = new WebSocket(url)

    socket.onopen = () => {
      reconnectAttempts = 0
      startHeartbeat()
      handlers.onConnect?.()
    }

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        handlers.onMessage?.(message)
      } catch {
        console.error('[LinguaChat WS] Invalid JSON received')
      }
    }

    socket.onclose = (event) => {
      stopHeartbeat()
      handlers.onDisconnect?.(event.code)

      // Attempt reconnect if not deliberate close
      if (event.code !== 1000 && event.code !== 4001 && event.code !== 4003) {
        scheduleReconnect()
      }
    }

    socket.onerror = () => {
      handlers.onError?.('CONNECTION_ERROR', 'WebSocket connection error')
    }
  }

  function scheduleReconnect() {
    if (reconnectAttempts >= RECONNECT_MAX_ATTEMPTS) {
      handlers.onError?.('MAX_RECONNECT_REACHED', 'Connection lost. Please refresh.')
      return
    }
    const delay = Math.min(
      RECONNECT_BASE_MS * Math.pow(2, reconnectAttempts),
      RECONNECT_MAX_MS
    )
    reconnectAttempts++
    setTimeout(connect, delay)
  }

  function disconnect() {
    stopHeartbeat()
    socket?.close(1000)
    socket = null
  }

  function sendMessage(text, originalLanguage = null) {
    if (socket?.readyState !== WebSocket.OPEN) return
    socket.send(buildEnvelope('TEXT_MESSAGE', {
      text,
      ...(originalLanguage ? { original_language: originalLanguage } : {}),
    }))
  }

  function sendTyping(isTyping) {
    if (socket?.readyState !== WebSocket.OPEN) return
    socket.send(buildEnvelope('TYPING', { is_typing: isTyping }))
  }

  function sendLiveSignal(type, payload = {}) {
    if (socket?.readyState !== WebSocket.OPEN) return
    socket.send(buildEnvelope(type, payload))
  }

  return { connect, disconnect, sendMessage, sendTyping, sendLiveSignal }
}
