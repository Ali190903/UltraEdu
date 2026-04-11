'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { TopicInfo } from '@/lib/types'

interface Props {
  subject: string
  grade: number
  value: string
  onChange: (topic: string) => void
}

export default function TopicSelector({ subject, grade, value, onChange }: Props) {
  const [topics, setTopics] = useState<TopicInfo[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!subject || !grade) return
    setLoading(true)
    api.subjects
      .topics(subject, grade)
      .then(setTopics)
      .catch(() => setTopics([]))
      .finally(() => setLoading(false))
  }, [subject, grade])

  if (loading) {
    return (
      <div className="input-field flex items-center gap-2 text-accent-400 bg-accent-50">
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Mövzular yüklənir...
      </div>
    )
  }

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="input-field bg-white cursor-pointer appearance-none"
      style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center' }}
    >
      <option value="">Mövzu seçin</option>
      {topics.map((t, i) => (
        <option key={i} value={t.topic}>
          {t.chapter} — {t.topic}
        </option>
      ))}
    </select>
  )
}