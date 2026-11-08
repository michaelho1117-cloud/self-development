/**
 * Smoke: process ../01_concepts/*.md (+ a KaTeX fixture) through the same
 * remark-gfm / remark-math / rehype-katex stack used by MarkdownPreview.
 */
import { readFileSync, readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
const __dirname = dirname(fileURLToPath(import.meta.url))
const uiRoot = join(__dirname, '..')
const conceptsDir = join(uiRoot, '..', '01_concepts')

// Mirror MarkdownPreview's remark/rehype stack (SSR without Vite).
const { default: ReactMarkdown } = await import('react-markdown')
const { default: remarkGfm } = await import('remark-gfm')
const { default: remarkMath } = await import('remark-math')
const { default: rehypeKatex } = await import('rehype-katex')

function renderMd(source) {
  return renderToStaticMarkup(
    createElement(
      ReactMarkdown,
      {
        remarkPlugins: [remarkGfm, remarkMath],
        rehypePlugins: [rehypeKatex],
      },
      source,
    ),
  )
}

const files = readdirSync(conceptsDir)
  .filter((name) => name.endsWith('.md'))
  .sort()

if (files.length === 0) {
  console.error('No concept markdown files under', conceptsDir)
  process.exit(1)
}

let failed = 0

for (const name of files) {
  const path = join(conceptsDir, name)
  const source = readFileSync(path, 'utf8')
  try {
    const html = renderMd(source)
    const hasHeading = /<h[1-3][\s>]/.test(html)
    const hasTable = html.includes('<table') || !source.includes('|---')
    if (!hasHeading) {
      throw new Error('expected at least one heading in rendered HTML')
    }
    if (!hasTable) {
      throw new Error('GFM table did not render')
    }
    console.log(`ok  ${name}  (${html.length} chars html)`)
  } catch (err) {
    failed += 1
    console.error(`FAIL ${name}:`, err instanceof Error ? err.message : err)
  }
}

const katexFixture = [
  '# KaTeX smoke',
  '',
  'Inline $O(n \\log n)$ and display:',
  '',
  '$$',
  '\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}',
  '$$',
  '',
].join('\n')

try {
  const html = renderMd(katexFixture)
  if (!html.includes('katex') || !html.includes('frac')) {
    throw new Error('KaTeX output missing expected markers')
  }
  console.log(`ok  [katex-fixture]  (${html.length} chars html)`)
} catch (err) {
  failed += 1
  console.error('FAIL [katex-fixture]:', err instanceof Error ? err.message : err)
}

if (failed) {
  console.error(`\nSmoke failed: ${failed} case(s)`)
  process.exit(1)
}

console.log(`\nSmoke passed: ${files.length} concept file(s) + KaTeX fixture`)
