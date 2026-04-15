'use client'
import { useState } from 'react'
import { api } from '@/lib/api'
import QuestionCard from './QuestionCard'

const subjects = [
  { id: 'az_dili', name: 'Azərbaycan dili' },
  { id: 'riyaziyyat', name: 'Riyaziyyat' },
  { id: 'ingilis', name: 'İngilis dili' },
]

export default function VariantBuilder() {
  const [form, setForm] = useState({
    title: '',
    subject: 'riyaziyyat',
    grades: new Set<number>([11]),
    easy: 10,
    medium: 10,
    hard: 5,
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const total = form.easy + form.medium + form.hard

  const submit = async () => {
    setError('')
    setLoading(true)
    try {
      const res = await api.variants.generate({
        title: form.title || `Variant - ${new Date().toLocaleDateString('az')}`,
        subject: form.subject,
        grade: Array.from(form.grades),
        total_questions: total,
        difficulty_dist: { easy: form.easy, medium: form.medium, hard: form.hard },
      })
      // Fetch full variant with questions
      const full = await api.variants.get(res.id)
      setResult(full)
    } catch (err: any) {
      setError(err.message || 'Variant yaratmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card p-6 space-y-6">
      {/* Title */}
      <div>
        <label className="text-sm font-semibold text-accent-700 mb-2 block">Variant adı</label>
        <input
          type="text"
          placeholder="Məs: DIM Sınaq - Aprel 2026"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          className="input-field"
        />
      </div>

      {/* Subject & Grade */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-semibold text-accent-700 mb-2 block">Fənn</label>
          <select
            value={form.subject}
            onChange={(e) => setForm({ ...form, subject: e.target.value })}
            className="input-field bg-white cursor-pointer appearance-none"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 1rem center',
            }}
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm font-semibold text-accent-700 mb-2 block">Sinif</label>
          <div className="flex gap-2">
            {[9, 10, 11].map((g) => {
              const isActive = form.grades.has(g)
              return (
                <button
                  key={g}
                  type="button"
                  onClick={() => {
                    const next = new Set(form.grades)
                    if (next.has(g)) {
                      if (next.size > 1) next.delete(g)
                    } else {
                      next.add(g)
                    }
                    setForm({ ...form, grades: next })
                  }}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-semibold border-1.5 transition-all duration-200 cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'bg-primary-50 border-primary-400 text-primary-700'
                      : 'bg-white border-accent-200 text-accent-500 hover:border-accent-300'
                  }`}
                >
                  {g}-{g === 11 ? 'ci' : 'cu'}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Difficulty distribution */}
      <div>
        <label className="text-sm font-semibold text-accent-700 mb-3 block">Çətinlik bölgüsü</label>
        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-emerald-600 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              Asan
            </label>
            <input
              type="number"
              min={0}
              value={form.easy}
              onChange={(e) => setForm({ ...form, easy: Number(e.target.value) })}
              className="input-field text-center !py-2"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-amber-600 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              Orta
            </label>
            <input
              type="number"
              min={0}
              value={form.medium}
              onChange={(e) => setForm({ ...form, medium: Number(e.target.value) })}
              className="input-field text-center !py-2"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-rose-600 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              Çətin
            </label>
            <input
              type="number"
              min={0}
              value={form.hard}
              onChange={(e) => setForm({ ...form, hard: Number(e.target.value) })}
              className="input-field text-center !py-2"
            />
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <p className="text-xs text-accent-400">Cəmi: <span className="font-semibold text-accent-600">{total}</span> sual</p>
          {/* Visual bar */}
          <div className="flex h-1.5 w-32 rounded-full overflow-hidden bg-accent-100">
            {total > 0 && (
              <>
                <div className="bg-emerald-400" style={{ width: `${(form.easy / total) * 100}%` }} />
                <div className="bg-amber-400" style={{ width: `${(form.medium / total) * 100}%` }} />
                <div className="bg-rose-400" style={{ width: `${(form.hard / total) * 100}%` }} />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-600 text-sm">
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={submit}
        disabled={loading || total === 0}
        className="btn-primary w-full py-3.5 text-center flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Yaradılır... (bu bir neçə dəqiqə çəkə bilər)
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
            Variant Yarat
          </>
        )}
      </button>

      {/* Success result */}
      {result && (
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-700 font-semibold">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Variant uğurla yaradıldı!
              </div>
              <span className="text-sm text-accent-500">
                {result.questions?.length || 0} sual yaradıldı
              </span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <button
                onClick={() => api.variants.export(result.variant?.id || result.id, 'pdf')}
                className="text-xs px-3 py-1.5 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition-colors cursor-pointer"
              >
                PDF yüklə
              </button>
              <button
                onClick={() => api.variants.export(result.variant?.id || result.id, 'word')}
                className="text-xs px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-700 transition-colors cursor-pointer"
              >
                Word yüklə
              </button>
            </div>
          </div>

          {/* Show generated questions */}
          {result.questions?.map((item: any, idx: number) => (
            <QuestionCard
              key={item.question?.id || idx}
              question={{
                question_type: item.question?.question_type,
                question_text: item.question?.question_text || '',
                options: item.question?.options || null,
                matching_pairs: null,
                rubric: item.question?.rubric || null,
                correct_answer: item.question?.correct_answer || '',
                explanation: item.question?.explanation || '',
                latex_content: item.question?.latex_content || null,
                source_reference: item.question?.source_reference || '',
                bloom_level: item.question?.bloom_level,
                difficulty: item.question?.difficulty,
              }}
              questionId={item.question?.id}
              index={idx}
            />
          ))}
        </div>
      )}
    </div>
  )
}