# MyTutor Sidecar (FastAPI)

Loopback-only API bridge for the local workbench. Binds **`127.0.0.1:8420`** only.

Workspace root defaults to the **repo root** (parent of `sidecar/`). Override with `WORKSPACE_ROOT`.

## Run

```bash
cd sidecar
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
# or: uvicorn main:app --host 127.0.0.1 --port 8420
```

Health check: `curl http://127.0.0.1:8420/health`

## API surface

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/health` | Liveness + workspace + `AGENT.md` + LLM config summary |
| `GET` | `/fs/tree?root=` | Whitelist tree (`00_`–`03_`, `templates`, root protocol files) |
| `GET` | `/fs/file?path=` | Read file + frontmatter |
| `PUT` | `/fs/file` | Write `.md`/source (safe join, no escape) |
| `GET` | `/fs/events` | SSE stub (Watchdog later) |
| `POST` | `/tutor/chat` | Mode-aware SSE; injects `AGENT.md` + streams LLM tokens |
| `POST` | `/labs/run` | **P1 stub** — returns `not_implemented` |
| `GET/PUT` | `/sessions…` | Optional SQLite stub |

CORS allows local Vite (`http://127.0.0.1:5173`, `localhost:5173`).

## Tutor LLM environment

`POST /tutor/chat` always injects `build_system_prompt(mode)` (Mode iron laws + `AGENT.md` excerpt). Modes:

| Mode | Behavior |
|------|----------|
| `inspire` | Clues / questions / TODO scaffolds only (anti-spoiler) |
| `stress` | 1–2 hard Socratic questions; no spoilers |
| `unlock` | Explicit stepwise fuller explanation (still no exam-key dump) |

If **no** credentials resolve at runtime, the endpoint streams a clear Mode-aware **stub** message (does not crash).

### Recognition order

1. **`MYTUTOR_LLM_*` overrides**
2. **`OPENAI_BASE_URL` + `OPENAI_API_KEY`** — OpenAI-compatible, including **Netlify AI Gateway** (gateway injects both after a production deploy)
3. **`OPENAI_API_KEY`** alone — official OpenAI
4. **`ANTHROPIC_API_KEY`** (+ optional `ANTHROPIC_BASE_URL`)

### Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI or OpenAI-compatible API key |
| `OPENAI_BASE_URL` | Optional base URL (Netlify AI Gateway / proxies). No trailing slash required. |
| `OPENAI_MODEL` | Optional model id (default `gpt-4o-mini`) |
| `ANTHROPIC_API_KEY` | Anthropic Messages API key |
| `ANTHROPIC_BASE_URL` | Optional Anthropic base (default `https://api.anthropic.com`) |
| `ANTHROPIC_MODEL` | Optional model id (default `claude-sonnet-4-5-20250929`) |
| `MYTUTOR_LLM_API_KEY` | Override key (wins over provider defaults when set with base URL / alone) |
| `MYTUTOR_LLM_BASE_URL` | Override OpenAI-compatible base URL |
| `MYTUTOR_LLM_MODEL` | Override model id for either provider |
| `MYTUTOR_LLM_PROVIDER` | Set to `anthropic` to force Anthropic path |

Never commit secrets. Export in your shell or a local `.env` that is gitignored.

### Examples

**OpenAI (official):**

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"   # optional
python main.py
```

**Netlify AI Gateway / any OpenAI-compatible proxy:**

```bash
export OPENAI_BASE_URL="https://your-gateway.example/v1"  # Netlify injects this in Functions
export OPENAI_API_KEY="..."                               # Netlify injects a placeholder key
export OPENAI_MODEL="gpt-4o-mini"
python main.py
```

> Note: Netlify AI Gateway auto-injection is for Netlify Functions after a production deploy. For this **local loopback sidecar**, copy the compatible base URL + key into your shell, or use a direct provider key.

**Anthropic:**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250929"  # optional
python main.py
```

**Explicit MyTutor overrides:**

```bash
export MYTUTOR_LLM_BASE_URL="http://127.0.0.1:1234/v1"  # e.g. local llama.cpp / ollama openai shim
export MYTUTOR_LLM_API_KEY="local"
export MYTUTOR_LLM_MODEL="local-model"
python main.py
```

### SSE event shape (unchanged)

```text
data: {"type":"meta","mode":"inspire","agent_md":true,"llm":"live"|"placeholder",...}

data: {"type":"token","text":"..."}

data: {"type":"done"}
```

On provider failure after keys were found, a `token` error note is streamed plus `{"type":"error",...}`, then `done` — the connection does not hard-crash.

## Security notes

- Listen address is hardcoded to `127.0.0.1`.
- Paths are resolved under the workspace and checked against a whitelist; `..` escapes are rejected.
- Lab execution is intentionally stubbed until P1 sandbox work.
- Do not log API key values.
