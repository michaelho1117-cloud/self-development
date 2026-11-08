import { putFile } from '../../lib/api'
import { useWorkbench } from '../../stores/workbench'

export function RightDrawer() {
  const tab = useWorkbench((s) => s.drawerTab)
  const setDrawerTab = useWorkbench((s) => s.setDrawerTab)
  const currentPath = useWorkbench((s) => s.currentPath)
  const fileContent = useWorkbench((s) => s.fileContent)
  const setFileContent = useWorkbench((s) => s.setFileContent)
  const fileDirty = useWorkbench((s) => s.fileDirty)
  const setPath = useWorkbench((s) => s.setPath)

  async function save() {
    if (!currentPath) return
    const saved = await putFile(currentPath, fileContent)
    setFileContent(saved.content, false)
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
            <span className="truncate text-xs text-[var(--text-muted)]">
              {currentPath ?? 'Open a file from the left tree'}
              {fileDirty ? ' · unsaved' : ''}
            </span>
            <button
              type="button"
              disabled={!currentPath || !fileDirty}
              onClick={() => void save().catch(console.error)}
              className="rounded bg-[var(--accent)] px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
            >
              Save
            </button>
          </div>
          <textarea
            className="min-h-0 flex-1 resize-none bg-[var(--bg)] px-3 py-2 font-mono text-xs leading-relaxed outline-none"
            value={fileContent}
            placeholder="Markdown / concept card content…"
            onChange={(e) => {
              setFileContent(e.target.value, true)
              if (!currentPath) setPath(null)
            }}
            disabled={!currentPath}
          />
          <p className="border-t border-[var(--border)] px-3 py-2 text-[11px] text-[var(--text-muted)]">
            KaTeX preview lands with richer editor polish; Phase 1 ships save via{' '}
            <code>PUT /fs/file</code>.
          </p>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col gap-3 p-3 text-sm">
          <p className="text-[var(--text-muted)]">
            Lab runner is a <strong className="text-[var(--text)]">P1 stub</strong>.
            Use <code>02_labs/</code> notes for now; sidecar{' '}
            <code>POST /labs/run</code> returns <code>not_implemented</code>.
          </p>
          <pre className="overflow-auto rounded border border-[var(--border)] bg-[var(--bg)] p-3 text-xs text-[var(--text-muted)]">
            {`TODO(P1): wire lab_runner subprocess
- path under 02_labs/
- runtime: py | node
- timeout + stdout/stderr`}
          </pre>
          <button
            type="button"
            disabled
            className="self-start rounded border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text-muted)] opacity-60"
            title="Available in Phase 2 / Spec P1"
          >
            Run lab (coming soon)
          </button>
        </div>
      )}
    </aside>
  )
}
