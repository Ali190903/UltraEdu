'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

type Stats = {
  total_questions: number
  total_generations: number
  success_rate: number
  avg_generation_time: number
}

type Variant = {
  id: string
  title: string
  subject: string
  total_questions: number
  created_at: string
}

const subjectLabels: Record<string, string> = {
  az_dili: 'Azərbaycan dili',
  riyaziyyat: 'Riyaziyyat',
  ingilis: 'İngilis dili',
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('az-AZ', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function TeacherDashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [variants, setVariants] = useState<Variant[] | null>(null)

  useEffect(() => {
    api.stats.dashboard().then(setStats).catch(() => {})
    api.variants
      .list()
      .then((list) => setVariants(list.slice(0, 5)))
      .catch(() => setVariants([]))
  }, [])

  return (
    <div className="min-h-screen bg-accent-50">
      {/* Compact hero */}
      <div className="bg-white border-b border-accent-100">
        <div className="max-w-5xl mx-auto px-6 py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-accent-900">Müəllim Paneli</h1>
            <p className="text-sm text-accent-500 mt-0.5">Sualları idarə edin və variantlar yaradın</p>
          </div>
          <Link
            href="/teacher/generate"
            className="btn-primary !py-2.5 !px-5 text-sm inline-flex items-center justify-center gap-2 shrink-0 w-full sm:w-auto"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Yeni Variant
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              color="primary"
              label="Sual bankı"
              hint="Ümumi yaradılmış sualların sayı"
              value={stats.total_questions.toString()}
              icon={
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              }
            />
            <StatCard
              color="emerald"
              label="Uğur faizi"
              hint="Uğurla yaradılan sualların nisbəti"
              value={`${stats.success_rate.toFixed(1)}%`}
              icon={<path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />}
            />
            <StatCard
              color="violet"
              label="Generasiya sayı"
              hint="İndiyə qədər başlanan sual cəhdləri"
              value={stats.total_generations.toString()}
              icon={<path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />}
            />
            <StatCard
              color="amber"
              label="Orta vaxt"
              hint="Bir sualın yaradılma vaxtı (saniyə)"
              value={`${stats.avg_generation_time}s`}
              icon={<path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />}
            />
          </div>
        )}

        {/* Recent variants */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-accent-800">Son yaradılan variantlar</h2>
            <Link
              href="/teacher/bank"
              className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              Hamısına bax →
            </Link>
          </div>

          {variants === null ? (
            <div className="card p-8 text-center text-sm text-accent-400">Yüklənir...</div>
          ) : variants.length === 0 ? (
            <div className="card p-10 text-center">
              <div className="w-12 h-12 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-accent-700 mb-1">Hələ variant yaradılmayıb</h3>
              <p className="text-xs text-accent-400 mb-4">İlk imtahan variantını yaratmaq üçün aşağıdakı düyməyə klikləyin</p>
              <Link
                href="/teacher/generate"
                className="btn-primary inline-flex items-center gap-2 text-sm !py-2 !px-4"
              >
                Variant Yarat
              </Link>
            </div>
          ) : (
            <div className="card divide-y divide-accent-100">
              {variants.map((v) => (
                <Link
                  key={v.id}
                  href={`/teacher/bank?variant=${v.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-accent-50 transition-colors"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-accent-800 truncate">{v.title}</p>
                    <p className="text-xs text-accent-400 mt-0.5">
                      {subjectLabels[v.subject] || v.subject} • {v.total_questions} sual • {formatDate(v.created_at)}
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-accent-300 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                  </svg>
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

const colorMap: Record<string, { bg: string; text: string }> = {
  primary: { bg: 'bg-primary-50', text: 'text-primary-600' },
  emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600' },
  violet: { bg: 'bg-violet-50', text: 'text-violet-600' },
  amber: { bg: 'bg-amber-50', text: 'text-amber-600' },
}

function StatCard({
  color,
  label,
  value,
  hint,
  icon,
}: {
  color: string
  label: string
  value: string
  hint: string
  icon: React.ReactNode
}) {
  const c = colorMap[color]
  return (
    <div className="card p-5" title={hint}>
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg ${c.bg} flex items-center justify-center`}>
          <svg className={`w-5 h-5 ${c.text}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {icon}
          </svg>
        </div>
        <div className="min-w-0">
          <p className="text-2xl font-bold text-accent-800 leading-tight">{value}</p>
          <p className="text-xs text-accent-500 mt-0.5 leading-snug">{label}</p>
        </div>
      </div>
    </div>
  )
}
