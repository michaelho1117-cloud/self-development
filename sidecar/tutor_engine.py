"""Mode-aware tutor engine with optional LLM streaming.

Injects AGENT.md + Mode iron laws into the system prompt. When no provider
credentials are configured, falls back to a clear stub (never crashes).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Literal

import httpx

from fs_manager import workspace_root

log = logging.getLogger("mytutor.tutor")

Mode = Literal["inspire", "stress", "unlock"]

MODE_SYSTEM: dict[Mode, str] = {
    "inspire": (
        "Mode=inspire (Anti-Spoiler & Scaffolding First).\n"
        "Follow AGENT.md iron laws strictly.\n"
        "- Lead with clarifying questions, hint ladders, TODO scaffolds, and assertions.\n"
        "- Never dump full worked solutions, exam keys, or complete code.\n"
        "- Prefer stubs with intentional gaps the learner must close.\n"
        "- Complete answers only if the learner says `unlock solution` or after repeated "
        "honest failure — and even then unlock stepwise."
    ),
    "stress": (
        "Mode=stress (Socratic Stress-Testing).\n"
        "Follow AGENT.md iron laws strictly.\n"
        "- Assume partial understanding; do NOT rubber-stamp mastery.\n"
        "- Ask 1–2 hard questions: Why not X / Edge Case / First Principles.\n"
        "- Do not spoil full answers. If they stumble, return to scaffolding.\n"
        "- Keep FE/SG distinctions clear when relevant."
    ),
    "unlock": (
        "Mode=unlock (explicit fuller explanation).\n"
        "The learner switched to unlock (aligned with saying `unlock solution`).\n"
        "- You MAY give fuller stepwise explanations and worked micro-examples.\n"
        "- Still prefer stepwise unlock over dumping entire exam keys or whole solutions.\n"
        "- End theory with a minimal `02_labs/` verification nudge (Theory-to-Lab Bridge)."
    ),
}


@dataclass(frozen=True)
class LlmConfig:
    """Resolved OpenAI-compatible or Anthropic credentials."""

    provider: Literal["openai_compatible", "anthropic"]
    api_key: str
    base_url: str | None
    model: str
    source: str  # human-readable which env path won


def agent_md_path() -> Path:
    return workspace_root() / "AGENT.md"


def agent_md_exists() -> bool:
    return agent_md_path().is_file()


def load_agent_excerpt(limit: int = 6000) -> str:
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
        "You are the Deep Tutor for this MyTutor local workbench "
        "(FE / SG exam self-study). Stay in tutor mode.\n\n"
        f"{base}\n\n"
        f"--- AGENT.md present={agent_md_exists()} ---\n"
        f"{agent}\n"
        f"--- end AGENT.md excerpt ---"
    )


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def resolve_llm_config() -> LlmConfig | None:
    """
    Prefer OpenAI-compatible / Netlify AI Gateway, then OpenAI, then Anthropic.

    Recognition order:
    1. MYTUTOR_LLM_* overrides (base URL + key, or provider=anthropic)
    2. OPENAI_BASE_URL + OPENAI_API_KEY (Netlify AI Gateway injects both)
    3. OPENAI_API_KEY alone (official OpenAI)
    4. ANTHROPIC_API_KEY (+ optional ANTHROPIC_BASE_URL)
    """
    model_default_openai = _env("MYTUTOR_LLM_MODEL") or _env("OPENAI_MODEL") or "gpt-4o-mini"
    model_default_anthropic = (
        _env("MYTUTOR_LLM_MODEL") or _env("ANTHROPIC_MODEL") or "claude-sonnet-4-5-20250929"
    )

    mytutor_key = _env("MYTUTOR_LLM_API_KEY")
    mytutor_base = _env("MYTUTOR_LLM_BASE_URL")
    mytutor_provider = (_env("MYTUTOR_LLM_PROVIDER") or "").lower()

    if mytutor_provider in {"anthropic", "claude"} and (
        mytutor_key or _env("ANTHROPIC_API_KEY")
    ):
        return LlmConfig(
            provider="anthropic",
            api_key=mytutor_key or _env("ANTHROPIC_API_KEY") or "",
            base_url=_env("MYTUTOR_LLM_BASE_URL") or _env("ANTHROPIC_BASE_URL"),
            model=model_default_anthropic,
            source="MYTUTOR_LLM_PROVIDER=anthropic",
        )

    if mytutor_base and (mytutor_key or _env("OPENAI_API_KEY")):
        return LlmConfig(
            provider="openai_compatible",
            api_key=mytutor_key or _env("OPENAI_API_KEY") or "",
            base_url=mytutor_base.rstrip("/"),
            model=model_default_openai,
            source="MYTUTOR_LLM_BASE_URL",
        )

    if mytutor_key and not mytutor_base:
        # Key-only override → treat as OpenAI-compatible default host.
        return LlmConfig(
            provider="openai_compatible",
            api_key=mytutor_key,
            base_url=None,
            model=model_default_openai,
            source="MYTUTOR_LLM_API_KEY",
        )

    openai_key = _env("OPENAI_API_KEY")
    openai_base = _env("OPENAI_BASE_URL")
    if openai_key and openai_base:
        return LlmConfig(
            provider="openai_compatible",
            api_key=openai_key,
            base_url=openai_base.rstrip("/"),
            model=model_default_openai,
            source="OPENAI_BASE_URL+OPENAI_API_KEY (e.g. Netlify AI Gateway)",
        )
    if openai_key:
        return LlmConfig(
            provider="openai_compatible",
            api_key=openai_key,
            base_url=None,
            model=model_default_openai,
            source="OPENAI_API_KEY",
        )

    anthropic_key = _env("ANTHROPIC_API_KEY")
    if anthropic_key:
        return LlmConfig(
            provider="anthropic",
            api_key=anthropic_key,
            base_url=_env("ANTHROPIC_BASE_URL"),
            model=model_default_anthropic,
            source="ANTHROPIC_API_KEY",
        )

    return None


def _normalize_messages(
    messages: list[dict[str, Any]],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for m in messages:
        role = str(m.get("role") or "user")
        if role not in {"user", "assistant", "system"}:
            role = "user"
        content = str(m.get("content") or "")
        if not content and role != "assistant":
            continue
        out.append({"role": role, "content": content})
    return out


def _pins_block(pins: list[Any] | None) -> str:
    if not pins:
        return ""
    try:
        rendered = json.dumps(pins, ensure_ascii=False, indent=2)
    except TypeError:
        rendered = str(pins)
    return (
        "\n\n--- Context pins from the workbench ---\n"
        f"{rendered}\n"
        "--- end pins ---"
    )


def placeholder_reply(mode: Mode, messages: list[dict[str, Any]]) -> str:
    """Clear stub when no LLM keys are configured — never crash the SSE path."""
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = str(m.get("content") or "")
            break

    exists = agent_md_exists()
    hint = (
        "No LLM API key configured — Mode-aware stub only. "
        "Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL for Netlify AI Gateway / "
        "OpenAI-compatible), or ANTHROPIC_API_KEY, or MYTUTOR_LLM_* — see sidecar/README.md."
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


async def _stream_openai_compatible(
    cfg: LlmConfig,
    system: str,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    """Stream chat.completions via OpenAI SDK (works with Netlify AI Gateway)."""
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "openai package missing — pip install -r requirements.txt"
        ) from exc

    client_kwargs: dict[str, Any] = {"api_key": cfg.api_key}
    if cfg.base_url:
        client_kwargs["base_url"] = cfg.base_url

    client = AsyncOpenAI(**client_kwargs)
    payload_messages = [{"role": "system", "content": system}, *messages]

    stream = await client.chat.completions.create(
        model=cfg.model,
        messages=payload_messages,
        stream=True,
        temperature=0.4,
    )
    async for event in stream:
        try:
            choice = event.choices[0]
            delta = choice.delta
            text = getattr(delta, "content", None) or ""
        except (AttributeError, IndexError, KeyError):
            continue
        if text:
            yield text


async def _stream_anthropic(
    cfg: LlmConfig,
    system: str,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    """Stream Anthropic Messages API (SSE) via httpx — no Anthropic SDK required."""
    base = (cfg.base_url or "https://api.anthropic.com").rstrip("/")
    url = f"{base}/v1/messages"

    # Anthropic rejects system in the messages array; fold only user/assistant turns.
    anth_messages: list[dict[str, str]] = []
    for m in messages:
        if m["role"] == "system":
            continue
        role = m["role"] if m["role"] in {"user", "assistant"} else "user"
        anth_messages.append({"role": role, "content": m["content"]})
    if not anth_messages:
        anth_messages = [{"role": "user", "content": "(empty)"}]

    headers = {
        "x-api-key": cfg.api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "accept": "text/event-stream",
    }
    body = {
        "model": cfg.model,
        "max_tokens": 2048,
        "system": system,
        "messages": anth_messages,
        "stream": True,
        "temperature": 0.4,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0)) as client:
        async with client.stream("POST", url, headers=headers, json=body) as resp:
            if resp.status_code >= 400:
                err_text = (await resp.aread()).decode("utf-8", errors="replace")
                raise RuntimeError(f"Anthropic HTTP {resp.status_code}: {err_text[:500]}")
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if not raw or raw == "[DONE]":
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if payload.get("type") == "content_block_delta":
                    delta = payload.get("delta") or {}
                    text = delta.get("text") or ""
                    if text:
                        yield text
                elif payload.get("type") == "error":
                    raise RuntimeError(str(payload.get("error") or payload))


async def stream_chat(
    mode: Mode,
    messages: list[dict[str, Any]],
    pins: list[Any] | None = None,
) -> AsyncIterator[str]:
    """
    Yield SSE `data:` payloads: meta → token* → done (or error token + done).

    Real LLM when env credentials resolve; otherwise Mode-aware stub.
    Always keeps `build_system_prompt(mode)` as the system message.
    """
    system = build_system_prompt(mode) + _pins_block(pins)
    normalized = _normalize_messages(messages)
    cfg = resolve_llm_config()

    meta: dict[str, Any] = {
        "type": "meta",
        "mode": mode,
        "agent_md": agent_md_exists(),
        "system_chars": len(system),
    }

    if cfg is None:
        meta["llm"] = "placeholder"
        meta["provider"] = None
        yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"
        reply = placeholder_reply(mode, messages)
        chunk_size = 48
        for i in range(0, len(reply), chunk_size):
            piece = reply[i : i + chunk_size]
            yield f"data: {json.dumps({'type': 'token', 'text': piece}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    meta["llm"] = "live"
    meta["provider"] = cfg.provider
    meta["model"] = cfg.model
    meta["source"] = cfg.source
    yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"

    try:
        if cfg.provider == "anthropic":
            token_iter = _stream_anthropic(cfg, system, normalized)
        else:
            token_iter = _stream_openai_compatible(cfg, system, normalized)

        async for text in token_iter:
            yield f"data: {json.dumps({'type': 'token', 'text': text}, ensure_ascii=False)}\n\n"
    except Exception as exc:  # noqa: BLE001 — surface to UI, keep SSE alive
        log.exception("tutor LLM stream failed (%s)", cfg.source)
        err = (
            f"\n\n[tutor llm error] {exc}\n"
            "Falling back note: check keys / base URL in sidecar/README.md. "
            "Mode + AGENT.md injection still applied on the next successful call."
        )
        yield f"data: {json.dumps({'type': 'token', 'text': err}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
