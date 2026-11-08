"""MyTutor sidecar — FastAPI on 127.0.0.1:8420 (loopback only)."""

from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import fs_manager
import lab_runner
import tutor_engine

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mytutor.sidecar")

app = FastAPI(title="MyTutor Sidecar", version="0.1.0")

# Local Vite only (loopback origins).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FileWriteBody(BaseModel):
    path: str
    content: str


class TutorChatBody(BaseModel):
    mode: Literal["inspire", "stress", "unlock"] = "inspire"
    messages: list[dict[str, Any]] = Field(default_factory=list)
    pins: list[Any] = Field(default_factory=list)


class LabRunBody(BaseModel):
    path: str
    runtime: Literal["py", "node"] = "py"


@app.get("/health")
def health() -> dict[str, Any]:
    llm = tutor_engine.resolve_llm_config()
    return {
        "ok": True,
        "service": "mytutor-sidecar",
        "workspace": str(fs_manager.workspace_root()),
        "agent_md": tutor_engine.agent_md_exists(),
        "llm": (
            {
                "configured": True,
                "provider": llm.provider,
                "model": llm.model,
                "source": llm.source,
            }
            if llm
            else {"configured": False, "provider": None, "model": None, "source": None}
        ),
    }


@app.get("/fs/tree")
def fs_tree(root: str | None = Query(default=None)) -> dict[str, Any]:
    try:
        tree = fs_manager.list_tree(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    return {"root": str(fs_manager.workspace_root()), "tree": tree}


@app.get("/fs/file")
def fs_file(path: str = Query(...)) -> dict[str, Any]:
    try:
        return fs_manager.read_file(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": f"not found: {path}"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc


@app.put("/fs/file")
def fs_file_put(body: FileWriteBody) -> dict[str, Any]:
    try:
        return fs_manager.write_file(body.path, body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except OSError as exc:
        log.exception("write failed")
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc


@app.get("/fs/events")
async def fs_events() -> StreamingResponse:
    """Watchdog SSE — stub stream for Phase 1 (optional full Watchdog later)."""

    async def gen():
        import json

        yield f"data: {json.dumps({'type': 'info', 'message': 'watchdog stub; reconnect later'})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/tutor/chat")
async def tutor_chat(body: TutorChatBody) -> StreamingResponse:
    async def gen():
        async for chunk in tutor_engine.stream_chat(body.mode, body.messages, body.pins):
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/labs/run")
async def labs_run(body: LabRunBody) -> dict[str, Any]:
    # P1 stub — always returns not_implemented with clear TODO.
    return await lab_runner.run_lab(body.path, body.runtime)


@app.get("/sessions")
def sessions_list() -> dict[str, Any]:
    # Optional SQLite index stub.
    return {"sessions": [], "note": "SQLite session store stub (optional Phase 1)"}


@app.put("/sessions/{session_id}")
def sessions_put(session_id: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": session_id,
        "saved": False,
        "stub": True,
        "payload": body or {},
        "note": "SQLite session store stub",
    }


def main() -> None:
    import uvicorn

    # Iron law: loopback only.
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8420,
        reload=False,
    )


if __name__ == "__main__":
    main()
