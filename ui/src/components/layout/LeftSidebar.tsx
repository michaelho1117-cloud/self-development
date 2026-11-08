import { useEffect, useState } from 'react'
import { fetchFile, fetchTree, type TreeNode } from '../../lib/api'
import { useWorkbench } from '../../stores/workbench'

function TreeItem({
  node,
  depth,
  onOpen,
  activePath,
}: {
  node: TreeNode
  depth: number
  onOpen: (path: string) => void
  activePath: string | null
}) {
  const [open, setOpen] = useState(depth < 1)
  const pad = { paddingLeft: `${8 + depth * 12}px` }

  if (node.type === 'dir') {
    return (
      <div>
        <button
          type="button"
          className="flex w-full items-center gap-1 truncate py-1 text-left text-sm text-[var(--text-muted)] hover:text-[var(--text)]"
          style={pad}
          onClick={() => setOpen((v) => !v)}
        >
          <span className="w-3 shrink-0 text-[10px]">{open ? '▾' : '▸'}</span>
          <span className="truncate">{node.name}/</span>
        </button>
        {open &&
          (node.children ?? []).map((child) => (
            <TreeItem
              key={child.path}
              node={child}
              depth={depth + 1}
              onOpen={onOpen}
              activePath={activePath}
            />
          ))}
      </div>
    )
  }

  const active = activePath === node.path
  return (
    <button
      type="button"
      className={`block w-full truncate py-1 text-left text-sm ${
        active
          ? 'bg-[var(--accent-soft)] text-[var(--text)]'
          : 'text-[var(--text)] hover:bg-[var(--bg-elevated)]'
      }`}
      style={pad}
      onClick={() => onOpen(node.path)}
      title={node.path}
    >
      {node.name}
    </button>
  )
}

export function LeftSidebar() {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [error, setError] = useState<string | null>(null)
  const currentPath = useWorkbench((s) => s.currentPath)
  const setPath = useWorkbench((s) => s.setPath)
  const setFileContent = useWorkbench((s) => s.setFileContent)
  const setDrawerTab = useWorkbench((s) => s.setDrawerTab)
  const sidecarOk = useWorkbench((s) => s.sidecarOk)

  useEffect(() => {
    let cancelled = false
    fetchTree()
      .then((data) => {
        if (!cancelled) {
          setTree(data.tree)
          setError(null)
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [sidecarOk])

  async function openFile(path: string) {
    try {
      const file = await fetchFile(path)
      setPath(path)
      setFileContent(file.content, false)
      setDrawerTab('feynman')
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <aside className="flex h-full flex-col bg-[var(--bg-panel)]">
      <div className="border-b border-[var(--border)] px-3 py-2">
        <div className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
          Workspace
        </div>
        <div className="text-sm font-medium">Navigation</div>
      </div>
      <div className="min-h-0 flex-1 overflow-auto py-1">
        {error && (
          <p className="px-3 py-2 text-xs text-red-300">
            {error}
            <br />
            Is sidecar on :8420?
          </p>
        )}
        {tree.map((node) => (
          <TreeItem
            key={node.path}
            node={node}
            depth={0}
            onOpen={openFile}
            activePath={currentPath}
          />
        ))}
      </div>
    </aside>
  )
}
