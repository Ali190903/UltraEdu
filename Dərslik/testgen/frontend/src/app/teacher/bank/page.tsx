'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import QuestionCard from '@/components/QuestionCard'
import LatexRenderer from '@/components/LatexRenderer'
import type { Question } from '@/lib/types'

const subjectNames: Record<string, string> = {
  az_dili: 'Azərbaycan dili',
  riyaziyyat: 'Riyaziyyat',
  ingilis: 'İngilis dili',
}

const difficultyLabels: Record<string, { label: string; cls: string }> = {
  easy: { label: 'Asan', cls: 'bg-emerald-50 text-emerald-600' },
  medium: { label: 'Orta', cls: 'bg-amber-50 text-amber-600' },
  hard: { label: 'Çətin', cls: 'bg-rose-50 text-rose-600' },
}

const statusLabels: Record<string, { label: string; cls: string }> = {
  active: { label: 'Aktiv', cls: 'bg-emerald-50 text-emerald-600' },
  reported: { label: 'Şikayət', cls: 'bg-rose-50 text-rose-600' },
  disabled: { label: 'Deaktiv', cls: 'bg-accent-100 text-accent-500' },
}

export default function QuestionBankPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({ subject: '', difficulty: '', page: 1 })
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (filters.subject) params.set('subject', filters.subject)
    if (filters.difficulty) params.set('difficulty', filters.difficulty)
    params.set('page', String(filters.page))
    params.set('page_size', '20')

    api.questions
      .list(params.toString())
      .then((res) => {
        setQuestions(res.items)
        setTotal(res.total)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [filters])

  const totalPages = Math.ceil(total / 20)

  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-bold">Sual Bankı</h1>
          <p className="text-primary-100 mt-1">Yaradılmış bütün sualları idarə edin — {total} sual</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        {/* Filters */}
        <div className="card p-4 flex flex-wrap items-center gap-3">
          <select
            value={filters.subject}
            onChange={(e) => setFilters({ ...filters, subject: e.target.value, page: 1 })}
            className="input-field !w-auto bg-white cursor-pointer appearance-none pr-10"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 0.75rem center',
            }}
          >
            <option value="">Bütün fənlər</option>
            <option value="az_dili">Azərbaycan dili</option>
            <option value="riyaziyyat">Riyaziyyat</option>
            <option value="ingilis">İngilis dili</option>
          </select>

          <select
            value={filters.difficulty}
            onChange={(e) => setFilters({ ...filters, difficulty: e.target.value, page: 1 })}
            className="input-field !w-auto bg-white cursor-pointer appearance-none pr-10"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 0.75rem center',
            }}
          >
            <option value="">Bütün çətinliklər</option>
            <option value="easy">Asan</option>
            <option value="medium">Orta</option>
            <option value="hard">Çətin</option>
          </select>

          <span className="text-sm text-accent-400 ml-auto">
            {total} nəticə
          </span>
        </div>

        {/* Loading */}
        {loading && (
          <div className="card p-12 text-center">
            <svg className="animate-spin h-8 w-8 text-primary-500 mx-auto mb-3" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-accent-400 text-sm">Suallar yüklənir...</p>
          </div>
        )}

        {/* Questions list */}
        {!loading && (
          <div className="space-y-3">
            {questions.map((q, idx) => {
              const isExpanded = expandedId === q.id
              const diff = difficultyLabels[q.difficulty] || { label: q.difficulty, cls: 'bg-accent-100 text-accent-500' }
              const status = statusLabels[q.status] || { label: q.status, cls: 'bg-accent-100 text-accent-500' }

              if (isExpanded) {
                return (
                  <div key={q.id}>
                    <button
                      onClick={() => setExpandedId(null)}
                      className="text-xs text-accent-400 hover:text-primary-600 mb-2 cursor-pointer"
                    >
                      ← Bağla
                    </button>
                    <QuestionCard
                      question={{
                        question_text: q.question_text,
                        options: q.options || null,
                        matching_pairs: null,
                        correct_answer: q.correct_answer,
                        explanation: q.explanation,
                        latex_content: q.latex_content || null,
                        source_reference: q.source_reference,
                        bloom_level: q.bloom_level,
                        difficulty: q.difficulty,
                      }}
                      questionId={q.id}
                      index={(filters.page - 1) * 20 + idx}
                    />
                  </div>
                )
              }

              return (
                <div
                  key={q.id}
                  onClick={() => setExpandedId(q.id)}
                  className="card p-5 cursor-pointer hover:border-primary-200 transition-colors"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-accent-800 text-sm leading-relaxed flex-1 line-clamp-2">
                      <LatexRenderer content={q.question_text} />
                    </p>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${status.cls}`}>
                      {status.label}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-500 font-medium">
                      {subjectNames[q.subject] || q.subject}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-500 font-medium">
                      {q.grade}-{q.grade === 11 ? 'ci' : 'cu'} sinif
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-500 font-medium">
                      {q.topic}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diff.cls}`}>
                      {diff.label}
                    </span>
                  </div>
                  <p className="text-xs text-accent-300 mt-2">Tam görmək üçün klikləyin</p>
                </div>
              )
            })}

            {questions.length === 0 && (
              <div className="card p-12 text-center">
                <p className="text-accent-400">Sual tapılmadı</p>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
              disabled={filters.page <= 1}
              className="px-4 py-2 text-sm font-medium rounded-lg border border-accent-200 text-accent-600 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
            >
              Əvvəlki
            </button>
            <span className="px-4 py-2 text-sm text-accent-500">
              {filters.page} / {totalPages}
            </span>
            <button
              onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
              disabled={filters.page >= totalPages}
              className="px-4 py-2 text-sm font-medium rounded-lg border border-accent-200 text-accent-600 hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
            >
              Növbəti
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
