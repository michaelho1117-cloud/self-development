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

## Phase 1 API surface

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/health` | Liveness + workspace + `AGENT.md` flag |
| `GET` | `/fs/tree?root=` | Whitelist tree (`00_`–`03_`, `templates`, root protocol files) |
| `GET` | `/fs/file?path=` | Read file + frontmatter |
| `PUT` | `/fs/file` | Write `.md`/source (safe join, no escape) |
| `GET` | `/fs/events` | SSE stub (Watchdog later) |
| `POST` | `/tutor/chat` | Mode-aware SSE; injects `AGENT.md` excerpt |
| `POST` | `/labs/run` | **P1 stub** — returns `not_implemented` |
| `GET/PUT` | `/sessions…` | Optional SQLite stub |

CORS allows local Vite (`http://127.0.0.1:5173`, `localhost:5173`).

## Wiring a real LLM later

`tutor_engine.stream_chat` currently streams a **Mode-aware placeholder** so the UI SSE path works without API keys. To wire a model:

1. Set provider credentials in the environment (never commit secrets), e.g. `OPENAI_API_KEY` or LiteLLM vars.
2. Keep `build_system_prompt(mode)` as the system message (it already loads `AGENT.md` + Mode rules).
3. Replace the placeholder loop in `stream_chat` with your streaming client; keep SSE event shapes (`meta` / `token` / `done`).
4. Default Mode remains `inspire` / `stress` — never auto-dump answers (see `AGENT.md` / `SPEC.md`).

## Security notes

- Listen address is hardcoded to `127.0.0.1`.
- Paths are resolved under the workspace and checked against a whitelist; `..` escapes are rejected.
- Lab execution is intentionally stubbed until P1 sandbox work.
