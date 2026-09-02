import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { useWebSocket } from '../hooks/useWebSocket.js'
import { authService } from '../services/auth.js'
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
        const applicantId = payload.sender_id || payload.user_id
        const applicantName = payload.sender_username || payload.username || 'مستخدم'
        if (applicantId) {
          setGuestRequests((prev) => [
            ...prev.filter((r) => r.user_id !== applicantId),
            { user_id: applicantId, username: applicantName },
          ])
        }
      } else if (msg.type === 'LIVE_ACCEPT_GUEST') {
        console.log('[Live] LIVE_ACCEPT_GUEST received:', JSON.stringify(payload))
        setGuestUsername(payload.guest_username)
        setGuestUserId(payload.guest_id)
        setGuestRequests((prev) => prev.filter((r) => r.user_id !== payload.guest_id))

        const currentUserId = user?.id || authService.getUser()?.id
        const currentUsername = user?.username || authService.getUser()?.username
        console.log('[Live] My identity: id=', currentUserId, 'username=', currentUsername)

        // إذا كنت أنا الضيف الذي تم قبوله
        if (
          (payload.guest_id && String(payload.guest_id) === String(currentUserId)) ||
          (payload.guest_username && payload.guest_username === currentUsername)
        ) {
          console.log('[Live] ✅ I am the accepted guest!')
          setIsGuest(true)
          setHasRequestedJoin(false)
          setIsLiveModalOpen(true)
          try {
            await webrtcRef.current?.startLocalStream(true, true)
            // sender_id is auto-injected by backend = the host's user ID
            const targetHost = payload.sender_id || payload.host_id || hostUserId
            console.log('[Live] Guest creating WebRTC offer to host:', targetHost)
            await webrtcRef.current?.createOffer(targetHost)
          } catch (err) {
            console.error('[Live] ❌ فشل تشغيل كاميرا الضيف:', err)
            alert('تعذر فتح كاميرا الضيف: ' + err.message)
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
        console.log('[Live] RTC_OFFER received from:', payload.sender_id, 'sdp type:', payload.sdp?.type)
        if (payload.sdp) {
          await webrtcRef.current?.handleOffer(payload.sender_id, payload.sdp)
        }
      } else if (msg.type === 'RTC_ANSWER') {
        console.log('[Live] RTC_ANSWER received from:', payload.sender_id, 'sdp type:', payload.sdp?.type)
        if (payload.sdp) {
          await webrtcRef.current?.handleAnswer(payload.sender_id, payload.sdp)
        }
      } else if (msg.type === 'RTC_ICE_CANDIDATE') {
        console.log('[Live] RTC_ICE_CANDIDATE received from:', payload.sender_id)
        if (payload.candidate) {
          await webrtcRef.current?.handleCandidate(payload.sender_id, payload.candidate)
        }
      }
    },
  })

  // تهيئة كائن WebRTC
  const sendLiveSignalRef = useRef(sendLiveSignal)
  sendLiveSignalRef.current = sendLiveSignal

  useEffect(() => {
    const rtc = new WebRTCService({
      onLocalStream: (stream) => {
        console.log('[ChatPage] onLocalStream called, tracks:', stream.getTracks().map(t => t.kind))
        setLocalStream(stream)
      },
      onRemoteStream: (userId, stream) => {
        console.log('[ChatPage] onRemoteStream called, tracks:', stream.getTracks().map(t => t.kind))
        setRemoteStream(stream)
      },
      sendSignal: (type, payload) => {
        console.log('[ChatPage] sendSignal:', type, 'target:', payload?.target_user_id)
        sendLiveSignalRef.current(type, payload)
      },
    })
    webrtcRef.current = rtc

    return () => {
      rtc.stopLocalStream()
    }
  }, []) // Empty deps - create once, use ref for sendLiveSignal

  // ── دوال التحكم في البث المباشر ──
  const handleStartLive = async () => {
    try {
      const currentUserId = user?.id || authService.getUser()?.id || ''
      const currentUsername = user?.username || authService.getUser()?.username || 'المضيف'

      setIsHost(true)
      setHostUsername(currentUsername)
      setHostUserId(currentUserId)
      setIsLiveActive(true)
      setIsLiveModalOpen(true)

      await webrtcRef.current?.startLocalStream(true, true)
      sendLiveSignal('LIVE_START', {
        host_id: currentUserId,
        host_username: currentUsername,
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
    const currentUserId = user?.id || authService.getUser()?.id
    const currentUsername = user?.username || authService.getUser()?.username
    sendLiveSignal('LIVE_REQUEST_JOIN', {
      target_user_id: hostUserId,
      user_id: currentUserId,
      username: currentUsername,
    })
  }

  const handleAcceptGuest = (guestId, guestName) => {
    setGuestRequests((prev) => prev.filter((r) => r.user_id !== guestId))
    setGuestUsername(guestName)
    setGuestUserId(guestId)
    const currentUserId = user?.id || authService.getUser()?.id
    sendLiveSignal('LIVE_ACCEPT_GUEST', {
      guest_id: guestId,
      guest_username: guestName,
      host_id: currentUserId,
      target_user_id: guestId,
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

    const sent = sendMessage(trimmed)
    if (sent !== false) {
      setInputText('')
      sendTyping(false)
    } else {
      reconnect()
    }
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

  // نسخ رابط الغرفة تلقائياً حسب عنوان المتصفح الحالي
  const handleCopyLink = () => {
    const inviteUrl = `${window.location.origin}/rooms/${roomId}`
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
