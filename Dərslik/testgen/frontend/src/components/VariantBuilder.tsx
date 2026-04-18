'use client'
import { useState } from 'react'
import { api } from '@/lib/api'
import QuestionCard from './QuestionCard'

const subjects: { id: string; name: string; disabled?: boolean }[] = [
  { id: 'riyaziyyat', name: 'Riyaziyyat' },
  { id: 'az_dili', name: 'Azərbaycan dili' },
  { id: 'ingilis', name: 'İngilis dili' },
]

export default function VariantBuilder() {
  const [form, setForm] = useState({
    title: '',
    subject: 'riyaziyyat',
    grades: new Set<number>([11]),
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  // Hardcode 25 for DIM standards (13 MCQ, 5 numeric, 7 open-ended handled by backend)
  const total = 25;
  const dimDifficulty = { easy: 10, medium: 10, hard: 5 };

  const submit = async () => {
    setError('')
    setLoading(true)
    try {
      const res = await api.variants.generate({
        title: form.title || `DİM Sınaq - ${new Date().toLocaleDateString('az')}`,
        subject: form.subject,
        grade: Array.from(form.grades),
        total_questions: total,
        difficulty_dist: dimDifficulty,
      })
      const full = await api.variants.get(res.id)
      setResult(full)
    } catch (err: any) {
      setError(err.message || 'Variant yaratmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header section with glassmorphism */}
      <div className="glass rounded-2xl p-8 border border-white/40 shadow-xs relative overflow-hidden">
        
        <div className="relative z-10 max-w-2xl">
          <h2 className="text-2xl font-bold tracking-tight text-accent-900 mb-2">Yeni İmtahan Variantı</h2>
          <p className="text-accent-500 text-sm leading-relaxed mb-8">
            DİM standartlarına cavab verən (13 qapalı, 5 kodlaşdırılan, 7 yazılı tələbli) sınaqları avtomatik generasiya edin.
          </p>

          <div className="space-y-6">
            {/* Title */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-accent-500 mb-2 block">Variant Təyinatı</label>
              <input
                type="text"
                placeholder="Məsələn: DİM Aprel Sınağı - Riyaziyyat 11"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full bg-white/70 backdrop-blur-sm border border-accent-200 text-accent-900 text-sm rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 block px-4 py-3 placeholder:text-accent-400 transition-all shadow-sm"
              />
            </div>

            {/* Subject & Grade grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-accent-500 mb-2 block">Fənn / Təmayül</label>
                <select
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  className="w-full bg-white/70 backdrop-blur-sm border border-accent-200 text-accent-900 text-sm rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 block px-4 py-3 appearance-none cursor-pointer shadow-sm transition-all"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'right 1rem center',
                  }}
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id} disabled={s.disabled} className={s.disabled ? "text-accent-300" : ""}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-accent-500 mb-2 block">Sinif (Kurikulum)</label>
                <div className="flex bg-white/50 backdrop-blur-sm p-1 rounded-xl border border-accent-200 shadow-sm">
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
                        className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                          isActive
                            ? 'bg-white shadow-sm text-emerald-700 ring-1 ring-accent-200/50'
                            : 'text-accent-500 hover:text-accent-700 hover:bg-white/40'
                        }`}
                      >
                        {g}-ci
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* DİM Badge Info */}
            <div className="bg-emerald-50/50 border border-emerald-100/50 rounded-xl p-4 flex items-start gap-4">
              <div className="bg-emerald-100/50 p-2 rounded-lg shrink-0 mt-0.5">
                <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div>
                <h4 className="text-sm font-bold text-emerald-900 leading-none mb-1.5">DİM 25 Tədris Modeli aktivdir</h4>
                <p className="text-xs text-emerald-700/80 leading-relaxed font-medium">Avtomatik olaraq riyaziyyat fənni üzrə 6 əsas konseptual blok (Cəbr, Həndəsə, Funksiyalar, Limit və s.) və çətinlik bölgüsü əsasında tam konfiqurasiya edilmiş 25 tapşırıq yaradılacaq.</p>
              </div>
            </div>

            {/* Submit button */}
            <button
              onClick={submit}
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-600/20 py-3.5 px-6 rounded-xl text-sm font-bold tracking-wide transition-all duration-200 hover:-translate-y-0.5 disabled:opacity-70 disabled:hover:translate-y-0 disabled:shadow-none flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Baza yoxlanılır və generasiya edilir...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                  </svg>
                  Təsdiqlə və Yarat
                </>
              )}
            </button>
            
            {error && (
              <div className="flex items-center gap-2 p-3 mt-4 rounded-lg bg-rose-50/80 border border-rose-200 text-rose-600 text-sm font-medium">
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Success result section styled properly */}
      {result && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 bg-white rounded-2xl border border-accent-200 shadow-sm">
            <div>
              <h3 className="text-lg font-bold text-accent-900">{result.variant?.title || result.title}</h3>
              <p className="text-sm text-accent-500 mt-1">{result.questions?.length || 0} sual tapıldı</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => api.variants.export(result.variant?.id || result.id, 'pdf')}
                className="flex items-center gap-2 px-4 py-2 bg-accent-50 hover:bg-accent-100 text-accent-700 text-sm font-semibold rounded-xl border border-accent-200 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                PDF Yüklə
              </button>
              <button
                onClick={() => api.variants.export(result.variant?.id || result.id, 'word')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 text-sm font-semibold rounded-xl border border-blue-200 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                Word Yüklə
              </button>
            </div>
          </div>

          <div className="space-y-6">
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
                  image_svg: item.question?.image_svg || null,
                  source_reference: item.question?.source_reference || '',
                  bloom_level: item.question?.bloom_level,
                  difficulty: item.question?.difficulty,
                }}
                questionId={item.question?.id}
                index={idx}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}