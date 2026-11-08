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
| **Right** | Tabs: Feynman (Edit / Preview + Save via `PUT /fs/file`) · Lab runner |

State: Zustand (`path` / `mode` / `drawerTab` / stream messages).

Feynman **Preview** renders GFM Markdown + KaTeX (`remark-math` / `rehype-katex`).

## Smoke checklist

1. Sidecar health dot turns green.
2. Open `01_concepts/fe-algorithms-complexity.md` (or `templates/concept-card.md`) from the left tree.
3. Toggle **Preview** in the Feynman tab — headings, tables, and emphasis should read cleanly.
4. In Edit, add `$O(n \\log n)$` / `$$\\sum_{i=1}^{n} i$$`, switch to Preview, confirm KaTeX.
5. Edit + Save still works.
6. Optional: `npm run smoke:md` processes `../01_concepts/*.md` through the same MD+math pipeline.
