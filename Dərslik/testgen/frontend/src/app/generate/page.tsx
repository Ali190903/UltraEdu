'use client'
import { useState } from 'react'
import TopicSelector from '@/components/TopicSelector'
import DifficultyPicker from '@/components/DifficultyPicker'
import QuestionCard from '@/components/QuestionCard'
import { api } from '@/lib/api'
import type { GenerateResponse } from '@/lib/types'

const subjects = [
  {
    id: 'az_dili',
    name: 'Azərbaycan dili',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    id: 'riyaziyyat',
    name: 'Riyaziyyat',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.745 3A23.933 23.933 0 003 12c0 3.183.62 6.22 1.745 9M19.5 3c.967 2.78 1.5 5.817 1.5 9s-.533 6.22-1.5 9M8.25 8.885l1.444-.89a.75.75 0 011.105.402l2.402 7.206a.75.75 0 001.105.401l1.444-.889" />
      </svg>
    ),
  },
  {
    id: 'ingilis',
    name: 'İngilis dili',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802" />
      </svg>
    ),
  },
]

const questionTypes = [
  { id: 'mcq', name: 'Test (5 variant)', desc: 'Çoxseçimli suallar' },
  { id: 'matching', name: 'Uyğunlaşma', desc: 'Cütləşdirmə tapşırıqları' },
  { id: 'open_ended', name: 'Açıq sual', desc: 'Ətraflı cavab tələb edən' },
]

export default function GeneratePage() {
  const [subject, setSubject] = useState('az_dili')
  const [grade, setGrade] = useState(9)
  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState('medium')
  const [questionType, setQuestionType] = useState('mcq')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<GenerateResponse[]>([])
  const [error, setError] = useState('')

  const generate = async () => {
    if (!topic) {
      setError('Zəhmət olmasa mövzu seçin')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await api.questions.generate({
        subject,
        grade,
        topic,
        difficulty,
        question_type: questionType,
      })
      setResults((prev) => [res, ...prev])
    } catch (err: any) {
      setError(err.message || 'Sual yaratmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-accent-50 pb-12">
      {/* Page header (Seamless) */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-8 pb-6">
        <h1 className="text-2xl font-extrabold text-accent-900 tracking-tight">Sual Generasiyası</h1>
        <p className="text-sm text-accent-500 mt-1.5">Fənni, sinifi və mövzunu seçin — AI sizin üçün unikal sual yaratsın</p>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Form panel */}
          <div className="lg:col-span-1">
            <div className="card p-5 md:p-6 space-y-5 sticky top-6 shadow-sm border-accent-100/60">
              {/* Subject selector */}
              <div>
                <label className="text-xs font-semibold tracking-wide text-accent-700 uppercase mb-2 block">Fənn</label>
                <div className="space-y-2">
                  {subjects.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => {
                         if (!loading) { setSubject(s.id); setTopic('') }
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl border border-transparent transition-all duration-300 cursor-pointer text-left ${
                        subject === s.id
                          ? 'bg-primary-50 border-primary-200 text-primary-800 shadow-sm'
                          : 'bg-white border-accent-200 text-accent-600 hover:border-primary-300'
                      }`}
                    >
                      <span
                        className={`p-1.5 rounded-lg transition-colors ${
                          subject === s.id ? 'bg-primary-100 text-primary-600' : 'bg-accent-100 text-accent-400'
                        }`}
                      >
                        <div className="scale-75">{s.icon}</div>
                      </span>
                      <span className="font-semibold text-sm">{s.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Grade selector */}
              <div>
                <label className="text-xs font-semibold tracking-wide text-accent-700 uppercase mb-2 block">Sinif</label>
                <div className="flex gap-2">
                  {[9, 10, 11].map((g) => (
                    <button
                      key={g}
                      onClick={() => {
                        if (!loading) { setGrade(g); setTopic('') }
                      }}
                      className={`flex-1 py-1.5 px-2 rounded-lg text-sm font-bold border transition-all duration-300 cursor-pointer ${
                        grade === g
                          ? 'bg-primary-50 border-primary-300 text-primary-700'
                          : 'bg-white border-accent-200 text-accent-500 hover:border-primary-300'
                      }`}
                    >
                      {g}-cu
                    </button>
                  ))}
                </div>
              </div>

              {/* Topic selector */}
              <div>
                <label className="text-xs font-semibold tracking-wide text-accent-700 uppercase mb-2 block">Mövzu</label>
                <TopicSelector subject={subject} grade={grade} value={topic} onChange={setTopic} />
              </div>

              {/* Difficulty */}
              <div>
                <label className="text-xs font-semibold tracking-wide text-accent-700 uppercase mb-2 block">Çətinlik</label>
                <DifficultyPicker value={difficulty} onChange={setDifficulty} />
              </div>

              {/* Question type */}
              <div>
                <label className="text-xs font-semibold tracking-wide text-accent-700 uppercase mb-2 block">Sual növü</label>
                <div className="space-y-1.5">
                  {questionTypes.map((qt) => (
                    <button
                      key={qt.id}
                      onClick={() => setQuestionType(qt.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                        questionType === qt.id
                          ? 'bg-primary-50 border-primary-300'
                          : 'bg-white border-accent-200 hover:border-accent-300'
                      }`}
                    >
                      <span
                        className={`text-sm font-medium ${questionType === qt.id ? 'text-primary-700' : 'text-accent-600'}`}
                      >
                        {qt.name}
                      </span>
                      <span className="text-[11px] text-accent-400 block">{qt.desc}</span>
                    </button>
                  ))}
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

              {/* Generate button */}
              <button
                onClick={generate}
                disabled={loading}
                className="btn-primary w-full py-2.5 text-sm text-center flex items-center justify-center gap-2 cursor-pointer mt-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Yaradılır...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                    </svg>
                    Sual Yarat
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right: Results panel */}
          <div className="lg:col-span-2">
            {results.length === 0 && !loading && (
              <div className="card p-12 text-center">
                <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-accent-700 mb-1">Sual yaratmağa hazırsınız</h3>
                <p className="text-accent-400 text-sm">Soldakı formdan parametrləri seçin və &quot;Sual Yarat&quot; düyməsinə basın</p>
              </div>
            )}

            {loading && (
              <div className="card p-12 text-center mb-6">
                <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-4">
                  <svg className="animate-spin h-8 w-8 text-primary-500" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-accent-700 mb-1">Sual yaradılır...</h3>
                <p className="text-accent-400 text-sm">RAG sistemi dərsliyə əsaslanan sual hazırlayır</p>
              </div>
            )}

            {results.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-accent-800">
                    Yaradılmış suallar
                    <span className="text-accent-400 font-normal text-sm ml-2">({results.length})</span>
                  </h2>
                  {results.length > 1 && (
                    <button
                      onClick={() => setResults([])}
                      className="text-sm text-accent-400 hover:text-accent-600 transition-colors cursor-pointer"
                    >
                      Hamısını təmizlə
                    </button>
                  )}
                </div>

                {results.map((res, i) => (
                  <div key={i}>
                    <QuestionCard
                      question={res.question}
                      questionId={res.question_id}
                      index={i}
                    />
                    <div className="flex justify-end mt-1.5 gap-3 text-xs text-accent-400">
                      <span>{res.attempts} cəhd</span>
                      <span>{res.timing.total.toFixed(1)}s</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}