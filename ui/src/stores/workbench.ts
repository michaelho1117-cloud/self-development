import { create } from 'zustand'
import type { TutorMode } from '../lib/api'

export type DrawerTab = 'feynman' | 'lab'

export type StreamMessage = {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
}

type WorkbenchState = {
  currentPath: string | null
  fileContent: string
  fileDirty: boolean
  mode: TutorMode
  drawerTab: DrawerTab
  messages: StreamMessage[]
  streaming: boolean
  sidecarOk: boolean | null
  setPath: (path: string | null) => void
  setFileContent: (content: string, dirty?: boolean) => void
  setMode: (mode: TutorMode) => void
  setDrawerTab: (tab: DrawerTab) => void
  appendMessage: (msg: StreamMessage) => void
  updateLastAssistant: (chunk: string) => void
  setStreaming: (v: boolean) => void
  setSidecarOk: (v: boolean | null) => void
  resetStream: () => void
}

export const useWorkbench = create<WorkbenchState>((set) => ({
  currentPath: null,
  fileContent: '',
  fileDirty: false,
  mode: 'inspire',
  drawerTab: 'feynman',
  messages: [],
  streaming: false,
  sidecarOk: null,
  setPath: (path) => set({ currentPath: path }),
  setFileContent: (content, dirty = false) =>
    set({ fileContent: content, fileDirty: dirty }),
  setMode: (mode) => set({ mode }),
  setDrawerTab: (drawerTab) => set({ drawerTab }),
  appendMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),
  updateLastAssistant: (chunk) =>
    set((s) => {
      const msgs = [...s.messages]
      for (let i = msgs.length - 1; i >= 0; i -= 1) {
        if (msgs[i].role === 'assistant') {
          msgs[i] = { ...msgs[i], content: msgs[i].content + chunk }
          break
        }
      }
      return { messages: msgs }
    }),
  setStreaming: (streaming) => set({ streaming }),
  setSidecarOk: (sidecarOk) => set({ sidecarOk }),
  resetStream: () => set({ messages: [] }),
}))
