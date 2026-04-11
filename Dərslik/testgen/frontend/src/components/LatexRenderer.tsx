'use client'
import { useMemo } from 'react'
import katex from 'katex'

function renderLatex(content: string): string {
  // Split by $$...$$ (display) and $...$ (inline), preserving delimiters
  const parts = content.split(/(\$\$[\s\S]+?\$\$|\$[^$]+?\$)/g)
  return parts
    .map((part) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        try {
          return katex.renderToString(part.slice(2, -2), {
            throwOnError: false,
            displayMode: true,
          })
        } catch {
          return part
        }
      }
      if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
        try {
          return katex.renderToString(part.slice(1, -1), {
            throwOnError: false,
            displayMode: false,
          })
        } catch {
          return part
        }
      }
      return part
    })
    .join('')
}

export default function LatexRenderer({ content }: { content: string }) {
  const html = useMemo(() => {
    if (!content) return ''
    return renderLatex(content)
  }, [content])

  return <span dangerouslySetInnerHTML={{ __html: html }} />
}
