"""Lab runner stub — full sandbox execution is Phase 1+ / Spec P1."""

from __future__ import annotations

from typing import Any, Literal


# TODO(P1): implement safe subprocess runner
# - resolve path via fs_manager.resolve_safe under 02_labs/
# - runtime ∈ {py, node}; timeout kill; capture stdout/stderr
# - never shell=True; never write outside workspace
# - bind no network; prefer resource limits where available


async def run_lab(
    path: str,
    runtime: Literal["py", "node"] = "py",
    timeout_sec: float = 10.0,
) -> dict[str, Any]:
    """Return a clear stub until P1 lands."""
    return {
        "ok": False,
        "stub": True,
        "path": path,
        "runtime": runtime,
        "timeout_sec": timeout_sec,
        "stdout": "",
        "stderr": (
            "lab_runner is a Phase-1 stub. "
            "TODO(P1): implement subprocess + timeout per SPEC.md §6 `/labs/run`."
        ),
        "exit_code": None,
        "error": "not_implemented",
    }
