/**
 * LinguaChat — WebRTC Live Stream Service
 * 
 * Manages a SINGLE RTCPeerConnection for 1:1 live streaming.
 * Simplified to avoid key mismatch issues between host and guest.
 */

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
  ],
}

export class WebRTCService {
  constructor(options = {}) {
    this.onRemoteStream = options.onRemoteStream || (() => {})
    this.onLocalStream = options.onLocalStream || (() => {})
    this.sendSignal = options.sendSignal || (() => {})
    
    this.localStream = null
    this.pc = null               // Single peer connection
    this.pendingCandidates = []  // ICE candidates received before remoteDescription
    this._targetUserId = null    // Who we're connected to
  }

  /**
   * Start local camera and microphone stream.
   */
  async startLocalStream(video = true, audio = true) {
    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        throw new Error(
          'متصفحك يحظر الكاميرا لأن الموقع غير محمي (HTTPS). يرجى فتح الرابط باستخدام https:// أو السماح بالأذونات.'
        )
      }
      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: video ? { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' } : false,
        audio: audio ? { echoCancellation: true, noiseSuppression: true } : false,
      })
      console.log('[WebRTC] ✅ Local stream obtained, tracks:', this.localStream.getTracks().map(t => t.kind))
      this.onLocalStream(this.localStream)
      return this.localStream
    } catch (err) {
      console.error('[WebRTC] ❌ Failed to get user media:', err)
      throw err
    }
  }

  /**
   * Stop local camera and microphone.
   */
  stopLocalStream() {
    if (this.localStream) {
      this.localStream.getTracks().forEach((t) => t.stop())
      this.localStream = null
    }
    this._closePeerConnection()
  }

  /**
   * Toggle audio mute.
   */
  toggleAudio(enabled) {
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach((t) => (t.enabled = enabled))
    }
  }

  /**
   * Toggle video enabled.
   */
  toggleVideo(enabled) {
    if (this.localStream) {
      this.localStream.getVideoTracks().forEach((t) => (t.enabled = enabled))
    }
  }

  /**
   * Create the single RTCPeerConnection (if not already created).
   */
  _ensurePeerConnection(targetUserId) {
    if (this.pc) return this.pc

    this._targetUserId = targetUserId
    const pc = new RTCPeerConnection(ICE_SERVERS)

    // Add all local tracks to the connection
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => {
        pc.addTrack(track, this.localStream)
        console.log('[WebRTC] ➕ Added local track:', track.kind)
      })
    } else {
      console.warn('[WebRTC] ⚠️ No local stream when creating peer connection!')
    }

    // Handle remote track reception
    pc.ontrack = (event) => {
      console.log('[WebRTC] 🎬 Remote track received:', event.track.kind, 'readyState:', event.track.readyState)
      const stream = event.streams?.[0] || new MediaStream([event.track])
      // Create a new MediaStream wrapper to trigger React state update
      const freshStream = new MediaStream(stream.getTracks())
      console.log('[WebRTC] 🎬 Calling onRemoteStream with', freshStream.getTracks().length, 'tracks')
      this.onRemoteStream(targetUserId, freshStream)
    }

    // Handle ICE candidate generation
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('[WebRTC] 🧊 Sending ICE candidate to:', targetUserId)
        this.sendSignal('RTC_ICE_CANDIDATE', {
          target_user_id: targetUserId,
          candidate: event.candidate.toJSON(),
        })
      }
    }

    pc.oniceconnectionstatechange = () => {
      console.log('[WebRTC] 🔌 ICE connection state:', pc.iceConnectionState)
    }

    pc.onconnectionstatechange = () => {
      console.log('[WebRTC] 📡 Connection state:', pc.connectionState)
    }

    pc.onsignalingstatechange = () => {
      console.log('[WebRTC] 🔄 Signaling state:', pc.signalingState)
    }

    this.pc = pc
    return pc
  }

  /**
   * Flush queued ICE candidates after remoteDescription is set.
   */
  async _flushPendingCandidates() {
    while (this.pendingCandidates.length > 0) {
      const cand = this.pendingCandidates.shift()
      try {
        await this.pc.addIceCandidate(new RTCIceCandidate(cand))
        console.log('[WebRTC] 🧊 Flushed queued ICE candidate')
      } catch (err) {
        console.warn('[WebRTC] ⚠️ Failed to flush ICE candidate:', err)
      }
    }
  }

  /**
   * Guest calls this: create offer and send to host.
   */
  async createOffer(targetUserId) {
    console.log('[WebRTC] 📤 Creating offer for:', targetUserId)
    const pc = this._ensurePeerConnection(targetUserId)
    
    const offer = await pc.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: true,
    })
    await pc.setLocalDescription(offer)
    console.log('[WebRTC] 📤 Offer created, sending to:', targetUserId)

    this.sendSignal('RTC_OFFER', {
      target_user_id: targetUserId,
      sdp: pc.localDescription.toJSON(),
    })
  }

  /**
   * Host calls this: handle incoming offer from guest, send answer back.
   */
  async handleOffer(senderUserId, sdp) {
    console.log('[WebRTC] 📥 Received offer from:', senderUserId)
    const pc = this._ensurePeerConnection(senderUserId)

    // Ensure local tracks are attached
    if (this.localStream) {
      const existingSenders = pc.getSenders()
      this.localStream.getTracks().forEach((track) => {
        const alreadyAdded = existingSenders.some((s) => s.track === track)
        if (!alreadyAdded) {
          pc.addTrack(track, this.localStream)
          console.log('[WebRTC] ➕ Added local track before answer:', track.kind)
        }
      })
    }

    await pc.setRemoteDescription(new RTCSessionDescription(sdp))
    console.log('[WebRTC] ✅ Remote description set (offer)')
    await this._flushPendingCandidates()

    const answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    console.log('[WebRTC] 📤 Answer created, sending to:', senderUserId)

    this.sendSignal('RTC_ANSWER', {
      target_user_id: senderUserId,
      sdp: pc.localDescription.toJSON(),
    })
  }

  /**
   * Guest calls this: handle incoming answer from host.
   */
  async handleAnswer(senderUserId, sdp) {
    console.log('[WebRTC] 📥 Received answer from:', senderUserId)
    if (!this.pc) {
      console.error('[WebRTC] ❌ No peer connection exists to set answer on!')
      return
    }
    await this.pc.setRemoteDescription(new RTCSessionDescription(sdp))
    console.log('[WebRTC] ✅ Remote description set (answer)')
    await this._flushPendingCandidates()
  }

  /**
   * Handle incoming ICE candidate from the other peer.
   */
  async handleCandidate(senderUserId, candidate) {
    if (!this.pc || !this.pc.remoteDescription) {
      console.log('[WebRTC] 🧊 Queueing ICE candidate (no remote description yet)')
      this.pendingCandidates.push(candidate)
      return
    }

    try {
      await this.pc.addIceCandidate(new RTCIceCandidate(candidate))
      console.log('[WebRTC] 🧊 Added ICE candidate successfully')
    } catch (err) {
      console.warn('[WebRTC] ⚠️ Failed to add ICE candidate:', err)
    }
  }

  /**
   * Close the peer connection.
   */
  _closePeerConnection() {
    if (this.pc) {
      this.pc.close()
      this.pc = null
    }
    this.pendingCandidates = []
    this._targetUserId = null
  }

  /**
   * Close all connections and stop stream.
   */
  closeAllConnections() {
    this.stopLocalStream()
  }
}
