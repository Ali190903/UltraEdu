'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

const reportTypeLabels: Record<string, string> = {
  wrong_answer: 'Səhv cavab',
  unclear: 'Aydın deyil',
  off_topic: 'Mövzuya uyğun deyil',
  grammar: 'Qrammatik səhv',
  other: 'Digər',
}

const statusTabs = [
  { id: 'pending', label: 'Gözləyir', icon: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'fixed', label: 'Düzəldildi', icon: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'rejected', label: 'Rədd edildi', icon: 'M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
]

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [filter, setFilter] = useState('pending')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.reports
      .list(filter)
      .then(setReports)
      .catch(() => setReports([]))
      .finally(() => setLoading(false))
  }, [filter])

  const resolve = async (id: string, status: string) => {
    await api.reports.resolve(id, status)
    setReports(reports.filter((r) => r.id !== id))
  }

  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-bold">Hesabatlar</h1>
          <p className="text-primary-100 mt-1">İstifadəçi şikayətlərini idarə edin və sualları düzəldin</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        {/* Status tabs */}
        <div className="flex gap-2">
          {statusTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium border-1.5 transition-all duration-200 cursor-pointer ${
                filter === tab.id
                  ? 'bg-primary-50 border-primary-400 text-primary-700'
                  : 'bg-white border-accent-200 text-accent-500 hover:border-accent-300'
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d={tab.icon} />
              </svg>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="card p-12 text-center">
            <svg className="animate-spin h-8 w-8 text-primary-500 mx-auto mb-3" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-accent-400 text-sm">Hesabatlar yüklənir...</p>
          </div>
        )}

        {/* Reports list */}
        {!loading && (
          <div className="space-y-3">
            {reports.map((r) => (
              <div key={r.id} className="card p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-accent-800">
                        {reportTypeLabels[r.report_type] || r.report_type}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-400">
                        {r.report_type}
                      </span>
                    </div>
                    {r.comment && (
                      <p className="text-sm text-accent-500 leading-relaxed">{r.comment}</p>
                    )}
                    <p className="text-xs text-accent-400 flex items-center gap-1">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                      Sual ID: {r.question_id}
                    </p>
                  </div>

                  {filter === 'pending' && (
                    <div className="flex gap-2 shrink-0">
                      <button
                        onClick={() => resolve(r.id, 'fixed')}
                        className="px-3 py-1.5 bg-emerald-500 text-white text-sm font-medium rounded-lg hover:bg-emerald-600 transition-colors cursor-pointer"
                      >
                        Düzəlt
                      </button>
                      <button
                        onClick={() => resolve(r.id, 'rejected')}
                        className="px-3 py-1.5 bg-accent-200 text-accent-600 text-sm font-medium rounded-lg hover:bg-accent-300 transition-colors cursor-pointer"
                      >
                        Rədd et
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {reports.length === 0 && (
              <div className="card p-12 text-center">
                <div className="w-12 h-12 rounded-full bg-accent-100 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-accent-400 text-sm">Bu statusda hesabat yoxdur</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}