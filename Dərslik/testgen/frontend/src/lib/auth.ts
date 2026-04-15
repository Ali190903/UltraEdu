'use client'
import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api } from './api'
import type { User } from './types'
import React from 'react'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

function getSavedUser(): User | null {
  if (typeof window === 'undefined') return null
  try {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(getSavedUser)
  const [loading, setLoading] = useState(!getSavedUser())

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setUser(null)
      localStorage.removeItem('user')
      setLoading(false)
      return
    }
    api.auth.me()
      .then((me) => {
        localStorage.setItem('user', JSON.stringify(me))
        setUser(me)
      })
      .catch(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.auth.login({ email, password })
    localStorage.setItem('token', access_token)
    const me = await api.auth.me()
    localStorage.setItem('user', JSON.stringify(me))
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    api.auth.logout().catch(() => {})  // Clear httpOnly cookie
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    window.location.href = '/' // Logout edəndə ana səhifəyə göndərsin
  }, [])

  return React.createElement(
    AuthContext.Provider,
    { value: { user, loading, login, logout } },
    children
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
