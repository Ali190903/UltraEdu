'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

const formatInfo: Record<string, { label: string; cls: string; icon: string }> = {
  pdf: {
    label: 'PDF',
    cls: 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100',
    icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m.75 12l3 3m0 0l3-3m-3 3v-6m-1.5-9H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  },
  word: {
    label: 'Word',
    cls: 'bg-indigo-50 text-indigo-600 border border-indigo-200 hover:bg-indigo-100',
    icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  },
  json: {
    label: 'JSON',
    cls: 'bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100',
    icon: 'M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5',
  },
  text: {
    label: 'TXT',
    cls: 'bg-stone-50 text-stone-600 border border-stone-200 hover:bg-stone-100',
    icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  },
}

export default function ExportPage() {
  const [variants, setVariants] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.variants
      .list()
      .then(setVariants)
      .catch(() => setVariants([]))
      .finally(() => setLoading(false))
  }, [])

  const subjectNames: Record<string, string> = {
    az_dili: 'Azərbaycan dili',
    riyaziyyat: 'Riyaziyyat',
    ingilis: 'İngilis dili',
  }

  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-white border-b border-accent-100 shadow-sm relative z-10">
        <div className="max-w-5xl mx-auto px-6 py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div>
            <h1 className="text-2xl font-extrabold text-accent-900 tracking-tight">İxrac</h1>
            <p className="text-[0.95rem] text-accent-500 mt-1">Variantları müxtəlif formatlarda yükləyin</p>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
        {/* Loading */}
        {loading && (
          <div className="card p-12 text-center">
            <svg className="animate-spin h-8 w-8 text-primary-500 mx-auto mb-3" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-accent-400 text-sm">Variantlar yüklənir...</p>
          </div>
        )}

        {/* Variants list */}
        {!loading && variants.map((v) => (
          <div key={v.id} className="card p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4 min-w-0">
              <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
                <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
                </svg>
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-accent-800 text-sm truncate">{v.title}</p>
                <p className="text-xs text-accent-400 mt-0.5 truncate">
                  {subjectNames[v.subject] || v.subject} | {v.total_questions} sual
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 sm:shrink-0">
              {Object.entries(formatInfo).map(([format, info]) => (
                <button
                  key={format}
                  onClick={() => api.variants.export(v.id, format)}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${info.cls}`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={info.icon} />
                  </svg>
                  {info.label}
                </button>
              ))}
            </div>
          </div>
        ))}

        {!loading && variants.length === 0 && (
          <div className="card p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-accent-100 flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
            </div>
            <p className="text-accent-500 font-medium">Hələ variant yoxdur</p>
            <p className="text-accent-400 text-sm mt-1">Əvvəlcə variant yaradın, sonra buradan ixrac edə bilərsiniz</p>
          </div>
        )}
      </div>
    </div>
  )
}