import { useWorkbench } from '../../stores/workbench'

export function Titlebar() {
  const sidecarOk = useWorkbench((s) => s.sidecarOk)

  return (
    <header className="flex h-10 shrink-0 items-center justify-between border-b border-[var(--border)] bg-[var(--bg-elevated)] px-4">
      <div className="flex items-baseline gap-2">
        <span className="text-sm font-semibold tracking-tight">MyTutor</span>
        <span className="text-xs text-[var(--text-muted)]">local workbench · Phase 1</span>
      </div>
      <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
        <span
          className="inline-block h-2 w-2 rounded-full"
          style={{
            background:
              sidecarOk === null
                ? '#666'
                : sidecarOk
                  ? 'var(--mode-inspire)'
                  : '#c44',
          }}
          title="Sidecar health"
        />
        sidecar :8420{' '}
        {sidecarOk === null ? '…' : sidecarOk ? 'ok' : 'down'}
      </div>
    </header>
  )
}
