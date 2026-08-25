import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const SUPPORTED_LANGUAGES = [
  { code: 'ar', name: 'العربية (Arabic)' },
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français (French)' },
  { code: 'es', name: 'Español (Spanish)' },
  { code: 'de', name: 'Deutsch (German)' },
]

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [preferredLanguage, setPreferredLanguage] = useState('ar')
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMessage('')

    const trimmedUsername = username.trim()
    if (!trimmedUsername || !password) {
      setErrorMessage('يرجى ملء جميع الحقول المطلوبة')
      return
    }

    if (isRegister) {
      if (trimmedUsername.length < 3 || trimmedUsername.length > 50) {
        setErrorMessage('اسم المستخدم يجب أن يكون بين 3 إلى 50 حرفاً')
        return
      }
      if (!/^[a-zA-Z0-9_]+$/.test(trimmedUsername)) {
        setErrorMessage('اسم المستخدم يجب أن يحتوي على أحرف إنجليزية وأرقام وشرطة سفلية فقط')
        return
      }
      if (password.length < 8) {
        setErrorMessage('كلمة المرور يجب ألا تقل عن 8 أحرف')
        return
      }
    }

    setIsLoading(true)
    try {
      if (isRegister) {
        // 1. تسجيل مستخدم جديد في الباك إند
        await register(trimmedUsername, password, preferredLanguage)
        // 2. تسجيل الدخول تلقائياً للحصول على التوكن
        await login(trimmedUsername, password)
      } else {
        // تسجيل الدخول
        await login(trimmedUsername, password)
      }
      const searchParams = new URLSearchParams(window.location.search)
      const redirectUrl = searchParams.get('redirect') || '/rooms'
      navigate(redirectUrl)
    } catch (err) {
      setErrorMessage(err.message || 'حدث خطأ أثناء الاتصال بالخادم')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{isRegister ? 'إنشاء حساب جديد' : 'تسجيل الدخول'}</h1>
        <p className="auth-subtitle">
          {isRegister
            ? 'انضم إلى LinguaChat وابدأ المحادثة الفورية المترجمة بكل لغات العالم'
            : 'أهلاً بك مجدداً في LinguaChat، سجل دخولك للوصول إلى غرف المحادثة'}
        </p>

        {errorMessage && (
          <div style={{
            background: 'rgba(255, 92, 114, 0.12)',
            border: '1px solid var(--color-error)',
            color: 'var(--color-error)',
            padding: '12px 16px',
            borderRadius: '12px',
            marginBottom: '18px',
            fontSize: '14px',
            lineHeight: 1.5
          }}>
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label className="auth-label">
            اسم المستخدم (Username)
            <input
              className="auth-input"
              type="text"
              placeholder="مثال: ahmed_99"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
              required
            />
          </label>

          <label className="auth-label">
            كلمة المرور (Password)
            <input
              className="auth-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              required
            />
          </label>

          {isRegister && (
            <label className="auth-label">
              اللغة المفضلة للترجمة الفورية
              <select
                className="auth-select"
                value={preferredLanguage}
                onChange={(e) => setPreferredLanguage(e.target.value)}
                disabled={isLoading}
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code} style={{ background: '#16181d', color: '#fff' }}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </label>
          )}

          <button className="auth-button" type="submit" disabled={isLoading}>
            {isLoading ? 'جارٍ التحقق...' : (isRegister ? 'إنشاء الحساب والبدء' : 'دخول')}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '14px', color: 'var(--muted-text)' }}>
          {isRegister ? 'لديك حساب بالفعل؟ ' : 'ليس لديك حساب بعد؟ '}
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister)
              setErrorMessage('')
            }}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent)',
              cursor: 'pointer',
              fontWeight: 700,
              fontFamily: 'inherit',
              padding: '0 4px'
            }}
          >
            {isRegister ? 'تسجيل الدخول' : 'إنشاء حساب جديد'}
          </button>
        </div>
      </div>
    </div>
  )
}
