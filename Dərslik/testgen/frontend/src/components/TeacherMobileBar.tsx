'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useRef, useState } from 'react'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth'

const items = [
  { href: '/teacher/dashboard', label: 'Panel' },
  { href: '/teacher/generate', label: 'Variant Yarat' },
  { href: '/teacher/bank', label: 'Sual Bankı' },
  { href: '/teacher/export', label: 'İxrac' },
  { href: '/teacher/reports', label: 'Hesabatlar' },
]

export default function TeacherMobileBar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => setMounted(true), [])
  useEffect(() => setOpen(false), [pathname])

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  return (
    <header className="lg:hidden sticky top-0 z-40 bg-white/90 backdrop-blur border-b border-accent-100">
      <div className="flex items-center justify-between h-14 px-4">
        <Link href="/teacher/dashboard" className="flex items-center gap-2">
          <Image src="/logo.svg" alt="UltraEdu" width={28} height={28} />
          <span className="text-base font-bold tracking-tight">
            <span className="text-accent-800">Ultra</span>
            <span className="text-primary-600">Edu</span>
          </span>
        </Link>
        <button
          onClick={() => setOpen((v) => !v)}
          aria-label="Menyu"
          className="p-2 -mr-2 rounded-lg hover:bg-accent-50 text-accent-700"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            {open ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
            )}
          </svg>
        </button>
      </div>

      {open && (
        <div ref={menuRef} className="border-t border-accent-100 bg-white">
          <nav className="p-3 space-y-1">
            {items.map((item) => {
              const active = pathname === item.href || pathname?.startsWith(item.href + '/')
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`block px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active ? 'bg-primary-50 text-primary-700' : 'text-accent-700 hover:bg-accent-50'
                  }`}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
          {mounted && user && (
            <div className="border-t border-accent-100 p-3">
              <div className="px-3 py-2">
                <p className="text-sm font-medium text-accent-800 truncate">{user.full_name}</p>
                <p className="text-xs text-accent-400 truncate">{user.email}</p>
              </div>
              <button
                onClick={logout}
                className="w-full text-left px-3 py-2 mt-1 rounded-lg text-sm font-medium text-accent-500 hover:text-red-600 hover:bg-red-50"
              >
                Çıxış
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  )
}
