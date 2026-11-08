import { useEffect } from 'react'
import { Group, Panel, Separator } from 'react-resizable-panels'
import { Titlebar } from './components/layout/Titlebar'
import { LeftSidebar } from './components/layout/LeftSidebar'
import { CenterStream } from './components/layout/CenterStream'
import { RightDrawer } from './components/layout/RightDrawer'
import { fetchHealth } from './lib/api'
import { useWorkbench } from './stores/workbench'

export default function App() {
  const setSidecarOk = useWorkbench((s) => s.setSidecarOk)

  useEffect(() => {
    let cancelled = false
    const tick = () => {
      fetchHealth()
        .then(() => {
          if (!cancelled) setSidecarOk(true)
        })
        .catch(() => {
          if (!cancelled) setSidecarOk(false)
        })
    }
    tick()
    const id = window.setInterval(tick, 8000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [setSidecarOk])

  return (
    <div className="flex h-full flex-col">
      <Titlebar />
      <Group
        orientation="horizontal"
        className="min-h-0 flex-1"
        id="workbench"
      >
        <Panel id="nav" defaultSize="22%" minSize="14%" className="min-w-0">
          <LeftSidebar />
        </Panel>
        <Separator className="w-1" />
        <Panel id="stream" defaultSize="48%" minSize="30%" className="min-w-0">
          <CenterStream />
        </Panel>
        <Separator className="w-1" />
        <Panel id="drawer" defaultSize="30%" minSize="18%" className="min-w-0">
          <RightDrawer />
        </Panel>
      </Group>
    </div>
  )
}
