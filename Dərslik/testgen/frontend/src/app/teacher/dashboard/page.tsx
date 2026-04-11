'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

const navCards = [
  {
    href: '/teacher/generate',
    title: 'Variant Yarat',
    desc: 'Toplu sual generasiyası və variant yaratma',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
      </svg>
    ),
    color: 'primary',
  },
  {
    href: '/teacher/bank',
    title: 'Sual Bankı',
    desc: 'Yaradılmış sualları idarə et',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
      </svg>
    ),
    color: 'emerald',
  },
  {
    href: '/teacher/reports',
    title: 'Hesabatlar',
    desc: 'İstifadəçi şikayətləri və düzəlişlər',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
      </svg>
    ),
    color: 'amber',
  },
  {
    href: '/teacher/export',
    title: 'İxrac',
    desc: 'Variantları PDF/Word/JSON formatında yüklə',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
      </svg>
    ),
    color: 'violet',
  },
]

const colorMap: Record<string, { bg: string; icon: string; border: string }> = {
  primary: { bg: 'bg-primary-50', icon: 'text-primary-600', border: 'group-hover:border-primary-300' },
  emerald: { bg: 'bg-emerald-50', icon: 'text-emerald-600', border: 'group-hover:border-emerald-300' },
  amber: { bg: 'bg-amber-50', icon: 'text-amber-600', border: 'group-hover:border-amber-300' },
  violet: { bg: 'bg-violet-50', icon: 'text-violet-600', border: 'group-hover:border-violet-300' },
}

export default function TeacherDashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    api.stats.dashboard().then(setStats).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-bold">Müəllim Paneli</h1>
          <p className="text-primary-100 mt-1">Sualları idarə edin, variantlar yaradın və hesabatları izləyin</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Stats cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-accent-800">{stats.total_questions}</p>
                  <p className="text-xs text-accent-400">Ümumi suallar</p>
                </div>
              </div>
            </div>
            <div className="card p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                  <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-accent-800">{stats.success_rate?.toFixed(1)}%</p>
                  <p className="text-xs text-accent-400">Uğur faizi</p>
                </div>
              </div>
            </div>
            <div className="card p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
                  <svg className="w-5 h-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-accent-800">{stats.total_generations}</p>
                  <p className="text-xs text-accent-400">Ümumi generasiyalar</p>
                </div>
              </div>
            </div>
            <div className="card p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                  <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-accent-800">{stats.avg_generation_time}s</p>
                  <p className="text-xs text-accent-400">Ort. vaxt</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {navCards.map((card) => {
            const colors = colorMap[card.color]
            return (
              <Link
                key={card.href}
                href={card.href}
                className={`card p-6 group flex items-start gap-4 border border-accent-100 ${colors.border}`}
              >
                <div className={`w-12 h-12 rounded-xl ${colors.bg} flex items-center justify-center shrink-0 ${colors.icon}`}>
                  {card.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-accent-800 group-hover:text-primary-700 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-sm text-accent-400 mt-0.5">{card.desc}</p>
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}