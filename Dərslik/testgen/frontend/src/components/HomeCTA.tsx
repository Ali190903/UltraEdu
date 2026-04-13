'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'

type Variant = 'hero' | 'footer'

export default function HomeCTA({ variant }: { variant: Variant }) {
  const { user } = useAuth()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  if (variant === 'hero') {
    if (!mounted) {
      return <div className="h-[3.25rem]" aria-hidden />
    }

    if (user) {
      const href = user.role === 'teacher' ? '/teacher/dashboard' : '/generate'
      const label = user.role === 'teacher' ? 'Müəllim panelinə keç' : 'Sual yaratmağa davam et'
      return (
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href={href} className="btn-primary text-base !py-3 !px-8 inline-flex items-center justify-center gap-2">
            {label}
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      )
    }

    return (
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link href="/register" className="btn-primary text-base !py-3 !px-8 inline-flex items-center justify-center gap-2">
          Pulsuz başla
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </Link>
        <Link href="/login" className="btn-outline text-base !py-3 !px-8 inline-flex items-center justify-center">
          Daxil ol
        </Link>
      </div>
    )
  }

  // footer
  if (!mounted) {
    return <div className="h-[3.25rem]" aria-hidden />
  }

  if (user) {
    const href = user.role === 'teacher' ? '/teacher/dashboard' : '/generate'
    const label = user.role === 'teacher' ? 'Panelə keç' : 'Sual yarat'
    return (
      <Link
        href={href}
        className="inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-8 py-3 rounded-lg hover:bg-primary-50 transition-all hover:shadow-lg"
      >
        {label}
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
        </svg>
      </Link>
    )
  }

  return (
    <Link
      href="/register"
      className="inline-flex items-center gap-2 bg-white text-primary-700 font-semibold px-8 py-3 rounded-lg hover:bg-primary-50 transition-all hover:shadow-lg"
    >
      Qeydiyyatdan keç
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
      </svg>
    </Link>
  )
}
