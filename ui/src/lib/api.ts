/** Sidecar client — defaults to loopback :8420 */

export const SIDECAR_BASE =
  import.meta.env.VITE_SIDECAR_URL ?? 'http://127.0.0.1:8420'

export type TreeNode = {
  name: string
  path: string
  type: 'file' | 'dir'
  children: TreeNode[] | null
}

export type FilePayload = {
  path: string
  content: string
  body: string
  frontmatter: Record<string, unknown>
  encoding: string
}

export type TutorMode = 'inspire' | 'stress' | 'unlock'

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body?.detail?.error ?? body?.error ?? JSON.stringify(body)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export async function fetchHealth(): Promise<{ ok: boolean; agent_md?: boolean }> {
  const res = await fetch(`${SIDECAR_BASE}/health`)
  return jsonOrThrow(res)
}

export async function fetchTree(root?: string): Promise<{ tree: TreeNode[] }> {
  const q = root ? `?root=${encodeURIComponent(root)}` : ''
  const res = await fetch(`${SIDECAR_BASE}/fs/tree${q}`)
  return jsonOrThrow(res)
}

export async function fetchFile(path: string): Promise<FilePayload> {
  const res = await fetch(
    `${SIDECAR_BASE}/fs/file?path=${encodeURIComponent(path)}`,
  )
  return jsonOrThrow(res)
}

export async function putFile(path: string, content: string): Promise<FilePayload> {
  const res = await fetch(`${SIDECAR_BASE}/fs/file`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, content }),
  })
  return jsonOrThrow(res)
}

export type ChatMessage = { role: string; content: string }

export type TutorSseEvent = {
  type: string
  text?: string
  mode?: string
  agent_md?: boolean
  llm?: 'live' | 'placeholder' | string
  provider?: string | null
  model?: string
  source?: string
  message?: string
  system_chars?: number
}

export async function* streamTutorChat(
  mode: TutorMode,
  messages: ChatMessage[],
  pins: unknown[] = [],
): AsyncGenerator<TutorSseEvent> {
  const res = await fetch(`${SIDECAR_BASE}/tutor/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ mode, messages, pins }),
  })
  if (!res.ok || !res.body) {
    throw new Error(`tutor chat failed: ${res.status}`)
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    // SSE events are separated by a blank line; tolerate \r\n.
    const parts = buffer.split(/\r?\n\r?\n/)
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const dataLines = part
        .split(/\r?\n/)
        .filter((l) => l.startsWith('data:'))
        .map((l) => l.replace(/^data:\s?/, ''))
      if (dataLines.length === 0) continue
      const raw = dataLines.join('\n')
      try {
        yield JSON.parse(raw) as TutorSseEvent
      } catch {
        /* ignore malformed chunk */
      }
    }
  }
}
