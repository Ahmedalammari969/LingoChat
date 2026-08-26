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

function buildWsUrls(roomId, token) {
  if (import.meta.env.VITE_WS_BASE_URL) {
    return [`${import.meta.env.VITE_WS_BASE_URL}/${roomId}?token=${encodeURIComponent(token)}`]
  }
  const urls = []
  if (typeof window !== 'undefined' && window.location?.host) {
    const host = window.location.hostname
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    // 1. Primary: Same port as webpage via Vite proxy (port 3000) - NEVER blocked by firewall if webpage loaded!
    urls.push(`${proto}//${window.location.host}/ws/${roomId}?token=${encodeURIComponent(token)}`)
    // 2. Secondary: Direct FastAPI port 8000
    urls.push(`${proto}//${host}:8000/ws/${roomId}?token=${encodeURIComponent(token)}`)
  } else {
    urls.push(`ws://localhost:8000/ws/${roomId}?token=${encodeURIComponent(token)}`)
  }
  return urls
}

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
 * @returns {{ connect, disconnect, sendMessage, sendTyping, sendLiveSignal }}
 */
export function createWebSocketService(roomId, token, handlers = {}) {
  let socket = null
  let reconnectAttempts = 0
  let heartbeatTimer = null
  let connectionTimeoutTimer = null
  let urlIndex = 0
  let isManuallyClosed = false

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

  function clearConnectionTimeout() {
    if (connectionTimeoutTimer) {
      clearTimeout(connectionTimeoutTimer)
      connectionTimeoutTimer = null
    }
  }

  function connect() {
    if (isManuallyClosed) return
    clearConnectionTimeout()
    stopHeartbeat()

    if (socket) {
      try {
        socket.onopen = null
        socket.onmessage = null
        socket.onclose = null
        socket.onerror = null
        socket.close()
      } catch (e) {}
      socket = null
    }

    const urls = buildWsUrls(roomId, token)
    const url = urls[urlIndex % urls.length]
    console.log(`[LinguaChat WS] Connecting (${(urlIndex % urls.length) + 1}/${urls.length}):`, url)

    try {
      socket = new WebSocket(url)
    } catch (e) {
      console.warn('[LinguaChat WS] Creation error for', url, e)
      urlIndex++
      scheduleReconnect(500)
      return
    }

    // Failover rapidly if connection takes > 2.5s to open
    connectionTimeoutTimer = setTimeout(() => {
      if (socket && socket.readyState !== WebSocket.OPEN) {
        console.warn('[LinguaChat WS] 2.5s Timeout on', url, '-> trying alternate route...')
        urlIndex++
        try { socket.close() } catch (e) {}
        connect()
      }
    }, 2500)

    socket.onopen = () => {
      clearConnectionTimeout()
      reconnectAttempts = 0
      console.log('[LinguaChat WS] Successfully connected to:', url)
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
      clearConnectionTimeout()
      stopHeartbeat()
      console.log(`[LinguaChat WS] Closed (code: ${event.code})`)
      handlers.onDisconnect?.(event.code)

      // Attempt reconnect if not deliberate close
      if (!isManuallyClosed && event.code !== 1000 && event.code !== 4001 && event.code !== 4003) {
        urlIndex++
        scheduleReconnect()
      }
    }

    socket.onerror = () => {
      console.warn('[LinguaChat WS] Error on:', url)
      handlers.onError?.('CONNECTION_ERROR', 'WebSocket connection error')
    }
  }

  function scheduleReconnect(customDelay = null) {
    if (isManuallyClosed) return
    if (reconnectAttempts >= RECONNECT_MAX_ATTEMPTS) {
      handlers.onError?.('MAX_RECONNECT_REACHED', 'Connection lost. Please refresh.')
      return
    }
    const delay = customDelay !== null ? customDelay : Math.min(
      RECONNECT_BASE_MS * Math.pow(1.5, reconnectAttempts),
      RECONNECT_MAX_MS
    )
    reconnectAttempts++
    setTimeout(connect, delay)
  }

  function disconnect() {
    isManuallyClosed = true
    clearConnectionTimeout()
    stopHeartbeat()
    if (socket) {
      try { socket.close(1000) } catch (e) {}
      socket = null
    }
  }

  function reconnectNow() {
    isManuallyClosed = false
    reconnectAttempts = 0
    urlIndex = 0
    connect()
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

  return { connect, disconnect, reconnectNow, sendMessage, sendTyping, sendLiveSignal }
}
