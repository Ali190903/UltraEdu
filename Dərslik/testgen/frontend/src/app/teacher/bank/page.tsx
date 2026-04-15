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

const difficultyStyles: Record<
  string,
  { label: string; badge: string; dot: string; accent: string }
> = {
  easy: {
    label: 'Asan',
    badge: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
    dot: 'bg-emerald-500',
    accent: 'bg-emerald-400',
  },
  medium: {
    label: 'Orta',
    badge: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
    dot: 'bg-amber-500',
    accent: 'bg-amber-400',
  },
  hard: {
    label: 'Çətin',
    badge: 'bg-rose-50 text-rose-700 ring-1 ring-rose-200',
    dot: 'bg-rose-500',
    accent: 'bg-rose-400',
  },
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
      {/* Compact hero matching dashboard */}
      <div className="bg-white border-b border-accent-100">
        <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-accent-900">Sual Bankı</h1>
            <p className="text-sm text-accent-500 mt-0.5">
              Yaradılmış bütün sualları idarə edin — {total} sual
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-accent-500">
            {(['easy', 'medium', 'hard'] as const).map((k) => (
              <span key={k} className="inline-flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${difficultyStyles[k].dot}`} />
                {difficultyStyles[k].label}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-6 space-y-5">
        {/* Filters */}
        <div className="card p-3 sm:p-4 flex flex-wrap items-center gap-2.5">
          <select
            value={filters.subject}
            onChange={(e) => setFilters({ ...filters, subject: e.target.value, page: 1 })}
            className="input-field !w-auto !py-2 text-sm bg-white cursor-pointer appearance-none pr-9"
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
            className="input-field !w-auto !py-2 text-sm bg-white cursor-pointer appearance-none pr-9"
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

          <span className="text-xs text-accent-400 ml-auto">{total} nəticə</span>
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

        {/* Questions grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 items-start">
            {questions.map((q, idx) => {
              const isExpanded = expandedId === q.id
              const diff =
                difficultyStyles[q.difficulty] || {
                  label: q.difficulty,
                  badge: 'bg-accent-100 text-accent-500',
                  dot: 'bg-accent-300',
                  accent: 'bg-accent-300',
                }
              const status = statusLabels[q.status] || { label: q.status, cls: 'bg-accent-100 text-accent-500' }

              if (isExpanded) {
                return (
                  <div key={q.id} className="col-span-full">
                    <button
                      onClick={() => setExpandedId(null)}
                      className="text-xs text-accent-400 hover:text-primary-600 mb-2 cursor-pointer inline-flex items-center gap-1"
                    >
                      <span aria-hidden>←</span> Bağla
                    </button>
                    <QuestionCard
                      question={{
                        question_type: q.question_type,
                        question_text: q.question_text,
                        options: q.options || null,
                        matching_pairs: null,
                        rubric: (q as any).rubric || null,
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
                  className="group relative card p-5 pl-6 cursor-pointer hover:border-primary-300 hover:shadow-md transition-all overflow-hidden"
                >
                  {/* Difficulty accent bar */}
                  <span className={`absolute left-0 top-0 bottom-0 w-1 ${diff.accent}`} aria-hidden />

                  {/* Header: difficulty badge + status */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span
                      className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-full ${diff.badge}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${diff.dot}`} />
                      {diff.label}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 ${status.cls}`}
                    >
                      {status.label}
                    </span>
                  </div>

                  {/* Question text */}
                  <p className="text-accent-800 text-sm leading-relaxed line-clamp-3 min-h-[4.5rem]">
                    <LatexRenderer content={q.question_text} />
                  </p>

                  {/* Meta row */}
                  <div className="flex flex-wrap gap-1.5 mt-4 pt-3 border-t border-accent-100">
                    <span className="text-[11px] px-2 py-0.5 rounded-md bg-primary-50 text-primary-700 font-medium">
                      {subjectNames[q.subject] || q.subject}
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded-md bg-accent-100 text-accent-600 font-medium">
                      {q.grade}-{q.grade === 11 ? 'ci' : 'cu'} sinif
                    </span>
                    <span
                      className="text-[11px] px-2 py-0.5 rounded-md bg-accent-100 text-accent-600 font-medium truncate max-w-[16rem]"
                      title={q.topic}
                    >
                      {q.topic}
                    </span>
                  </div>

                  <p className="text-[11px] text-accent-400 mt-3 flex items-center gap-1 group-hover:text-primary-600 transition-colors">
                    Tam görmək üçün klikləyin
                    <span aria-hidden className="transition-transform group-hover:translate-x-0.5">→</span>
                  </p>
                </div>
              )
            })}

            {questions.length === 0 && (
              <div className="card p-12 text-center col-span-full">
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
