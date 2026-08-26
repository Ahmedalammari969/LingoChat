/**
 * LinguaChat — useWebSocket Hook (Skeleton)
 *
 * React hook wrapping the WebSocket service for use in ChatPage.
 * Implementation: Ahmed Alammari — TASK: Frontend / Integration
 */

import { useEffect, useRef, useCallback } from 'react'
import { createWebSocketService } from '../services/websocket.js'
import { authService } from '../services/auth.js'

/**
 * @param {string} roomId
 * @param {object} handlers
 * @param {function} handlers.onMessage
 * @param {function} handlers.onConnect
 * @param {function} handlers.onDisconnect
 * @param {function} handlers.onError
 * @returns {{ sendMessage, sendTyping, disconnect }}
 */
export function useWebSocket(roomId, handlers) {
  const serviceRef = useRef(null)
  const handlersRef = useRef(handlers)
  handlersRef.current = handlers

  useEffect(() => {
    const token = authService.getToken()
    if (!token || !roomId) return

    const proxyHandlers = {
      onMessage: (msg) => handlersRef.current?.onMessage?.(msg),
      onConnect: () => handlersRef.current?.onConnect?.(),
      onDisconnect: (code) => handlersRef.current?.onDisconnect?.(code),
      onError: (code, msg) => handlersRef.current?.onError?.(code, msg),
    }

    const service = createWebSocketService(roomId, token, proxyHandlers)
    serviceRef.current = service
    service.connect()

    return () => {
      service.disconnect()
    }
  }, [roomId]) // eslint-disable-line react-hooks/exhaustive-deps

  const sendMessage = useCallback((text, lang) => {
    serviceRef.current?.sendMessage(text, lang)
  }, [])

  const sendTyping = useCallback((isTyping) => {
    serviceRef.current?.sendTyping(isTyping)
  }, [])

  const sendLiveSignal = useCallback((type, payload) => {
    serviceRef.current?.sendLiveSignal(type, payload)
  }, [])

  const disconnect = useCallback(() => {
    serviceRef.current?.disconnect()
  }, [])

  const reconnect = useCallback(() => {
    serviceRef.current?.reconnectNow()
  }, [])

  return { sendMessage, sendTyping, sendLiveSignal, disconnect, reconnect }
}
