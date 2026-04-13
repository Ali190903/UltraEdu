'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function Navbar() {
  const { user, logout } = useAuth()
  const [mounted, setMounted] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    setMounted(true)
  }, [])

  const hideOnRoutes = ['/login', '/register']
  const shouldHide =
    pathname?.startsWith('/teacher') ||
    hideOnRoutes.some((r) => pathname === r || pathname?.startsWith(r + '/'))
  if (shouldHide) return null

  return (
    <nav className="glass sticky top-0 z-50 border-b border-accent-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <Image
              src="/logo.png"
              alt="UltraEdu"
              width={36}
              height={36}
              className="transition-transform group-hover:scale-105"
            />
            <span className="text-xl font-bold tracking-tight">
              <span className="text-accent-800">Ultra</span>
              <span className="text-primary-600">Edu</span>
            </span>
          </Link>

          {/* Navigation - only render auth-dependent UI after mount to avoid hydration mismatch */}
          <div className="flex items-center gap-2">
            {!mounted ? null : user ? (
              <>
                <span className="hidden sm:inline text-sm text-accent-500 mr-2">
                  {user.full_name}
                </span>
                {user.role === 'teacher' ? (
                  <Link
                    href="/teacher/dashboard"
                    className="text-sm font-medium text-accent-600 hover:text-primary-600 transition-colors px-3 py-1.5 rounded-lg hover:bg-primary-50"
                  >
                    Müəllim Paneli
                  </Link>
                ) : (
                  <Link
                    href="/generate"
                    className="text-sm font-medium text-accent-600 hover:text-primary-600 transition-colors px-3 py-1.5 rounded-lg hover:bg-primary-50"
                  >
                    Sual yarat
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="text-sm font-medium text-accent-400 hover:text-red-500 transition-colors px-3 py-1.5 rounded-lg hover:bg-red-50 ml-1"
                >
                  Çıxış
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-sm font-medium text-accent-600 hover:text-primary-600 transition-colors px-3 py-2 rounded-lg hover:bg-primary-50"
                >
                  Daxil ol
                </Link>
                <Link
                  href="/register"
                  className="btn-primary text-sm !py-2 !px-4"
                >
                  Qeydiyyat
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}