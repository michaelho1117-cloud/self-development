import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

type Props = {
  source: string
  emptyHint?: string
}

export function MarkdownPreview({
  source,
  emptyHint = 'Nothing to preview yet.',
}: Props) {
  const trimmed = source.trim()
  if (!trimmed) {
    return (
      <p className="px-4 py-3 text-sm text-[var(--text-muted)]">{emptyHint}</p>
    )
  }

  return (
    <div className="md-preview min-h-0 flex-1 overflow-auto px-4 py-3">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
      >
        {source}
      </ReactMarkdown>
    </div>
  )
}
