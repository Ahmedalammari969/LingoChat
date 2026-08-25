import React, { useState, useEffect, useRef } from 'react'

export default function LiveStreamView({
  isHost,
  isGuest,
  hostUsername,
  guestUsername,
  localStream,
  remoteStream,
  guestRequests,
  onStartLive,
  onEndLive,
  onRequestJoin,
  onAcceptGuest,
  onRejectGuest,
  onLeaveGuest,
  onClose,
  hasRequestedJoin,
}) {
  const localVideoRef = useRef(null)
  const remoteVideoRef = useRef(null)

  const [isMuted, setIsMuted] = useState(false)
  const [isVideoOff, setIsVideoOff] = useState(false)

  // Attach local stream to video element
  useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream
    }
  }, [localStream])

  // Attach remote stream to video element
  useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream
    }
  }, [remoteStream])

  // Handle Mute Toggle
  const toggleMute = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = isMuted
        setIsMuted(!isMuted)
      }
    }
  }

  // Handle Video Toggle
  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = isVideoOff
        setIsVideoOff(!isVideoOff)
      }
    }
  }

  const isCoHostActive = Boolean(guestUsername)

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      background: 'rgba(10, 13, 20, 0.96)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      flexDirection: 'column',
      color: '#fff',
      fontFamily: 'inherit',
    }}>
      {/* ── Top Bar ── */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 24px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(22, 26, 34, 0.8)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(239, 68, 68, 0.2)',
            color: '#ef4444',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '13px',
            fontWeight: 800,
            letterSpacing: '0.5px',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#ef4444',
              boxShadow: '0 0 10px #ef4444',
            }} />
            🔴 بث مباشر (LIVE)
          </span>
          <span style={{ color: 'var(--muted-text)', fontSize: '14px' }}>
            المضيف: <strong style={{ color: '#fff' }}>{hostUsername}</strong>
          </span>
        </div>

        <button
          type="button"
          onClick={onClose}
          style={{
            background: 'rgba(255, 255, 255, 0.08)',
            border: 'none',
            color: '#fff',
            padding: '8px 16px',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            fontFamily: 'inherit',
          }}
        >
          ✕ إغلاق النافذة
        </button>
      </div>

      {/* ── Main Video Area (TikTok Split Screen Layout) ── */}
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: isCoHostActive ? '1fr 1fr' : '1fr',
        gap: '16px',
        padding: '20px',
        maxHeight: 'calc(100vh - 160px)',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        {/* Host Video Box */}
        <div style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          maxHeight: isCoHostActive ? '70vh' : '75vh',
          background: '#000',
          borderRadius: '24px',
          overflow: 'hidden',
          border: '2px solid rgba(99, 102, 241, 0.4)',
          boxShadow: '0 12px 36px rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <video
            ref={isHost ? localVideoRef : remoteVideoRef}
            autoPlay
            playsInline
            muted={isHost} // Mute own playback to avoid echo
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: isHost ? 'scaleX(-1)' : 'none', // Mirror self camera
            }}
          />
          <div style={{
            position: 'absolute',
            top: '14px',
            right: '14px',
            background: 'rgba(0, 0, 0, 0.65)',
            backdropFilter: 'blur(8px)',
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 700,
            color: '#a5b4fc',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}>
            👑 المضيف: {hostUsername}
          </div>
        </div>

        {/* Guest Video Box (Active when guest accepted) */}
        {isCoHostActive && (
          <div style={{
            position: 'relative',
            width: '100%',
            height: '100%',
            maxHeight: '70vh',
            background: '#000',
            borderRadius: '24px',
            overflow: 'hidden',
            border: '2px solid rgba(16, 185, 129, 0.4)',
            boxShadow: '0 12px 36px rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <video
              ref={isGuest ? localVideoRef : remoteVideoRef}
              autoPlay
              playsInline
              muted={isGuest}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                transform: isGuest ? 'scaleX(-1)' : 'none',
              }}
            />
            <div style={{
              position: 'absolute',
              top: '14px',
              right: '14px',
              background: 'rgba(0, 0, 0, 0.65)',
              backdropFilter: 'blur(8px)',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 700,
              color: '#6ee7b7',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}>
              🎙️ الضيف: {guestUsername}
            </div>
          </div>
        )}
      </div>

      {/* ── Host Guest Requests Banner (When viewers request to join) ── */}
      {isHost && guestRequests.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '90px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10000,
          background: 'rgba(30, 41, 59, 0.95)',
          border: '1px solid var(--accent)',
          borderRadius: '20px',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
          backdropFilter: 'blur(10px)',
          animation: 'fadeIn 0.3s ease',
        }}>
          <span style={{ fontSize: '14px', fontWeight: 600 }}>
            ✋ <strong>{guestRequests[0].username}</strong> يطلب الصعود للبث معك!
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              onClick={() => onAcceptGuest(guestRequests[0].user_id, guestRequests[0].username)}
              style={{
                background: '#10b981',
                color: '#fff',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '10px',
                fontSize: '13px',
                fontWeight: 700,
                cursor: 'pointer',
                fontFamily: 'inherit',
              }}
            >
              قبول ✅
            </button>
            <button
              type="button"
              onClick={() => onRejectGuest(guestRequests[0].user_id)}
              style={{
                background: 'rgba(239, 68, 68, 0.2)',
                color: '#ef4444',
                border: '1px solid #ef4444',
                padding: '6px 14px',
                borderRadius: '10px',
                fontSize: '13px',
                fontWeight: 700,
                cursor: 'pointer',
                fontFamily: 'inherit',
              }}
            >
              رفض ❌
            </button>
          </div>
        </div>
      )}

      {/* ── Bottom Controls Bar ── */}
      <div style={{
        padding: '16px 24px',
        background: 'rgba(22, 26, 34, 0.9)',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '16px',
      }}>
        {/* Controls for Host or Active Guest */}
        {(isHost || isGuest) ? (
          <>
            <button
              type="button"
              onClick={toggleMute}
              style={{
                background: isMuted ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                color: isMuted ? '#ef4444' : '#fff',
                border: isMuted ? '1px solid #ef4444' : '1px solid rgba(255,255,255,0.1)',
                padding: '10px 20px',
                borderRadius: '16px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                fontFamily: 'inherit',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {isMuted ? '🔇 كتم المايك (مكتوم)' : '🎙️ المايك شغال'}
            </button>

            <button
              type="button"
              onClick={toggleVideo}
              style={{
                background: isVideoOff ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                color: isVideoOff ? '#ef4444' : '#fff',
                border: isVideoOff ? '1px solid #ef4444' : '1px solid rgba(255,255,255,0.1)',
                padding: '10px 20px',
                borderRadius: '16px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600,
                fontFamily: 'inherit',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {isVideoOff ? '🚫 الكاميرا مقفلة' : '📹 الكاميرا شغالة'}
            </button>

            {isHost ? (
              <button
                type="button"
                onClick={onEndLive}
                style={{
                  background: '#ef4444',
                  color: '#fff',
                  border: 'none',
                  padding: '10px 24px',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 700,
                  fontFamily: 'inherit',
                }}
              >
                🛑 إنهاء البث للجميع
              </button>
            ) : (
              <button
                type="button"
                onClick={onLeaveGuest}
                style={{
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#ef4444',
                  border: '1px solid #ef4444',
                  padding: '10px 24px',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 700,
                  fontFamily: 'inherit',
                }}
              >
                نزول من البث (عودة كمشاهد)
              </button>
            )}
          </>
        ) : (
          /* Controls for Viewers */
          <div>
            {hasRequestedJoin ? (
              <span style={{
                background: 'rgba(234, 179, 8, 0.15)',
                color: '#eab308',
                border: '1px solid #eab308',
                padding: '10px 24px',
                borderRadius: '16px',
                fontSize: '14px',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                ⏳ تم إرسال طلب الصعود، بانتظار موافقة المضيف...
              </span>
            ) : (
              <button
                type="button"
                onClick={onRequestJoin}
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 28px',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  fontSize: '15px',
                  fontWeight: 700,
                  boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
                  fontFamily: 'inherit',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                ✋ طلب الصعود للمشاركة في البث
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
