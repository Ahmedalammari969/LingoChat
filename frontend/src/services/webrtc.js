/**
 * LinguaChat — WebRTC Live Stream Service
 * 
 * Manages WebRTC Peer Connections for TikTok-style interactive live streaming.
 * Handles local camera/mic media streams, SDP negotiation, and ICE candidates.
 */

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
}

export class WebRTCService {
  constructor(options = {}) {
    this.onRemoteStream = options.onRemoteStream || (() => {})
    this.onLocalStream = options.onLocalStream || (() => {})
    this.sendSignal = options.sendSignal || (() => {})
    
    this.localStream = null
    this.peers = new Map() // targetUserId -> RTCPeerConnection
  }

  /**
   * Start local camera and microphone stream.
   */
  async startLocalStream(video = true, audio = true) {
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: video ? { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' } : false,
        audio: audio ? { echoCancellation: true, noiseSuppression: true } : false,
      })
      this.onLocalStream(this.localStream)
      return this.localStream
    } catch (err) {
      console.error('[WebRTC] Failed to get user media:', err)
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
    this.closeAllConnections()
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
   * Get or create a peer connection for a specific target user.
   */
  getOrCreatePeer(targetUserId) {
    if (this.peers.has(targetUserId)) {
      return this.peers.get(targetUserId)
    }

    const pc = new RTCPeerConnection(ICE_SERVERS)

    // Add local tracks if available
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => {
        pc.addTrack(track, this.localStream)
      })
    }

    // Handle remote track reception
    pc.ontrack = (event) => {
      if (event.streams && event.streams[0]) {
        this.onRemoteStream(targetUserId, event.streams[0])
      }
    }

    // Handle ICE candidate generation
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.sendSignal('RTC_ICE_CANDIDATE', {
          target_user_id: targetUserId,
          candidate: event.candidate,
        })
      }
    }

    this.peers.set(targetUserId, pc)
    return pc
  }

  /**
   * Initiate a call/offer to a target user.
   */
  async createOffer(targetUserId) {
    const pc = this.getOrCreatePeer(targetUserId)
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    this.sendSignal('RTC_OFFER', {
      target_user_id: targetUserId,
      sdp: offer,
    })
  }

  /**
   * Handle incoming offer and return answer.
   */
  async handleOffer(targetUserId, sdp) {
    const pc = this.getOrCreatePeer(targetUserId)
    await pc.setRemoteDescription(new RTCSessionDescription(sdp))
    const answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    this.sendSignal('RTC_ANSWER', {
      target_user_id: targetUserId,
      sdp: answer,
    })
  }

  /**
   * Handle incoming answer.
   */
  async handleAnswer(targetUserId, sdp) {
    const pc = this.peers.get(targetUserId)
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(sdp))
    }
  }

  /**
   * Handle incoming ICE candidate.
   */
  async handleCandidate(targetUserId, candidate) {
    const pc = this.peers.get(targetUserId)
    if (pc && candidate) {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(candidate))
      } catch (err) {
        console.warn('[WebRTC] Failed to add ICE candidate:', err)
      }
    }
  }

  /**
   * Close a specific peer connection.
   */
  closePeer(targetUserId) {
    const pc = this.peers.get(targetUserId)
    if (pc) {
      pc.close()
      this.peers.delete(targetUserId)
    }
  }

  /**
   * Close all active peer connections.
   */
  closeAllConnections() {
    this.peers.forEach((pc) => pc.close())
    this.peers.clear()
  }
}
