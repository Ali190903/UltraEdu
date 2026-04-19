'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth'

type NavItem = {
  href: string
  label: string
  icon: React.ReactNode
}

const items: NavItem[] = [
  {
    href: '/teacher/dashboard',
    label: 'Panel',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l9-9 9 9M5 10v10a1 1 0 001 1h3v-6h6v6h3a1 1 0 001-1V10" />
      </svg>
    ),
  },
  {
    href: '/teacher/generate',
    label: 'Variant Yarat',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
      </svg>
    ),
  },
  {
    href: '/teacher/bank',
    label: 'Sual Bankı',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75" />
      </svg>
    ),
  },
  {
    href: '/teacher/export',
    label: 'İxrac',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
      </svg>
    ),
  },
  {
    href: '/teacher/reports',
    label: 'Hesabatlar',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
      </svg>
    ),
  },
]

export default function TeacherSidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0 sticky top-0 self-start h-screen border-r border-accent-100 bg-white/80 backdrop-blur">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2.5 px-5 h-16 border-b border-accent-100 shrink-0">
        <Image src="/logo.svg" alt="UltraEdu" width={32} height={32} />
        <span className="text-lg font-bold tracking-tight">
          <span className="text-accent-800">Ultra</span>
          <span className="text-primary-600">Edu</span>
        </span>
      </Link>

      {/* Nav */}
      <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
        <p className="px-3 pt-2 pb-3 text-[11px] font-semibold uppercase tracking-wider text-accent-400">
          Müəllim
        </p>
        {items.map((item) => {
          const active =
            pathname === item.href || pathname?.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                active
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-accent-600 hover:bg-accent-50 hover:text-accent-900'
              }`}
            >
              <span
                className={`absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full transition-all ${
                  active ? 'bg-primary-600' : 'bg-transparent'
                }`}
              />
              <span
                className={`transition-colors ${
                  active ? 'text-primary-600' : 'text-accent-400 group-hover:text-accent-700'
                }`}
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* User + logout */}
      {mounted && user && (
        <div className="p-3 border-t border-accent-100 shrink-0">
          <div className="px-3 py-2">
            <p className="text-sm font-medium text-accent-800 truncate">{user.full_name}</p>
            <p className="text-xs text-accent-400 truncate">{user.email}</p>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 mt-1 rounded-lg text-sm font-medium text-accent-500 hover:text-red-600 hover:bg-red-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
            </svg>
            Çıxış
          </button>
        </div>
      )}
    </aside>
  )
}
