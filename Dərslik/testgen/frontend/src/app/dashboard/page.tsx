'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (!user) {
      router.push('/login')
      return
    }
    router.push(user.role === 'teacher' ? '/teacher/dashboard' : '/generate')
  }, [user, loading, router])

  return (
    <div className="min-h-screen bg-accent-50 flex items-center justify-center">
      <div className="text-center">
        <svg className="animate-spin h-8 w-8 text-primary-500 mx-auto mb-3" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p className="text-accent-400 text-sm">Yönləndirilir...</p>
      </div>
    </div>
  )
}