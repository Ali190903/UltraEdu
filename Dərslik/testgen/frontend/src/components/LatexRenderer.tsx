'use client'
import { useMemo } from 'react'
import katex from 'katex'

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderLatex(content: string): string {
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
          return escapeHtml(part)
        }
      }
      if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
        try {
          return katex.renderToString(part.slice(1, -1), {
            throwOnError: false,
            displayMode: false,
          })
        } catch {
          return escapeHtml(part)
        }
      }
      return escapeHtml(part).replace(/\\n|\n/g, '<br />')
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
