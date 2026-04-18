'use client'
import { Fragment, useState } from 'react'
import LatexRenderer from './LatexRenderer'
import ReportButton from './ReportButton'

interface Props {
  question: {
    question_type?: 'mcq' | 'matching' | 'open_ended' | 'numeric_open' | 'written_solution'
    question_text: string
    options: Record<string, string> | null
    matching_pairs: Record<string, string> | null
    rubric?: Record<string, string> | null
    correct_answer: string
    explanation: string
    latex_content: string | null
    image_svg?: string | null
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
  const [matchingSelection, setMatchingSelection] = useState<Record<string, string[]>>({})
  const [pairsSelection, setPairsSelection] = useState<Record<string, string>>({})

  const isMatching = question.question_type === 'matching' || (question.options && question.correct_answer?.includes('1-'));

  const matchingRows = isMatching
    ? Array.from(new Set((question.correct_answer || '').split(';').map(p => p.trim().split('-')[0]).filter(Boolean)))
    : [];

  const checkMatching = () => {
    const userStr = matchingRows
      .map(r => {
        const sel = matchingSelection[r] || [];
        return sel.length > 0 ? `${r}-${sel.join(',')}` : null;
      })
      .filter(Boolean)
      .join('; ');
    
    const norm = (s: string) => s.replace(/\s/g, '').toLowerCase();
    return norm(userStr) === norm(question.correct_answer);
  };

  const isCorrect = isMatching ? checkMatching() : selected === question.correct_answer

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

      {/* Embedded Geometry/SVG Model */}
      {question.image_svg && (
        <div
          className="my-5 flex justify-center p-4 bg-white border border-accent-200 rounded-xl shadow-sm"
          dangerouslySetInnerHTML={{ __html: question.image_svg.replace(/\$([^$]+)\$/g, '$1') }}
        />
      )}

      {/* MCQ options / Matching Matrix */}
      {question.options && !isMatching && (
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

      {/* Matching Matrix UI */}
      {question.options && isMatching && (
        <div className="space-y-6 bg-accent-50/50 p-4 rounded-xl border border-accent-100">
          <div className="space-y-3 pl-2">
            {Object.entries(question.options).map(([key, val]) => (
              <div key={key} className="flex items-start gap-3 text-[0.9375rem]">
                <span className="font-bold text-accent-500 uppercase shrink-0 pt-0.5 w-5 text-right">{key})</span>
                <span className="text-accent-800">{renderText(val)}</span>
              </div>
            ))}
          </div>

          <div className="space-y-3 pt-3 border-t border-accent-200">
            <p className="text-xs font-semibold uppercase tracking-wide text-accent-500 mb-2">Variantları təyin edin:</p>
            {matchingRows.map((row) => (
              <div key={row} className="flex items-center gap-4 bg-white p-3 rounded-lg border border-accent-200 shadow-sm">
                <span className="w-8 h-8 flex items-center justify-center font-bold text-lg text-primary-700 bg-primary-50 rounded-full shrink-0">
                  {row}
                </span>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(question.options || {}).map(opt => {
                    const isSelected = (matchingSelection[row] || []).includes(opt);
                    // Determine if correct in showAnswer layout
                    const correctAnswerParts = question.correct_answer.split(';').map(p => p.trim());
                    const matchedPart = correctAnswerParts.find(p => p.startsWith(`${row}-`));
                    const correctAnswersForRow = matchedPart ? matchedPart.split('-')[1].split(',') : [];
                    const isCorrectForThisOpt = correctAnswersForRow.includes(opt);

                    let btnClass = 'bg-accent-50 border-accent-200 text-accent-600 hover:bg-accent-100';
                    if (showAnswer) {
                      if (isCorrectForThisOpt) btnClass = 'bg-emerald-500 text-white border-emerald-600';
                      else if (isSelected && !isCorrectForThisOpt) btnClass = 'bg-rose-500 text-white border-rose-600';
                      else btnClass = 'bg-accent-50 text-accent-300 border-accent-100 opacity-50';
                    } else if (isSelected) {
                      btnClass = 'bg-primary-600 text-white border-primary-700 shadow-inner';
                    }

                    return (
                      <button
                        key={opt}
                        onClick={() => {
                          if (showAnswer) return;
                          setMatchingSelection(prev => {
                            const current = prev[row] || [];
                            const updated = current.includes(opt) 
                              ? current.filter(c => c !== opt) 
                              : [...current, opt].sort();
                            return { ...prev, [row]: updated };
                          });
                        }}
                        className={`w-9 h-9 rounded transition-all font-bold uppercase text-sm border ${btnClass} ${showAnswer ? 'cursor-default' : 'cursor-pointer'}`}
                      >
                        {opt}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>

          {!showAnswer && (
            <div className="pt-2 flex justify-end">
              <button
                disabled={Object.values(matchingSelection).every(arr => arr.length === 0)}
                onClick={() => setShowAnswer(true)}
                className="btn-primary text-sm px-6 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cavabı Yoxla
              </button>
            </div>
          )}
        </div>
      )}

      {/* Matching pairs — interactive two-column layout */}
      {question.matching_pairs && Object.keys(question.matching_pairs).length > 0 && (
        (() => {
          // Stable shuffle logic could be needed if we want identical renders, 
          // but for a simple card we can derive a list of keys and options.
          const entries = Object.entries(question.matching_pairs);
          // Get unique Right options, sorted just to keep it deterministic
          const rightOptions = Array.from(new Set(entries.map(e => e[1]))).sort();
          
          let allCorrect = true;
          let anySelected = false;
          entries.forEach(([left, correctRight]) => {
            const userSelectedRightIdx = pairsSelection[left];
            if (userSelectedRightIdx) anySelected = true;
            if (!userSelectedRightIdx || rightOptions[parseInt(userSelectedRightIdx)] !== correctRight) {
              allCorrect = false;
            }
          });

          return (
            <div className="space-y-4">
              <div className="bg-accent-50/50 p-4 rounded-xl border border-accent-100 flex flex-col md:flex-row gap-6">
                
                {/* Left Column - Questions */}
                <div className="flex-1 space-y-3">
                  <div className="text-xs font-semibold uppercase tracking-wide text-accent-500 mb-4 px-1">
                    Sol sütun
                  </div>
                  {entries.map(([left], i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-bold flex items-center justify-center shrink-0">
                        {i + 1}
                      </span>
                      <div className="flex-1 px-3 py-2 rounded-lg border border-accent-200 bg-white text-accent-800 text-[0.9375rem] shadow-sm">
                        {renderText(left)}
                      </div>
                      
                      {/* Selection Dropdown */}
                      <select 
                        value={pairsSelection[left] || ""}
                        onChange={(e) => {
                          if (showAnswer) return;
                          setPairsSelection(prev => ({...prev, [left]: e.target.value}));
                        }}
                        disabled={showAnswer}
                        className={`w-14 h-10 rounded-lg border text-center font-bold appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                          showAnswer 
                            ? ((rightOptions[parseInt(pairsSelection[left])] === entries[i][1]) 
                                ? 'bg-emerald-50 border-emerald-400 text-emerald-700' 
                                : 'bg-rose-50 border-rose-400 text-rose-700')
                            : 'bg-white border-accent-300 text-accent-700'
                        }`}
                      >
                        <option value="" disabled>-</option>
                        {rightOptions.map((_, optsIdx) => (
                          <option key={optsIdx} value={optsIdx}>
                            {String.fromCharCode(65 + optsIdx)}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>

                {/* Right Column - Shuffled Options */}
                <div className="flex-1 space-y-3">
                  <div className="text-xs font-semibold uppercase tracking-wide text-accent-500 mb-4 px-1">
                    Sağ sütun (Variantlar)
                  </div>
                  {rightOptions.map((rightText, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="w-8 h-8 rounded-full bg-accent-100 text-accent-600 text-sm font-bold flex items-center justify-center shrink-0">
                        {String.fromCharCode(65 + i)}
                      </span>
                      <div className="flex-1 px-3 py-2 rounded-lg border border-accent-200 bg-white text-accent-700 text-[0.9375rem] shadow-sm">
                        {renderText(rightText)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {!showAnswer && (
                <div className="flex justify-end pt-2">
                  <button
                    disabled={!anySelected}
                    onClick={() => setShowAnswer(!showAnswer)}
                    className="btn-primary text-sm px-6 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cavabı Yoxla
                  </button>
                </div>
              )}
              
              {/* If answer is shown via top level, we inject to the common result panel below */}
            </div>
          )
        })()
      )}

      {/* Open-ended: show/hide answer */}
      {!question.options && !question.matching_pairs && !isMatching && (
        <div className="pt-2">
          {question.rubric && (
            <p className="text-xs text-accent-500 mb-3 flex items-center gap-1.5">
              <svg className="w-4 h-4 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Bu tapşırıq yazılı həll tələb edir. Sərbəst həll etdikdən sonra qiymətləndirmə meyarı (rubrik) ilə yoxlayın.
            </p>
          )}
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="btn-primary text-sm"
          >
            {showAnswer ? 'Cavabı gizlət' : 'Cavabı göstər'}
          </button>
        </div>
      )}

      {/* Answer reveal */}
      {showAnswer && (
        <div className={`rounded-lg p-5 space-y-4 ${
          isCorrect || (question.matching_pairs ? true : false) 
            ? 'bg-emerald-50 border border-emerald-200' 
            : 'bg-accent-50 border border-accent-200'
        }`}>
          {((selected && question.options && !isMatching) || (isMatching)) && (
            <div className={`text-sm font-semibold ${isCorrect ? 'text-emerald-600' : 'text-rose-600'}`}>
              {isCorrect ? 'Doğru cavab!' : `Səhv. Doğru cavab: ${question.correct_answer}`}
            </div>
          )}
          
          {question.matching_pairs && (
            <div className="text-sm font-semibold text-emerald-600">
              Doğru Uyğunlaşdırma:
              <ul className="mt-2 space-y-1 font-medium text-accent-800">
                {Object.entries(question.matching_pairs).map(([left, right], i) => (
                  <li key={i}>
                    {i + 1}. {renderText(left)} &rarr; {renderText(right)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {!question.options && !question.matching_pairs && (
            <div className="bg-white p-3 rounded border border-primary-200 inline-block min-w-[120px]">
              <span className="text-xs font-semibold text-primary-500 uppercase tracking-wide block mb-1">Düzgün Cavab</span>
              <span className="text-primary-800 font-bold text-lg">{renderText(question.correct_answer)}</span>
            </div>
          )}

          {question.rubric && (
            <div className="border border-accent-200 rounded-lg overflow-hidden bg-white mt-4 shadow-sm">
              <table className="w-full text-[0.9375rem] text-left">
                <thead className="bg-accent-100 text-accent-700">
                  <tr>
                    <th className="px-4 py-2.5 font-semibold border-b border-accent-200 w-24">Bal</th>
                    <th className="px-4 py-2.5 font-semibold border-b border-accent-200">Meyar (Rubrik)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-accent-100">
                  {Object.entries(question.rubric).map(([score, criteria]) => (
                    <tr key={score} className="hover:bg-accent-50/50 transition-colors">
                      <td className="px-4 py-3 font-bold text-primary-600 align-top whitespace-nowrap bg-primary-50/30">{score}</td>
                      <td className="px-4 py-3 text-accent-800 align-top leading-relaxed">{renderText(criteria as string)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-accent-500 mb-1">İzahı / Həlli</h4>
            <p className="text-accent-700 text-[0.9375rem] leading-relaxed p-3 bg-white rounded border border-accent-100">{renderText(question.explanation)}</p>
          </div>
          
          <p className="text-accent-400 text-xs flex items-center gap-1.5 pt-1 border-t border-accent-200/60 mt-2">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Mənbə: {question.source_reference}
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