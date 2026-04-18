'use client'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function RequireRole({
  children,
  role,
}: {
  children: React.ReactNode
  role: string
}) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.replace('/login')
      } else if (user.role !== role) {
        router.replace('/')
      }
    }
  }, [user, loading, role, router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-accent-50 text-accent-500 font-medium tracking-wide">
        Səlahiyyətlər yoxlanılır...
      </div>
    )
  }

  if (!user || user.role !== role) {
    return null // Redirect occurs via useEffect
  }

  return <>{children}</>
}
