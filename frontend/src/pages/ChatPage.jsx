import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { useWebSocket } from '../hooks/useWebSocket.js'
import { getRoomMessages, joinRoom } from '../api/rooms.js'

export default function ChatPage() {
  const { roomId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [connectionStatus, setConnectionStatus] = useState('connecting')
  const [typingUsers, setTypingUsers] = useState([])
  const [showOriginalMap, setShowOriginalMap] = useState({})

  const messagesEndRef = useRef(null)
  const typingTimeoutRef = useRef(null)

  // التمرير التلقائي لأسفل عند وصول رسالة جديدة
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, typingUsers])

  // الانضمام التلقائي للغرفة وجلب سجل الرسائل عند فتح الرابط المباشر
  useEffect(() => {
    const token = localStorage.getItem('linguachat_token')
    if (!token) {
      navigate(`/login?redirect=${encodeURIComponent(window.location.pathname)}`)
      return
    }

    async function loadHistory() {
      try {
        await joinRoom(roomId).catch(() => {})
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
        console.error('فشل جلب الرسائل السابقة:', err)
      }
    }
    if (roomId) loadHistory()
  }, [roomId])

  // إعداد مستمعات الـ WebSocket
  const { sendMessage, sendTyping } = useWebSocket(roomId, {
    onConnect: () => setConnectionStatus('open'),
    onDisconnect: () => setConnectionStatus('connecting'),
    onError: () => setConnectionStatus('error'),
    onMessage: (msg) => {
      if (!msg || !msg.type) return

      // رسالة دردشة جديدة
      if (msg.type === 'TEXT_MESSAGE') {
        const payload = msg.payload || {}
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
      // حدث انضمام عضو
      else if (msg.type === 'JOIN') {
        setMessages((prev) => [
          ...prev,
          {
            id: `join-${Date.now()}`,
            text: `👋 انضم ${msg.payload?.username || 'مستخدم جديد'} إلى المحادثة`,
            isSystem: true,
          },
        ])
      }
      // حدث مغادرة عضو
      else if (msg.type === 'LEAVE') {
        setMessages((prev) => [
          ...prev,
          {
            id: `leave-${Date.now()}`,
            text: `🚪 غادر ${msg.payload?.username || 'مستخدم'} المحادثة`,
            isSystem: true,
          },
        ])
      }
      // مؤشر الكتابة الفوري
      else if (msg.type === 'TYPING') {
        const { username, is_typing } = msg.payload || {}
        if (username && username !== user?.username) {
          setTypingUsers((prev) => {
            if (is_typing) {
              return prev.includes(username) ? prev : [...prev, username]
            }
            return prev.filter((u) => u !== username)
          })
        }
      }
    },
  })

  // إرسال الرسالة
  const handleSend = (e) => {
    e?.preventDefault()
    const trimmed = inputText.trim()
    if (!trimmed) return

    sendMessage(trimmed)
    setInputText('')
    sendTyping(false)
  }

  // التفاعل مع حقل الكتابة (إرسال Typing)
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

  return (
    <div className="chat-page">
      {/* رأس المحادثة */}
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
          <h1>غرفة المحادثة</h1>
        </div>

        <div className={`chat-page__status chat-page__status--${connectionStatus}`}>
          {connectionStatus === 'open' && '🟢 متصل فوري'}
          {connectionStatus === 'connecting' && '🟡 جارٍ الاتصال...'}
          {connectionStatus === 'error' && '🔴 انقطع الاتصال'}
        </div>
      </header>

      {/* منطقة الرسائل */}
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
          disabled={connectionStatus !== 'open'}
        />
        <button
          className="message-input__send-btn"
          type="submit"
          disabled={connectionStatus !== 'open' || !inputText.trim()}
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
