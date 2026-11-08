import { useState } from 'react'
import { streamTutorChat, type TutorMode } from '../../lib/api'
import { useWorkbench } from '../../stores/workbench'

const MODES: TutorMode[] = ['inspire', 'stress', 'unlock']

const modeColor: Record<TutorMode, string> = {
  inspire: 'var(--mode-inspire)',
  stress: 'var(--mode-stress)',
  unlock: 'var(--mode-unlock)',
}

export function CenterStream() {
  const mode = useWorkbench((s) => s.mode)
  const setMode = useWorkbench((s) => s.setMode)
  const messages = useWorkbench((s) => s.messages)
  const appendMessage = useWorkbench((s) => s.appendMessage)
  const updateLastAssistant = useWorkbench((s) => s.updateLastAssistant)
  const streaming = useWorkbench((s) => s.streaming)
  const setStreaming = useWorkbench((s) => s.setStreaming)
  const currentPath = useWorkbench((s) => s.currentPath)
  const [draft, setDraft] = useState('')

  async function send() {
    const text = draft.trim()
    if (!text || streaming) return
    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user' as const,
      content: text,
    }
    appendMessage(userMsg)
    appendMessage({ id: `a-${Date.now()}`, role: 'assistant', content: '' })
    setDraft('')
    setStreaming(true)
    try {
      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }))
      for await (const ev of streamTutorChat(mode, history)) {
        if (ev.type === 'token' && ev.text) {
          updateLastAssistant(ev.text)
        }
      }
    } catch (err) {
      updateLastAssistant(
        `\n[error] ${err instanceof Error ? err.message : String(err)}`,
      )
    } finally {
      setStreaming(false)
    }
  }

  return (
    <section className="flex h-full flex-col bg-[var(--bg)]">
      <header className="flex items-center justify-between gap-3 border-b border-[var(--border)] px-4 py-2">
        <div>
          <div className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
            Pedagogical stream
          </div>
          <div className="text-sm text-[var(--text-muted)]">
            {currentPath ? `Pinned context: ${currentPath}` : 'No file pinned'}
          </div>
        </div>
        <div className="flex items-center gap-1 rounded-md border border-[var(--border)] p-0.5">
          {MODES.map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className="rounded px-2.5 py-1 text-xs font-medium capitalize"
              style={{
                background: mode === m ? modeColor[m] : 'transparent',
                color: mode === m ? '#0b1016' : 'var(--text-muted)',
              }}
              title={
                m === 'inspire'
                  ? 'Clues only'
                  : m === 'stress'
                    ? 'Hard questions'
                    : 'Explicit unlock'
              }
            >
              {m}
            </button>
          ))}
        </div>
      </header>

      <div className="min-h-0 flex-1 space-y-3 overflow-auto px-4 py-3">
        {messages.length === 0 && (
          <p className="text-sm text-[var(--text-muted)]">
            Mode-aware tutor stub. Sidecar injects <code>AGENT.md</code> — default
            is clues / stress tests, not spoilers. Wire a real LLM later (see
            sidecar README).
          </p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`max-w-[52rem] whitespace-pre-wrap rounded-md px-3 py-2 text-sm ${
              m.role === 'user'
                ? 'ml-auto bg-[var(--accent-soft)]'
                : 'bg-[var(--bg-elevated)]'
            }`}
          >
            <div className="mb-1 text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
              {m.role}
            </div>
            {m.content || (streaming ? '…' : '')}
          </div>
        ))}
      </div>

      <footer className="border-t border-[var(--border)] p-3">
        <div className="flex gap-2">
          <textarea
            className="min-h-[64px] flex-1 resize-y rounded-md border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
            placeholder="Ask the tutor (inspire = clues)…"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                void send()
              }
            }}
          />
          <button
            type="button"
            disabled={streaming || !draft.trim()}
            onClick={() => void send()}
            className="self-end rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            Send
          </button>
        </div>
        <p className="mt-1 text-[11px] text-[var(--text-muted)]">
          ⌘/Ctrl+Enter to send · No modals — Mode lives in this pill
        </p>
      </footer>
    </section>
  )
}
