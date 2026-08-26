import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { useWebSocket } from '../hooks/useWebSocket.js'
import { getRoomMessages, joinRoom, getRoomDetails } from '../api/rooms.js'
import { WebRTCService } from '../services/webrtc.js'
import LiveStreamView from '../components/LiveStreamView.jsx'

export default function ChatPage() {
  const { roomId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [roomInfo, setRoomInfo] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [connectionStatus, setConnectionStatus] = useState('connecting')
  const [typingUsers, setTypingUsers] = useState([])
  const [showOriginalMap, setShowOriginalMap] = useState({})
  const [copySuccess, setCopySuccess] = useState(false)

  // ── Live Streaming & WebRTC State ──
  const [isLiveActive, setIsLiveActive] = useState(false)
  const [isLiveModalOpen, setIsLiveModalOpen] = useState(false)
  const [isHost, setIsHost] = useState(false)
  const [isGuest, setIsGuest] = useState(false)
  const [hostUsername, setHostUsername] = useState('')
  const [hostUserId, setHostUserId] = useState('')
  const [guestUsername, setGuestUsername] = useState('')
  const [guestUserId, setGuestUserId] = useState('')
  const [guestRequests, setGuestRequests] = useState([])
  const [hasRequestedJoin, setHasRequestedJoin] = useState(false)
  const [localStream, setLocalStream] = useState(null)
  const [remoteStream, setRemoteStream] = useState(null)

  const messagesEndRef = useRef(null)
  const typingTimeoutRef = useRef(null)
  const webrtcRef = useRef(null)

  // التمرير التلقائي لأسفل عند وصول رسالة جديدة
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, typingUsers])

  // الانضمام التلقائي للغرفة وجلب معلوماتها وسجل الرسائل عند فتح الرابط المباشر
  useEffect(() => {
    const token = localStorage.getItem('linguachat_token')
    if (!token) {
      navigate(`/login?redirect=${encodeURIComponent(window.location.pathname)}`)
      return
    }

    async function loadRoomAndHistory() {
      try {
        await joinRoom(roomId).catch(() => {})
        getRoomDetails(roomId).then(setRoomInfo).catch(() => {})

        const data = await getRoomMessages(roomId)
        if (data?.messages) {
          const formatted = data.messages.map((m) => ({
            id: m.id,
            sender: m.sender_username,
            text: m.translated_text || m.original_text,
            originalText: m.original_text,
            originalLang: m.original_language,
            targetLang: m.target_language,
            source: m.translation_source,
            timestamp: m.sent_at,
            isSystem: false,
          }))
          setMessages(formatted)
        }
      } catch (err) {
        console.error('فشل جلب تفاصيل الغرفة أو الرسائل:', err)
      }
    }
    if (roomId) loadRoomAndHistory()
  }, [roomId, navigate])

  // ── إعداد مستمعات الـ WebSocket مع معالجة أحداث البث المباشر ──
  const { sendMessage, sendTyping, sendLiveSignal, reconnect } = useWebSocket(roomId, {
    onConnect: () => setConnectionStatus('open'),
    onDisconnect: (code) => {
      if (code === 1000) setConnectionStatus('error')
      else setConnectionStatus('connecting')
    },
    onError: () => setConnectionStatus('error'),
    onMessage: async (msg) => {
      if (!msg || !msg.type) return

      const payload = msg.payload || {}

      // 1. رسالة شات جديدة
      if (msg.type === 'TEXT_MESSAGE') {
        setMessages((prev) => [
          ...prev,
          {
            id: payload.message_id || `${Date.now()}-${Math.random()}`,
            sender: payload.sender_username || 'مجهول',
            text: payload.translated_text || payload.original_text || payload.text,
            originalText: payload.original_text || payload.text,
            originalLang: payload.original_language,
            targetLang: payload.target_language,
            source: payload.translation_source,
            timestamp: msg.timestamp || new Date().toISOString(),
            isSystem: false,
          },
        ])
      }
      // 2. حدث انضمام ومغادرة الأعضاء
      else if (msg.type === 'JOIN') {
        setMessages((prev) => [
          ...prev,
          {
            id: `join-${Date.now()}`,
            text: `👋 انضم ${payload.username || 'مستخدم جديد'} إلى المحادثة`,
            isSystem: true,
          },
        ])
      } else if (msg.type === 'LEAVE') {
        setMessages((prev) => [
          ...prev,
          {
            id: `leave-${Date.now()}`,
            text: `🚪 غادر ${payload.username || 'مستخدم'} المحادثة`,
            isSystem: true,
          },
        ])
      }
      // 3. مؤشر الكتابة
      else if (msg.type === 'TYPING') {
        const { username, is_typing } = payload
        if (username && username !== user?.username) {
          setTypingUsers((prev) => {
            if (is_typing) {
              return prev.includes(username) ? prev : [...prev, username]
            }
            return prev.filter((u) => u !== username)
          })
        }
      }
      // ── 4. أحداث البث المباشر (TikTok Live Events) ──
      else if (msg.type === 'LIVE_START') {
        setIsLiveActive(true)
        setHostUsername(payload.host_username || 'المضيف')
        setHostUserId(payload.host_id || payload.sender_id)
        setMessages((prev) => [
          ...prev,
          {
            id: `live-start-${Date.now()}`,
            text: `🔴 بدأ ${payload.host_username || 'المضيف'} بثاً مباشراً في الغرفة!`,
            isSystem: true,
          },
        ])
      } else if (msg.type === 'LIVE_STOP') {
        setIsLiveActive(false)
        setIsLiveModalOpen(false)
        setIsGuest(false)
        setIsHost(false)
        setGuestUsername('')
        setGuestUserId('')
        setGuestRequests([])
        setHasRequestedJoin(false)
        webrtcRef.current?.stopLocalStream()
        setLocalStream(null)
        setRemoteStream(null)
        setMessages((prev) => [
          ...prev,
          {
            id: `live-stop-${Date.now()}`,
            text: `🛑 انتهى البث المباشر.`,
            isSystem: true,
          },
        ])
      } else if (msg.type === 'LIVE_REQUEST_JOIN') {
        // إشعار المضيف بطلب الصعود
        if (isHost || user?.username === hostUsername) {
          setGuestRequests((prev) => [
            ...prev.filter((r) => r.user_id !== payload.sender_id),
            { user_id: payload.sender_id, username: payload.sender_username },
          ])
        }
      } else if (msg.type === 'LIVE_ACCEPT_GUEST') {
        setGuestUsername(payload.guest_username)
        setGuestUserId(payload.guest_id)
        setGuestRequests((prev) => prev.filter((r) => r.user_id !== payload.guest_id))

        // إذا كنت أنا الضيف الذي تم قبوله
        if (payload.guest_id === user?.id || payload.guest_username === user?.username) {
          setIsGuest(true)
          setHasRequestedJoin(false)
          setIsLiveModalOpen(true)
          try {
            await webrtcRef.current?.startLocalStream(true, true)
            // إنشاء اتصال WebRTC مع المضيف
            await webrtcRef.current?.createOffer(payload.host_id)
          } catch (err) {
            console.error('فشل تشغيل كاميرا الضيف:', err)
          }
        }
      } else if (msg.type === 'LIVE_REJECT_GUEST') {
        if (payload.target_user_id === user?.id) {
          setHasRequestedJoin(false)
          alert('عذراً، رفض المضيف طلب الصعود للمشاركة في البث.')
        }
      } else if (msg.type === 'LIVE_LEAVE_GUEST') {
        setGuestUsername('')
        setGuestUserId('')
        if (isGuest) {
          setIsGuest(false)
          webrtcRef.current?.stopLocalStream()
          setLocalStream(null)
        }
      }
      // ── 5. إشارات WebRTC Signaling ──
      else if (msg.type === 'RTC_OFFER') {
        if (payload.sdp) {
          await webrtcRef.current?.handleOffer(payload.sender_id, payload.sdp)
        }
      } else if (msg.type === 'RTC_ANSWER') {
        if (payload.sdp) {
          await webrtcRef.current?.handleAnswer(payload.sender_id, payload.sdp)
        }
      } else if (msg.type === 'RTC_ICE_CANDIDATE') {
        if (payload.candidate) {
          await webrtcRef.current?.handleCandidate(payload.sender_id, payload.candidate)
        }
      }
    },
  })

  // تهيئة كائن WebRTC
  useEffect(() => {
    webrtcRef.current = new WebRTCService({
      onLocalStream: (stream) => setLocalStream(stream),
      onRemoteStream: (userId, stream) => setRemoteStream(stream),
      sendSignal: (type, payload) => sendLiveSignal(type, payload),
    })

    return () => {
      webrtcRef.current?.stopLocalStream()
    }
  }, [sendLiveSignal])

  // ── دوال التحكم في البث المباشر ──
  const handleStartLive = async () => {
    try {
      setIsHost(true)
      setHostUsername(user?.username || 'المضيف')
      setHostUserId(user?.id || '')
      setIsLiveActive(true)
      setIsLiveModalOpen(true)

      await webrtcRef.current?.startLocalStream(true, true)
      sendLiveSignal('LIVE_START', {
        host_id: user?.id,
        host_username: user?.username,
      })
    } catch (err) {
      alert('تعذر فتح الكاميرا أو الميكروفون: ' + err.message)
      setIsHost(false)
      setIsLiveModalOpen(false)
    }
  }

  const handleEndLive = () => {
    setIsHost(false)
    setIsLiveActive(false)
    setIsLiveModalOpen(false)
    webrtcRef.current?.stopLocalStream()
    setLocalStream(null)
    setRemoteStream(null)
    sendLiveSignal('LIVE_STOP', {})
  }

  const handleRequestJoin = () => {
    setHasRequestedJoin(true)
    sendLiveSignal('LIVE_REQUEST_JOIN', {
      target_user_id: hostUserId,
    })
  }

  const handleAcceptGuest = (guestId, guestName) => {
    setGuestRequests((prev) => prev.filter((r) => r.user_id !== guestId))
    setGuestUsername(guestName)
    setGuestUserId(guestId)
    sendLiveSignal('LIVE_ACCEPT_GUEST', {
      guest_id: guestId,
      guest_username: guestName,
      host_id: user?.id,
    })
  }

  const handleRejectGuest = (guestId) => {
    setGuestRequests((prev) => prev.filter((r) => r.user_id !== guestId))
    sendLiveSignal('LIVE_REJECT_GUEST', {
      target_user_id: guestId,
    })
  }

  const handleLeaveGuest = () => {
    setIsGuest(false)
    setGuestUsername('')
    setGuestUserId('')
    webrtcRef.current?.stopLocalStream()
    setLocalStream(null)
    sendLiveSignal('LIVE_LEAVE_GUEST', {})
  }

  // إرسال الرسالة
  const handleSend = (e) => {
    e?.preventDefault()
    const trimmed = inputText.trim()
    if (!trimmed) return

    sendMessage(trimmed)
    setInputText('')
    sendTyping(false)
  }

  // التفاعل مع حقل الكتابة
  const handleInputChange = (e) => {
    setInputText(e.target.value)
    sendTyping(true)

    clearTimeout(typingTimeoutRef.current)
    typingTimeoutRef.current = setTimeout(() => {
      sendTyping(false)
    }, 2000)
  }

  // تبديل عرض النص الأصلي/المترجم
  const toggleOriginal = (msgId) => {
    setShowOriginalMap((prev) => ({ ...prev, [msgId]: !prev[msgId] }))
  }

  // نسخ رابط الغرفة
  const handleCopyLink = () => {
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    const host = isLocal ? '10.171.146.61' : window.location.hostname
    const port = window.location.port ? `:${window.location.port}` : ''
    const inviteUrl = `${window.location.protocol}//${host}${port}/rooms/${roomId}`
    navigator.clipboard.writeText(inviteUrl)
    setCopySuccess(true)
    setTimeout(() => setCopySuccess(false), 2000)
  }

  return (
    <div className="chat-page">
      {/* ── رأس المحادثة ── */}
      <header className="chat-page__header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button
            onClick={() => navigate('/rooms')}
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              border: 'none',
              color: '#fff',
              padding: '6px 12px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '13px',
              fontFamily: 'inherit',
            }}
          >
            ← الغرف
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: '#fff' }}>
              {roomInfo?.name || 'غرفة المحادثة'}
            </h1>
            {roomInfo?.is_private ? (
              <span style={{ fontSize: '11px', background: 'rgba(99, 102, 241, 0.2)', color: 'var(--accent)', padding: '2px 8px', borderRadius: '8px', fontWeight: 700 }}>
                🔒 خاصة
              </span>
            ) : roomInfo ? (
              <span style={{ fontSize: '11px', background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '2px 8px', borderRadius: '8px', fontWeight: 700 }}>
                🌐 عامة
              </span>
            ) : null}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* زر البث المباشر (TikTok Live Button) */}
          {isLiveActive ? (
            <button
              type="button"
              onClick={() => setIsLiveModalOpen(true)}
              style={{
                background: 'linear-gradient(135deg, #ef4444, #f43f5e)',
                border: 'none',
                color: '#fff',
                padding: '6px 14px',
                borderRadius: '12px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 700,
                fontFamily: 'inherit',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 0 12px rgba(239, 68, 68, 0.5)',
                animation: 'pulse 1.5s infinite',
              }}
            >
              🔴 فتح شاشة البث المباشر (حي الآن)
            </button>
          ) : (
            <button
              type="button"
              onClick={handleStartLive}
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid #ef4444',
                color: '#ef4444',
                padding: '6px 14px',
                borderRadius: '12px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 700,
                fontFamily: 'inherit',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              📹 بدء بث مباشر (Go Live)
            </button>
          )}

          {/* زر نسخ رابط الغرفة */}
          <button
            type="button"
            onClick={handleCopyLink}
            style={{
              background: copySuccess ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.15)',
              border: copySuccess ? '1px solid #10b981' : '1px solid var(--accent)',
              color: copySuccess ? '#10b981' : 'var(--accent)',
              padding: '6px 14px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 600,
              fontFamily: 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s ease',
            }}
          >
            {copySuccess ? '✓ تم نسخ الرابط!' : '🔗 نسخ رابط الغرفة'}
          </button>

          <div
            className={`chat-page__status chat-page__status--${connectionStatus}`}
            onClick={connectionStatus !== 'open' ? reconnect : undefined}
            style={{ cursor: connectionStatus !== 'open' ? 'pointer' : 'default' }}
            title={connectionStatus !== 'open' ? 'اضغط لإعادة الاتصال الفوري' : 'الاتصال نشط ومستقر'}
          >
            {connectionStatus === 'open' && '🟢 متصل فوري'}
            {connectionStatus === 'connecting' && '🟡 جارٍ الاتصال... (اضغط لإعادة المحاولة)'}
            {connectionStatus === 'error' && '🔴 انقطع الاتصال (اضغط لإعادة الاتصال)'}
          </div>
        </div>
      </header>

      {/* ── شاشة البث المباشر المنبثقة (TikTok Live Overlay) ── */}
      {isLiveModalOpen && (
        <LiveStreamView
          isHost={isHost}
          isGuest={isGuest}
          hostUsername={hostUsername}
          guestUsername={guestUsername}
          localStream={localStream}
          remoteStream={remoteStream}
          guestRequests={guestRequests}
          onStartLive={handleStartLive}
          onEndLive={handleEndLive}
          onRequestJoin={handleRequestJoin}
          onAcceptGuest={handleAcceptGuest}
          onRejectGuest={handleRejectGuest}
          onLeaveGuest={handleLeaveGuest}
          onClose={() => setIsLiveModalOpen(false)}
          hasRequestedJoin={hasRequestedJoin}
        />
      )}

      {/* ── منطقة الرسائل ── */}
      <div className="chat-page__messages">
        {messages.map((msg) => {
          if (msg.isSystem) {
            return (
              <div
                key={msg.id}
                style={{
                  textAlign: 'center',
                  fontSize: '12px',
                  color: 'var(--muted-text)',
                  margin: '10px 0',
                }}
              >
                {msg.text}
              </div>
            )
          }

          const isOwn = msg.sender === user?.username
          const isOriginalShown = showOriginalMap[msg.id]
          const hasOriginalDiff = msg.originalText && msg.originalText !== msg.text

          return (
            <div
              key={msg.id}
              className={`message-bubble ${isOwn ? 'message-bubble--own' : ''}`}
            >
              {!isOwn && <span className="message-bubble__sender">{msg.sender}</span>}
              <div className="message-bubble__body">
                <p className="message-bubble__text">
                  {isOriginalShown ? msg.originalText : msg.text}
                </p>

                {/* زر إظهار النص الأصلي عند وجود ترجمة */}
                {hasOriginalDiff && (
                  <button
                    type="button"
                    onClick={() => toggleOriginal(msg.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: isOwn ? 'rgba(255,255,255,0.75)' : 'var(--accent)',
                      fontSize: '11px',
                      cursor: 'pointer',
                      padding: '2px 0 0',
                      textDecoration: 'underline',
                      fontFamily: 'inherit',
                      display: 'block',
                    }}
                  >
                    {isOriginalShown ? 'عرض النص المترجم ↶' : 'عرض النص الأصلي 🌐'}
                  </button>
                )}

                <span className="message-bubble__time">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          )
        })}

        {/* مؤشر "فلان يكتب الآن..." */}
        {typingUsers.length > 0 && (
          <div style={{ fontSize: '12px', color: 'var(--accent)', padding: '6px 12px', fontStyle: 'italic' }}>
            ✍️ {typingUsers.join(', ')} يكتب الآن...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* شريط كتابة وإرسال الرسالة */}
      <form className="message-input" onSubmit={handleSend}>
        <input
          className="message-input__field"
          type="text"
          placeholder="اكتب رسالتك هنا... (اضغط Enter للإرسال)"
          value={inputText}
          onChange={handleInputChange}
          autoFocus
        />
        <button
          className="message-input__send-btn"
          type="submit"
          disabled={!inputText.trim()}
          title="إرسال"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  )
}
