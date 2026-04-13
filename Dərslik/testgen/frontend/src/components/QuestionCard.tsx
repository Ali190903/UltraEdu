'use client'
import { Fragment, useState } from 'react'
import LatexRenderer from './LatexRenderer'
import ReportButton from './ReportButton'

interface Props {
  question: {
    question_text: string
    options: Record<string, string> | null
    matching_pairs: Record<string, string> | null
    correct_answer: string
    explanation: string
    latex_content: string | null
    source_reference: string
    bloom_level?: string
    difficulty?: string
  }
  questionId?: string
  index?: number
}

export default function QuestionCard({ question, questionId, index }: Props) {
  const [showAnswer, setShowAnswer] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)

  const isCorrect = selected === question.correct_answer

  const renderText = (text: string) =>
    text.includes('$') ? <LatexRenderer content={text} /> : <span>{text}</span>

  return (
    <div className="card p-6 space-y-4">
      {/* Header badges */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {index !== undefined && (
            <span className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-bold flex items-center justify-center">
              {index + 1}
            </span>
          )}
          {question.bloom_level && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 text-accent-500 font-medium">
              {question.bloom_level}
            </span>
          )}
        </div>
        {question.difficulty && (
          <span
            className={`text-xs px-2.5 py-1 rounded-full font-medium ${
              question.difficulty === 'easy'
                ? 'bg-emerald-50 text-emerald-600'
                : question.difficulty === 'medium'
                  ? 'bg-amber-50 text-amber-600'
                  : 'bg-rose-50 text-rose-600'
            }`}
          >
            {question.difficulty === 'easy' ? 'Asan' : question.difficulty === 'medium' ? 'Orta' : 'Çətin'}
          </span>
        )}
      </div>

      {/* Question text */}
      <div className="text-accent-800 text-[0.9375rem] leading-relaxed font-medium">
        {renderText(question.question_text)}
      </div>

      {/* MCQ options */}
      {question.options && (
        <div className="space-y-2">
          {Object.entries(question.options).map(([key, val]) => {
            const isThisCorrect = key === question.correct_answer
            const isThisSelected = key === selected
            let classes = 'bg-white border-accent-200 hover:border-accent-300 hover:bg-accent-50'
            if (showAnswer && isThisCorrect) {
              classes = 'bg-emerald-50 border-emerald-400 ring-1 ring-emerald-200'
            } else if (showAnswer && isThisSelected && !isThisCorrect) {
              classes = 'bg-rose-50 border-rose-400 ring-1 ring-rose-200'
            } else if (isThisSelected && !showAnswer) {
              classes = 'bg-primary-50 border-primary-400'
            }

            return (
              <button
                key={key}
                onClick={() => {
                  setSelected(key)
                  setShowAnswer(true)
                }}
                className={`w-full text-left px-4 py-3 border-1.5 rounded-lg transition-all duration-200 flex items-start gap-3 cursor-pointer ${classes}`}
              >
                <span
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold shrink-0 mt-0.5 ${
                    showAnswer && isThisCorrect
                      ? 'bg-emerald-500 text-white'
                      : showAnswer && isThisSelected && !isThisCorrect
                        ? 'bg-rose-500 text-white'
                        : isThisSelected
                          ? 'bg-primary-600 text-white'
                          : 'bg-accent-100 text-accent-600'
                  }`}
                >
                  {key}
                </span>
                <span className="text-accent-700 text-[0.9375rem] pt-0.5">{renderText(val)}</span>
              </button>
            )
          })}
        </div>
      )}

      {/* Matching pairs — two-column layout */}
      {question.matching_pairs && Object.keys(question.matching_pairs).length > 0 && (
        <div className="space-y-3">
          <div className="grid grid-cols-[auto_1fr_auto_1fr] gap-x-3 gap-y-2 items-center text-[0.9375rem]">
            <div className="col-span-2 text-xs font-semibold uppercase tracking-wide text-accent-500 px-1">
              Sol sütun
            </div>
            <div className="col-span-2 text-xs font-semibold uppercase tracking-wide text-accent-500 px-1">
              Sağ sütun
            </div>
            {Object.entries(question.matching_pairs).map(([left, right], i) => (
              <Fragment key={i}>
                <span className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <div className="px-3 py-2 rounded-lg border border-accent-200 bg-white text-accent-800">
                  {renderText(left)}
                </div>
                <span className="w-7 h-7 rounded-full bg-accent-100 text-accent-500 text-xs font-bold flex items-center justify-center">
                  {String.fromCharCode(65 + i)}
                </span>
                <div
                  className={`px-3 py-2 rounded-lg border transition-all ${
                    showAnswer
                      ? 'border-emerald-300 bg-emerald-50 text-emerald-900'
                      : 'border-accent-200 bg-white text-accent-400 blur-[3px] select-none'
                  }`}
                >
                  {renderText(right)}
                </div>
              </Fragment>
            ))}
          </div>
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="btn-primary text-sm"
          >
            {showAnswer ? 'Cavabı gizlət' : 'Cavabı göstər'}
          </button>
        </div>
      )}

      {/* Open-ended: show/hide answer */}
      {!question.options && !question.matching_pairs && (
        <button
          onClick={() => setShowAnswer(!showAnswer)}
          className="btn-primary text-sm"
        >
          {showAnswer ? 'Gizlət' : 'Cavabı göstər'}
        </button>
      )}

      {/* Answer reveal */}
      {showAnswer && (
        <div className={`rounded-lg p-4 space-y-2 ${isCorrect ? 'bg-emerald-50 border border-emerald-200' : 'bg-accent-50 border border-accent-200'}`}>
          {selected && question.options && (
            <div className={`text-sm font-semibold ${isCorrect ? 'text-emerald-600' : 'text-rose-600'}`}>
              {isCorrect ? 'Dogru cavab!' : `Səhv. Dogru cavab: ${question.correct_answer}`}
            </div>
          )}
          {!question.options && (
            <p className="text-sm font-semibold text-primary-700">Cavab: {question.correct_answer}</p>
          )}
          <p className="text-accent-600 text-sm leading-relaxed">{renderText(question.explanation)}</p>
          <p className="text-accent-400 text-xs flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            {question.source_reference}
          </p>
        </div>
      )}

      {/* Report button */}
      {questionId && (
        <div className="pt-2 border-t border-accent-100">
          <ReportButton questionId={questionId} />
        </div>
      )}
    </div>
  )
}