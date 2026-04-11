interface Props {
  value: string
  onChange: (difficulty: string) => void
}

const levels = [
  {
    id: 'easy',
    label: 'Asan',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    ),
    active: 'bg-emerald-50 border-emerald-400 text-emerald-700 shadow-sm shadow-emerald-100',
  },
  {
    id: 'medium',
    label: 'Orta',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h8" />
      </svg>
    ),
    active: 'bg-amber-50 border-amber-400 text-amber-700 shadow-sm shadow-amber-100',
  },
  {
    id: 'hard',
    label: 'Çətin',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    active: 'bg-rose-50 border-rose-400 text-rose-700 shadow-sm shadow-rose-100',
  },
]

export default function DifficultyPicker({ value, onChange }: Props) {
  return (
    <div className="flex gap-2">
      {levels.map((level) => (
        <button
          key={level.id}
          type="button"
          onClick={() => onChange(level.id)}
          className={`flex items-center gap-1.5 px-4 py-2 border-1.5 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
            value === level.id
              ? level.active
              : 'bg-white border-accent-200 text-accent-400 hover:border-accent-300 hover:text-accent-500'
          }`}
        >
          {level.icon}
          {level.label}
        </button>
      ))}
    </div>
  )
}