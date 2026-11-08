"""Safe lab subprocess runner — only under 02_labs/, no shell, timeout kill."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

import fs_manager

LABS_PREFIX = "02_labs"
DEFAULT_TIMEOUT_SEC = 15.0
MIN_TIMEOUT_SEC = 1.0
MAX_TIMEOUT_SEC = 30.0
TIMEOUT_EXIT_CODE = 124

Runtime = Literal["py", "node"]


def _clamp_timeout(timeout_sec: float) -> float:
    try:
        value = float(timeout_sec)
    except (TypeError, ValueError) as exc:
        raise ValueError("timeout_sec must be a number") from exc
    if value < MIN_TIMEOUT_SEC or value > MAX_TIMEOUT_SEC:
        raise ValueError(
            f"timeout_sec must be between {MIN_TIMEOUT_SEC} and {MAX_TIMEOUT_SEC}"
        )
    return value


def _ensure_under_labs(rel_path: str) -> Path:
    """Resolve path and require it lives under 02_labs/ (file only)."""
    cleaned = rel_path.replace("\\", "/").lstrip("/")
    if not cleaned.startswith(f"{LABS_PREFIX}/") and cleaned != LABS_PREFIX:
        raise ValueError(f"lab path must be under {LABS_PREFIX}/")
    if cleaned == LABS_PREFIX or cleaned.endswith("/"):
        raise ValueError("lab path must point to a file under 02_labs/")

    path = fs_manager.resolve_safe(cleaned)
    # Defense in depth: resolve_safe allows other whitelist tops; re-check prefix.
    root = fs_manager.workspace_root()
    rel = path.resolve().relative_to(root.resolve())
    if rel.parts[0] != LABS_PREFIX:
        raise ValueError(f"lab path must be under {LABS_PREFIX}/")
    if not path.is_file():
        raise FileNotFoundError(cleaned)
    return path


def _interpreter_cmd(runtime: Runtime, script: Path) -> list[str]:
    if runtime == "py":
        return [sys.executable, str(script)]
    if runtime == "node":
        node = shutil.which("node")
        if not node:
            raise ValueError("node runtime requested but `node` was not found on PATH")
        return [node, str(script)]
    raise ValueError(f"unsupported runtime: {runtime}")


def _decode(data: bytes | str | None) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    return data.decode("utf-8", errors="replace")


def _run_sync(
    path: str,
    runtime: Runtime,
    timeout_sec: float,
) -> dict[str, Any]:
    script = _ensure_under_labs(path)
    cmd = _interpreter_cmd(runtime, script)
    # Never shell=True — argv list only; path already whitelist-resolved.
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(script.parent),
            capture_output=True,
            timeout=timeout_sec,
            shell=False,
            check=False,
            start_new_session=True,
        )
        return {
            "ok": completed.returncode == 0,
            "path": path.replace("\\", "/"),
            "runtime": runtime,
            "timeout_sec": timeout_sec,
            "stdout": _decode(completed.stdout),
            "stderr": _decode(completed.stderr),
            "exit_code": completed.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = _decode(exc.stdout)
        stderr = _decode(exc.stderr)
        note = f"[timeout] killed after {timeout_sec}s"
        stderr = f"{stderr}\n{note}" if stderr else note
        return {
            "ok": False,
            "path": path.replace("\\", "/"),
            "runtime": runtime,
            "timeout_sec": timeout_sec,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": TIMEOUT_EXIT_CODE,
            "timed_out": True,
            "error": "timeout",
        }


async def run_lab(
    path: str,
    runtime: Runtime = "py",
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> dict[str, Any]:
    """Execute a lab file under 02_labs/ and return stdout/stderr/exit_code."""
    if runtime not in ("py", "node"):
        raise ValueError("runtime must be 'py' or 'node'")
    clamped = _clamp_timeout(timeout_sec)
    return await asyncio.to_thread(_run_sync, path, runtime, clamped)
