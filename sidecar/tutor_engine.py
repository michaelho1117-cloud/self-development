"""Mode-aware tutor stubs. Full LLM wiring is optional (no API keys required for Phase 1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator, Literal

from fs_manager import workspace_root

Mode = Literal["inspire", "stress", "unlock"]

MODE_SYSTEM: dict[Mode, str] = {
    "inspire": (
        "Mode=inspire. Follow AGENT.md iron laws. Give clues, questions, and TODO scaffolds only. "
        "Do NOT dump full answers or exam keys."
    ),
    "stress": (
        "Mode=stress. Follow AGENT.md. After any claimed understanding, ask 1–2 hard questions "
        "(Why not X / Edge Case / First Principles). Do not spoil."
    ),
    "unlock": (
        "Mode=unlock. Learner explicitly requested fuller explanation. Still prefer stepwise unlock "
        "aligned with AGENT.md; avoid dumping entire exam keys."
    ),
}


def agent_md_path() -> Path:
    return workspace_root() / "AGENT.md"


def agent_md_exists() -> bool:
    return agent_md_path().is_file()


def load_agent_excerpt(limit: int = 1200) -> str:
    path = agent_md_path()
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncated; full protocol in AGENT.md]"


def build_system_prompt(mode: Mode) -> str:
    base = MODE_SYSTEM.get(mode, MODE_SYSTEM["inspire"])
    agent = load_agent_excerpt()
    return (
        f"{base}\n\n"
        f"--- AGENT.md present={agent_md_exists()} ---\n"
        f"{agent}\n"
        f"--- end AGENT.md excerpt ---"
    )


def placeholder_reply(mode: Mode, messages: list[dict[str, Any]]) -> str:
    """Deterministic Phase 1 stub when no LLM keys are configured."""
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = str(m.get("content") or "")
            break

    exists = agent_md_exists()
    hint = (
        "LLM keys are not wired yet — this is a Mode-aware placeholder. "
        "See sidecar/README.md to connect LiteLLM / an OpenAI-compatible API later."
    )

    if mode == "inspire":
        body = (
            f"[inspire] AGENT.md loaded={exists}. "
            "Start with a clarifying question, then one hint. "
            "Do not request the full solution yet.\n\n"
            f"You said: {last_user[:280] or '(empty)'}\n\n"
            "Scaffold: what is the smallest claim you can test in `02_labs/`?"
        )
    elif mode == "stress":
        body = (
            f"[stress] AGENT.md loaded={exists}. "
            "Assume a partial answer. Why not the obvious alternative? "
            "What edge case breaks your explanation?\n\n"
            f"You said: {last_user[:280] or '(empty)'}"
        )
    else:
        body = (
            f"[unlock] AGENT.md loaded={exists}. "
            "Stepwise unlock only — still no exam-key dump. "
            "State the first principle, then one worked micro-example with a TODO for you to close.\n\n"
            f"You said: {last_user[:280] or '(empty)'}"
        )

    return f"{body}\n\n({hint})"


async def stream_chat(
    mode: Mode,
    messages: list[dict[str, Any]],
    pins: list[Any] | None = None,
) -> AsyncIterator[str]:
    """
    Yield SSE `data:` payloads.

    Phase 1: placeholder tokens. When OPENAI_API_KEY / LITELLM is set later,
    replace the body of this generator with a real streaming client while
    keeping `build_system_prompt(mode)` as the system message.
    """
    _ = pins  # reserved for context pins
    system = build_system_prompt(mode)
    reply = placeholder_reply(mode, messages)

    # Emit a meta event first so the UI can show Mode + AGENT.md status.
    meta = {
        "type": "meta",
        "mode": mode,
        "agent_md": agent_md_exists(),
        "system_chars": len(system),
        "llm": "placeholder",
    }
    yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"

    # Stream reply in small chunks to exercise SSE clients.
    chunk_size = 48
    for i in range(0, len(reply), chunk_size):
        piece = reply[i : i + chunk_size]
        yield f"data: {json.dumps({'type': 'token', 'text': piece}, ensure_ascii=False)}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
