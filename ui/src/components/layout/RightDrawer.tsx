import { useEffect, useState } from 'react'
import { putFile, runLab, type LabRuntime, type LabRunResult } from '../../lib/api'
import { useWorkbench } from '../../stores/workbench'
import { MarkdownPreview } from '../MarkdownPreview'

type FeynmanView = 'edit' | 'preview'

function isUnderLabs(path: string | null): boolean {
  if (!path) return false
  const norm = path.replace(/\\/g, '/')
  return norm === '02_labs' || norm.startsWith('02_labs/')
}

function inferRuntime(path: string | null): LabRuntime {
  if (!path) return 'py'
  const lower = path.replace(/\\/g, '/').toLowerCase()
  if (/\.(js|mjs|cjs)$/.test(lower)) return 'node'
  return 'py'
}

function isRunnableLab(path: string | null): boolean {
  if (!isUnderLabs(path) || !path) return false
  const lower = path.replace(/\\/g, '/').toLowerCase()
  return /\.(py|js|mjs|cjs)$/.test(lower)
}

export function RightDrawer() {
  const tab = useWorkbench((s) => s.drawerTab)
  const setDrawerTab = useWorkbench((s) => s.setDrawerTab)
  const currentPath = useWorkbench((s) => s.currentPath)
  const fileContent = useWorkbench((s) => s.fileContent)
  const setFileContent = useWorkbench((s) => s.setFileContent)
  const fileDirty = useWorkbench((s) => s.fileDirty)
  const setPath = useWorkbench((s) => s.setPath)

  const [feynmanView, setFeynmanView] = useState<FeynmanView>('edit')
  const [runtime, setRuntime] = useState<LabRuntime>('py')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<LabRunResult | null>(null)
  const [runError, setRunError] = useState<string | null>(null)

  const underLabs = isUnderLabs(currentPath)
  const canRun = isRunnableLab(currentPath)

  useEffect(() => {
    setRuntime(inferRuntime(currentPath))
    setResult(null)
    setRunError(null)
  }, [currentPath])

  async function save() {
    if (!currentPath) return
    const saved = await putFile(currentPath, fileContent)
    setFileContent(saved.content, false)
  }

  async function onRun() {
    if (!currentPath || !canRun) return
    setRunning(true)
    setRunError(null)
    try {
      const out = await runLab(currentPath, runtime)
      setResult(out)
    } catch (err) {
      setResult(null)
      setRunError(err instanceof Error ? err.message : String(err))
    } finally {
      setRunning(false)
    }
  }

  return (
    <aside className="flex h-full flex-col bg-[var(--bg-panel)]">
      <div className="flex border-b border-[var(--border)]">
        {(
          [
            ['feynman', 'Feynman'],
            ['lab', 'Lab'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setDrawerTab(id)}
            className={`flex-1 px-3 py-2 text-sm ${
              tab === id
                ? 'border-b-2 border-[var(--accent)] text-[var(--text)]'
                : 'text-[var(--text-muted)]'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'feynman' ? (
        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex items-center justify-between gap-2 border-b border-[var(--border)] px-3 py-2">
            <span className="min-w-0 truncate text-xs text-[var(--text-muted)]">
              {currentPath ?? 'Open a file from the left tree'}
              {fileDirty ? ' · unsaved' : ''}
            </span>
            <div className="flex shrink-0 items-center gap-1.5">
              <div
                className="flex rounded border border-[var(--border)] p-0.5"
                role="group"
                aria-label="Feynman view"
              >
                {(
                  [
                    ['edit', 'Edit'],
                    ['preview', 'Preview'],
                  ] as const
                ).map(([id, label]) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setFeynmanView(id)}
                    className={`rounded px-2 py-0.5 text-xs ${
                      feynmanView === id
                        ? 'bg-[var(--accent-soft)] text-[var(--text)]'
                        : 'text-[var(--text-muted)] hover:text-[var(--text)]'
                    }`}
                    aria-pressed={feynmanView === id}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <button
                type="button"
                disabled={!currentPath || !fileDirty}
                onClick={() => void save().catch(console.error)}
                className="rounded bg-[var(--accent)] px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
              >
                Save
              </button>
            </div>
          </div>

          {feynmanView === 'edit' ? (
            <textarea
              className="min-h-0 flex-1 resize-none bg-[var(--bg)] px-3 py-2 font-mono text-xs leading-relaxed outline-none"
              value={fileContent}
              placeholder="Markdown / concept card content…"
              onChange={(e) => {
                setFileContent(e.target.value, true)
                if (!currentPath) setPath(null)
              }}
              disabled={!currentPath}
              spellCheck={false}
            />
          ) : (
            <MarkdownPreview
              source={fileContent}
              emptyHint={
                currentPath
                  ? 'File is empty — switch to Edit to write Markdown / LaTeX.'
                  : 'Open a concept card from the left tree, then Preview.'
              }
            />
          )}

          <p className="border-t border-[var(--border)] px-3 py-2 text-[11px] text-[var(--text-muted)]">
            Preview uses remark-gfm + remark-math / rehype-katex. Inline{' '}
            <code>$…$</code>, display <code>$$…$$</code>. Save via{' '}
            <code>PUT /fs/file</code>.
          </p>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col gap-3 p-3 text-sm">
          <div className="space-y-1">
            <p className="truncate text-xs text-[var(--text-muted)]">
              {currentPath ?? 'Open a lab file under 02_labs/'}
            </p>
            {!underLabs && currentPath ? (
              <p className="text-xs text-[var(--text-muted)]">
                Run is limited to files under <code>02_labs/</code>.
              </p>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <label className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
              Runtime
              <select
                value={runtime}
                onChange={(e) => setRuntime(e.target.value as LabRuntime)}
                disabled={!canRun || running}
                className="rounded border border-[var(--border)] bg-[var(--bg)] px-2 py-1 text-xs text-[var(--text)]"
              >
                <option value="py">py</option>
                <option value="node">node</option>
              </select>
            </label>
            <button
              type="button"
              disabled={!canRun || running}
              onClick={() => void onRun()}
              className="rounded bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              title={
                canRun
                  ? 'POST /labs/run'
                  : 'Open a .py / .js lab under 02_labs/'
              }
            >
              {running ? 'Running…' : 'Run'}
            </button>
          </div>

          {runError ? (
            <pre className="overflow-auto rounded border border-red-500/40 bg-[var(--bg)] p-3 text-xs text-red-400">
              {runError}
            </pre>
          ) : null}

          {result ? (
            <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-auto">
              <p className="text-xs text-[var(--text-muted)]">
                exit_code: {String(result.exit_code)}
                {result.timed_out ? ' · timed out' : ''}
              </p>
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wide text-[var(--text-muted)]">
                  stdout
                </div>
                <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded border border-[var(--border)] bg-[var(--bg)] p-3 text-xs">
                  {result.stdout || '(empty)'}
                </pre>
              </div>
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wide text-[var(--text-muted)]">
                  stderr
                </div>
                <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded border border-[var(--border)] bg-[var(--bg)] p-3 text-xs">
                  {result.stderr || '(empty)'}
                </pre>
              </div>
            </div>
          ) : (
            <pre className="overflow-auto rounded border border-[var(--border)] bg-[var(--bg)] p-3 text-xs text-[var(--text-muted)]">
              {canRun
                ? 'Click Run to execute this lab via the loopback sidecar.'
                : 'Select a .py or .js file under 02_labs/ to enable Run.'}
            </pre>
          )}
        </div>
      )}
    </aside>
  )
}
