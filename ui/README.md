# MyTutor UI

Vite + React 19 + TypeScript + Tailwind v4 three-pane workbench (Local-First).

Talks to the FastAPI sidecar at **`http://127.0.0.1:8420`**.

## Run

Start the sidecar first (see `../sidecar/README.md`), then:

```bash
cd ui
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

Optional override:

```bash
VITE_SIDECAR_URL=http://127.0.0.1:8420 npm run dev
```

## Layout (no modals)

| Pane | Role |
|------|------|
| **Left** | Workspace file tree from `GET /fs/tree` |
| **Center** | Mode pill + tutor SSE stream (`POST /tutor/chat`) |
| **Right** | Tabs: Feynman (MD edit / `PUT /fs/file`) · Lab (P1 stub) |

State: Zustand (`path` / `mode` / `drawerTab` / stream messages).

## Smoke checklist

1. Sidecar health dot turns green.
2. Open `templates/concept-card.md` from the left tree.
3. Edit + Save in the Feynman tab.
4. Send a message in **inspire** mode — placeholder SSE should mention `AGENT.md`.
