/**
 * LinguaChat — Progressive Web App Service Worker
 * 
 * Provides offline caching for static assets, network-first strategy for dynamic content,
 * and enables native PWA installation across Chrome, Edge, Safari, Android, and iOS.
 */

const CACHE_NAME = 'linguachat-pwa-v1'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
  '/icon-192.png',
  '/icon-512.png',
]

// ── Install Event ─────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[LinguaChat SW] Non-critical cache add warning:', err)
      })
    })
  )
  self.skipWaiting()
})

// ── Activate Event ────────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key)
          }
        })
      )
    })
  )
  self.clients.claim()
})

// ── Fetch Event (Network-First with Cache Fallback) ───────────────────────────
self.addEventListener('fetch', (event) => {
  const request = event.request

  // Never intercept WebSocket or API mutations
  if (
    request.url.includes('/ws') ||
    request.url.includes('/api/v1') ||
    request.method !== 'GET'
  ) {
    return
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cache successful responses for static assets
        if (response && response.status === 200 && response.type === 'basic') {
          const responseClone = response.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone)
          })
        }
        return response
      })
      .catch(() => {
        return caches.match(request).then((cached) => {
          if (cached) return cached
          // If HTML request failed and offline, return cached root index.html
          if (request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/index.html')
          }
        })
      })
  )
})
