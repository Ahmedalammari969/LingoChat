import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { getDashboardStats } from '../api/dashboard.js'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [stats, setStats] = useState({
    total_users: 0,
    total_rooms: 0,
    total_messages: 0,
    total_translations: 0,
    active_connections: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)

  const pollingTimerRef = useRef(null)

  const fetchStats = async (isManual = false) => {
    if (isManual) setIsRefreshing(true)
    try {
      setErrorMessage('')
      const data = await getDashboardStats()
      if (data) {
        setStats({
          total_users: data.total_users ?? 0,
          total_rooms: data.total_rooms ?? 0,
          total_messages: data.total_messages ?? 0,
          total_translations: data.total_translations ?? 0,
          active_connections: data.active_connections ?? 0,
        })
        setLastUpdated(new Date().toLocaleTimeString())
      }
    } catch (err) {
      setErrorMessage(err.message || 'فشل جلب إحصائيات النظام')
    } finally {
      setIsLoading(false)
      if (isManual) setIsRefreshing(false)
    }
  }

  useEffect(() => {
    // 1. جلب الإحصائيات عند فتح الصفحة
    fetchStats()

    // 2. تحديث دوري تلقائي كل 10 ثوانٍ (Auto-polling)
    pollingTimerRef.current = setInterval(() => {
      fetchStats()
    }, 10000)

    // 3. إيقاف المؤقت عند مغادرة الصفحة لمنع تسريب الذاكرة (Memory Leaks)
    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current)
      }
    }
  }, [])

  const statCards = [
    {
      title: 'إجمالي المستخدمين',
      value: stats.total_users,
      icon: '👥',
      color: '#5b8cff',
      subtext: 'مستخدم مسجل في المنصة',
    },
    {
      title: 'الغرف النشطة',
      value: stats.total_rooms,
      icon: '💬',
      color: '#4ade80',
      subtext: 'غرفة محادثة تم إنشاؤها',
    },
    {
      title: 'إجمالي الرسائل',
      value: stats.total_messages,
      icon: '📨',
      color: '#facc15',
      subtext: 'رسالة تم إرسالها وتوزيعها',
    },
    {
      title: 'الترجمات المنفذة',
      value: stats.total_translations,
      icon: '🌐',
      color: '#a78bfa',
      subtext: 'ترجمة فورية بالذكاء الاصطناعي',
    },
    {
      title: 'الاتصالات الحية الآن',
      value: stats.active_connections,
      icon: '⚡',
      color: '#38bdf8',
      subtext: 'مستخدم متصل بالـ WebSocket',
      isLive: true,
    },
  ]

  return (
    <div className="room-list-page" style={{ padding: '24px 16px' }}>
      {/* شريط التنقل العلوي */}
      <div style={{
        width: 'min(900px, 100%)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(22, 26, 34, 0.85)',
        padding: '16px 24px',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        backdropFilter: 'blur(8px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => navigate('/rooms')}
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              border: 'none',
              color: '#fff',
              padding: '8px 14px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '13px',
              fontFamily: 'inherit',
              fontWeight: 600
            }}
          >
            ← الغرف
          </button>
          <h1 style={{ fontSize: '18px', margin: 0, color: 'var(--text)' }}>
            📊 لوحة مؤشرات النظام (System Dashboard)
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => fetchStats(true)}
            disabled={isRefreshing}
            style={{
              background: 'rgba(91, 140, 255, 0.15)',
              border: '1px solid rgba(91, 140, 255, 0.3)',
              color: 'var(--accent)',
              padding: '8px 14px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '13px',
              fontFamily: 'inherit',
              fontWeight: 600
            }}
          >
            {isRefreshing ? 'جارٍ التحديث...' : '🔄 تحديث'}
          </button>
          <button
            onClick={logout}
            style={{
              background: 'rgba(255, 92, 114, 0.15)',
              border: 'none',
              color: 'var(--color-error)',
              padding: '8px 14px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '13px',
              fontFamily: 'inherit',
              fontWeight: 600
            }}
          >
            خروج
          </button>
        </div>
      </div>

      {/* رسالة الخطأ مع زر إعادة المحاولة */}
      {errorMessage && (
        <div style={{
          width: 'min(900px, 100%)',
          background: 'rgba(255, 92, 114, 0.12)',
          border: '1px solid var(--color-error)',
          color: 'var(--color-error)',
          padding: '14px 20px',
          borderRadius: '16px',
          fontSize: '14px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>⚠️ {errorMessage}</span>
          <button
            onClick={() => fetchStats(true)}
            style={{
              background: 'var(--color-error)',
              color: '#fff',
              border: 'none',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 600
            }}
          >
            إعادة المحاولة ↻
          </button>
        </div>
      )}

      {/* المحتوى الرئيسي للوحة التحكم */}
      <div style={{
        width: 'min(900px, 100%)',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}>
        {/* شبكة البطاقات الإحصائية */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '18px'
        }}>
          {statCards.map((card, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(22, 26, 34, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '20px',
                padding: '24px',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, border-color 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span style={{ color: 'var(--muted-text)', fontSize: '14px', fontWeight: 600 }}>
                  {card.title}
                </span>
                <span style={{ fontSize: '24px' }}>{card.icon}</span>
              </div>

              <div style={{ margin: '18px 0 8px', display: 'flex', alignItems: 'baseline', gap: '10px' }}>
                <span style={{ fontSize: '36px', fontWeight: 700, color: card.color }}>
                  {isLoading ? '...' : card.value.toLocaleString()}
                </span>
                {card.isLive && (
                  <span style={{
                    fontSize: '11px',
                    padding: '2px 8px',
                    borderRadius: '999px',
                    background: 'rgba(74, 222, 128, 0.15)',
                    color: '#4ade80',
                    border: '1px solid rgba(74, 222, 128, 0.3)'
                  }}>
                    ● حي
                  </span>
                )}
              </div>

              <span style={{ color: 'var(--muted-text)', fontSize: '12px' }}>
                {card.subtext}
              </span>
            </div>
          ))}
        </div>

        {/* بطاقة معلومات وتحديث النظام */}
        <div style={{
          background: 'rgba(22, 26, 34, 0.7)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '20px',
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: '#4ade80', fontSize: '14px' }}>● خوادم النظام تعمل بكفاءة عالية</span>
            <span style={{ color: 'var(--muted-text)', fontSize: '13px' }}>| محركات الترجمة نشطة</span>
          </div>
          {lastUpdated && (
            <span style={{ color: 'var(--muted-text)', fontSize: '12px' }}>
              آخر تحديث تلقائي: {lastUpdated}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
