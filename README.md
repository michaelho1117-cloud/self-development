# self-development

Agent-native study workspace for Japan’s 情報技術者試験 — **基本情報技術者 (FE)** and **情報処理安全確保支援士 (SG / 登録セキスペ)**.

Pedagogy is inspired by [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) and [deeptutor.info](https://deeptutor.info/) (Socratic / guided solve, mastery paths, durable memory). That project is **inspiration only**, not a dependency — nothing from it is vendored or run here.

**Product contract:** [`SPEC.md`](./SPEC.md) (architecture / Phase plan) · **Tutor protocol:** [`AGENT.md`](./AGENT.md)

## How to study here

1. Open `00_roadmap/` for the syllabus and short next-topics queue.
2. Capture theory in `01_concepts/` using `templates/concept-card.md`.
3. Verify with a minimal task in `02_labs/` (`templates/lab-note.md`).
4. Schedule blindspots / quizzes / weekly recall in `03_reviews/` (`templates/review-active-recall.md`).
5. Commit progress with semantic messages (see `AGENT.md`).

Work with a Cursor agent that follows this workspace’s tutor protocol — ask questions, attempt scaffolds, and only request `unlock solution` when stuck after honest tries.

## Local workbench (Phase 1)

Three-pane Local-First UI + loopback FastAPI sidecar. Markdown + Git remain the source of truth.

### Run UI + sidecar together

**Terminal A — sidecar** (`127.0.0.1:8420` only):

```bash
cd sidecar
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal B — UI**:

```bash
cd ui
npm install
npm run dev
```

Open **http://127.0.0.1:5173**. Details: [`sidecar/README.md`](./sidecar/README.md), [`ui/README.md`](./ui/README.md).

Smoke: open `templates/concept-card.md` → inspire chat → edit/save in the Feynman tab.

## How AGENT.md works

| File | Role |
|------|------|
| **`AGENT.md`** | Source of truth: full Deep Tutor role, FE/SG context, directory map, template usage, and the **four iron laws** in full |
| **`.cursorrules`** | Short Cursor hook: always read `AGENT.md`, abbreviated laws, never spoil |
| **`SPEC.md`** | Product / architecture contract for the workbench (Phases, API, layout slots) |

Agents should load `AGENT.md` before teaching. `.cursorrules` exists so Cursor surfaces the protocol automatically; it deliberately stays thin so the laws are not duplicated in two long copies.

## Layout

```text
SPEC.md         product / architecture contract
AGENT.md        canonical tutor protocol
.cursorrules    Cursor entrypoint → AGENT.md
00_roadmap/     syllabus + next topics (FE / SG seeds)
01_concepts/    concept cards (empty until you study)
02_labs/        verification labs
03_reviews/     blindspots, quizzes, weekly reviews
templates/      Markdown skeletons
sidecar/        FastAPI loopback API (Phase 1)
ui/             Vite + React three-pane shell (Phase 1)
```
