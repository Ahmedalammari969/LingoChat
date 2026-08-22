import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { createRoom, listRooms, joinRoom } from '../api/rooms.js'

export default function RoomsPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [rooms, setRooms] = useState([])
  const [newRoomName, setNewRoomName] = useState('')
  const [createdRoomInfo, setCreatedRoomInfo] = useState(null)
  const [copySuccess, setCopySuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  // جلب قائمة الغرف من السيرفر
  const fetchRooms = async () => {
    try {
      setErrorMessage('')
      const data = await listRooms()
      setRooms(data?.rooms || [])
    } catch (err) {
      setErrorMessage(err.message || 'فشل تحميل قائمة الغرف')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRooms()
  }, [])

  // إنشاء غرفة جديدة
  const handleCreateRoom = async (e) => {
    e.preventDefault()
    if (!newRoomName.trim()) return

    setIsCreating(true)
    setErrorMessage('')
    try {
      const room = await createRoom(newRoomName.trim())
      setCreatedRoomInfo(room)
      setNewRoomName('')
      fetchRooms()
    } catch (err) {
      setErrorMessage(err.message || 'فشل إنشاء الغرفة')
    } finally {
      setIsCreating(false)
    }
  }

  // الانضمام والدخول إلى الغرفة
  const handleJoinAndEnter = async (roomId) => {
    try {
      await joinRoom(roomId)
      navigate(`/chat/${roomId}`)
    } catch (err) {
      // في حال كان منضماً بالفعل أو أي كود، نوجهه مباشرة للدردشة
      navigate(`/chat/${roomId}`)
    }
  }

  // نسخ رابط/كود الدعوة
  const handleCopyInvite = (link) => {
    navigator.clipboard.writeText(link)
    setCopySuccess(true)
    setTimeout(() => setCopySuccess(false), 2000)
  }

  return (
    <div className="room-list-page">
      {/* شريط معلومات المستخدم العلوي */}
      <div style={{
        width: 'min(760px, 100%)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(22, 26, 34, 0.8)',
        padding: '14px 24px',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        backdropFilter: 'blur(8px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent)' }}>LinguaChat</span>
          <span style={{ color: 'var(--muted-text)', fontSize: '14px' }}>| مرحباً، {user?.username || 'مستخدم'}</span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link
            to="/dashboard"
            style={{
              padding: '8px 14px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.06)',
              color: '#fff',
              fontSize: '13px',
              textDecoration: 'none',
              fontWeight: 600
            }}
          >
            📊 لوحة المؤشرات
          </Link>
          <button
            onClick={logout}
            style={{
              padding: '8px 14px',
              borderRadius: '12px',
              background: 'rgba(255, 92, 114, 0.15)',
              color: 'var(--color-error)',
              border: 'none',
              fontSize: '13px',
              cursor: 'pointer',
              fontWeight: 600,
              fontFamily: 'inherit'
            }}
          >
            خروج
          </button>
        </div>
      </div>

      {/* رسالة الخطأ إن وجدت */}
      {errorMessage && (
        <div style={{
          width: 'min(760px, 100%)',
          background: 'rgba(255, 92, 114, 0.12)',
          border: '1px solid var(--color-error)',
          color: 'var(--color-error)',
          padding: '12px 16px',
          borderRadius: '16px',
          fontSize: '14px'
        }}>
          {errorMessage}
        </div>
      )}

      {/* بطاقة إنشاء غرفة جديدة */}
      <div className="room-creation-card">
        <h1>إنشاء غرفة محادثة جديدة</h1>
        <p>أنشئ غرفة محادثة فورية، وشارك الرابط مع أصدقائك لتبادل الرسائل المترجمة بأي لغة.</p>

        <form className="room-form" onSubmit={handleCreateRoom}>
          <label>
            اسم الغرفة (Room Name)
            <input
              type="text"
              placeholder="مثال: غرفة المطورين العامة"
              value={newRoomName}
              onChange={(e) => setNewRoomName(e.target.value)}
              disabled={isCreating}
              required
            />
          </label>
          <button type="submit" disabled={isCreating}>
            {isCreating ? 'جارٍ الإنشاء...' : 'إنشاء الغرفة'}
          </button>
        </form>

        {/* بطاقة رابط الدعوة عند إنشاء الغرفة بنجاح */}
        {createdRoomInfo && (
          <div className="invite-card">
            <p className="invite-note">🎉 تم إنشاء الغرفة بنجاح! شارك الرابط:</p>
            <label className="invite-link-label">
              رابط الدعوة:
              <input
                className="invite-link-input"
                type="text"
                readOnly
                value={createdRoomInfo.invitation_link || `${window.location.origin}/chat/${createdRoomInfo.id}`}
              />
            </label>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <button
                type="button"
                className="copy-button"
                onClick={() => handleCopyInvite(createdRoomInfo.invitation_link || `${window.location.origin}/chat/${createdRoomInfo.id}`)}
              >
                {copySuccess ? '✓ تم النسخ!' : 'نسخ الرابط'}
              </button>
              <button
                type="button"
                className="copy-button"
                style={{ background: 'rgba(255, 255, 255, 0.1)' }}
                onClick={() => handleJoinAndEnter(createdRoomInfo.id)}
              >
                دخول الغرفة الآن ➔
              </button>
            </div>
          </div>
        )}
      </div>

      {/* بطاقة قائمة الغرف المتاحة */}
      <div className="room-list-section">
        <h2>الغرف المتاحة حالياً</h2>
        <p>انضم إلى أي من الغرف المتاحة للدردشة المباشرة مع الأعضاء.</p>

        {isLoading ? (
          <p style={{ textAlign: 'center', color: 'var(--muted-text)' }}>جارٍ تحميل الغرف...</p>
        ) : rooms.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--muted-text)', padding: '20px 0' }}>
            لا توجد غرف منشأة حالياً. كن أول من ينشئ غرفة أعلاه!
          </p>
        ) : (
          <ul className="room-list">
            {rooms.map((room) => (
              <li key={room.id} className="room-list__item">
                <div>
                  <strong>{room.name}</strong>
                  <p>الأعضاء: {room.member_count ?? 1} عضو</p>
                </div>
                <button
                  type="button"
                  onClick={() => handleJoinAndEnter(room.id)}
                >
                  انضمام ودخول ➔
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
