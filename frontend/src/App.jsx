/**
 * LinguaChat — Root Application Component
 *
 * Approved frontend stack (Architecture Freeze 2026-08-13):
 *   Framework:  React 18
 *   Build tool: Vite
 *   Routing:    React Router v6
 *
 * Approved routes (FROZEN):
 *   /login           → Login page
 *   /rooms           → Rooms list page
 *   /rooms/:roomId   → Chat room page
 *   /dashboard       → Dashboard page
 *
 * Full implementation: Ahmed Alammari — TASK: Frontend / Integration
 */

import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import LoginPage from './pages/LoginPage.jsx'
import RoomsPage from './pages/RoomsPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/rooms" element={<RoomsPage />} />
        <Route path="/rooms/:roomId" element={<ChatPage />} />
        <Route path="/chat/:roomId" element={<Navigate to="/rooms/:roomId" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        {/* Catch-all: redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
