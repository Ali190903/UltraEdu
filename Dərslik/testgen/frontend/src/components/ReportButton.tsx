'use client'
import { useState } from 'react'
import { api } from '@/lib/api'

interface Props {
  questionId: string
}

const reportTypes = [
  { value: 'wrong_answer', label: 'Səhv cavab' },
  { value: 'unclear', label: 'Aydın deyil' },
  { value: 'off_topic', label: 'Mövzuya uyğun deyil' },
  { value: 'grammar', label: 'Qrammatik səhv' },
  { value: 'other', label: 'Digər' },
]

export default function ReportButton({ questionId }: Props) {
  const [open, setOpen] = useState(false)
  const [type, setType] = useState('wrong_answer')
  const [comment, setComment] = useState('')
  const [sent, setSent] = useState(false)
  const [sending, setSending] = useState(false)

  const submit = async () => {
    setSending(true)
    try {
      await api.reports.create({
        question_id: questionId,
        report_type: type,
        comment: comment || undefined,
      })
      setSent(true)
      setOpen(false)
    } finally {
      setSending(false)
    }
  }

  if (sent) {
    return (
      <span className="inline-flex items-center gap-1 text-sm text-primary-600 font-medium">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        Göndərildi
      </span>
    )
  }

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1 text-sm text-accent-400 hover:text-rose-500 transition-colors cursor-pointer"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
        </svg>
        Xəta bildir
      </button>

      {open && (
        <div className="mt-3 p-4 rounded-lg bg-accent-50 border border-accent-200 space-y-3 animate-in">
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="input-field text-sm bg-white"
          >
            {reportTypes.map((rt) => (
              <option key={rt.value} value={rt.value}>
                {rt.label}
              </option>
            ))}
          </select>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Əlavə şərh (istəyə bağlı)"
            className="input-field text-sm resize-none"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              onClick={submit}
              disabled={sending}
              className="px-4 py-2 bg-rose-500 text-white text-sm font-medium rounded-lg hover:bg-rose-600 transition-colors disabled:opacity-50 cursor-pointer"
            >
              {sending ? 'Göndərilir...' : 'Göndər'}
            </button>
            <button
              onClick={() => setOpen(false)}
              className="px-4 py-2 text-sm text-accent-500 hover:text-accent-700 transition-colors cursor-pointer"
            >
              Ləğv et
            </button>
          </div>
        </div>
      )}
    </div>
  )
}