"""Workspace filesystem helpers with path whitelist + escape protection."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import frontmatter

# Pedagogue dirs + root protocol docs (SPEC Phase 1 whitelist).
ALLOWED_TOP_LEVEL_DIRS = (
    "00_roadmap",
    "01_concepts",
    "02_labs",
    "03_reviews",
    "templates",
)
ALLOWED_ROOT_FILES = (
    "AGENT.md",
    "SPEC.md",
    "README.md",
    ".cursorrules",
)


def workspace_root() -> Path:
    env = os.environ.get("WORKSPACE_ROOT")
    if env:
        return Path(env).resolve()
    # sidecar/ lives one level under the repo root.
    return Path(__file__).resolve().parent.parent


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve_safe(rel_path: str) -> Path:
    """Join rel_path under workspace; reject escapes and non-whitelist paths."""
    root = workspace_root()
    if not rel_path or rel_path.strip() == "":
        raise ValueError("path is required")

    # Normalize separators; forbid absolute / drive / null bytes.
    cleaned = rel_path.replace("\\", "/").lstrip("/")
    if "\x00" in cleaned or cleaned.startswith("~"):
        raise ValueError("invalid path")

    candidate = (root / cleaned).resolve()
    if not _is_under(candidate, root) and candidate != root:
        raise ValueError("path escapes workspace")

    rel = candidate.relative_to(root)
    parts = rel.parts
    if not parts:
        raise ValueError("cannot target workspace root as a file")

    top = parts[0]
    if top in ALLOWED_TOP_LEVEL_DIRS:
        return candidate
    if len(parts) == 1 and top in ALLOWED_ROOT_FILES:
        return candidate
    raise ValueError(f"path not in whitelist: {rel_path}")


def list_tree(root_hint: str | None = None) -> list[dict[str, Any]]:
    """Return a nested tree of whitelisted paths."""
    root = workspace_root()
    nodes: list[dict[str, Any]] = []

    # Optional root protocol files
    for name in ALLOWED_ROOT_FILES:
        p = root / name
        if p.is_file():
            nodes.append(
                {
                    "name": name,
                    "path": name,
                    "type": "file",
                    "children": None,
                }
            )

    dirs = ALLOWED_TOP_LEVEL_DIRS
    if root_hint:
        hint = root_hint.strip().strip("/")
        if hint and hint in ALLOWED_TOP_LEVEL_DIRS:
            dirs = (hint,)

    for dirname in dirs:
        d = root / dirname
        if not d.exists():
            continue
        nodes.append(_dir_node(d, root))

    return nodes


def _dir_node(directory: Path, root: Path) -> dict[str, Any]:
    children: list[dict[str, Any]] = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        entries = []

    for entry in entries:
        if entry.name.startswith(".") and entry.name not in {".cursorrules"}:
            continue
        rel = str(entry.relative_to(root)).replace("\\", "/")
        if entry.is_dir():
            children.append(_dir_node(entry, root))
        elif entry.is_file():
            children.append({"name": entry.name, "path": rel, "type": "file", "children": None})

    rel_dir = str(directory.relative_to(root)).replace("\\", "/")
    return {
        "name": directory.name,
        "path": rel_dir,
        "type": "dir",
        "children": children,
    }


def read_file(rel_path: str) -> dict[str, Any]:
    path = resolve_safe(rel_path)
    if not path.is_file():
        raise FileNotFoundError(rel_path)

    raw = path.read_text(encoding="utf-8")
    meta: dict[str, Any] = {}
    body = raw
    if path.suffix.lower() in {".md", ".markdown"}:
        try:
            post = frontmatter.loads(raw)
            meta = dict(post.metadata) if post.metadata else {}
            body = post.content
        except Exception:
            # Soft-fail frontmatter parse; still return raw.
            meta = {}
            body = raw

    return {
        "path": rel_path.replace("\\", "/"),
        "content": raw,
        "body": body,
        "frontmatter": meta,
        "encoding": "utf-8",
    }


def write_file(rel_path: str, content: str) -> dict[str, Any]:
    path = resolve_safe(rel_path)
    # Only allow writing markdown / source under whitelist (not binary dumps).
    allowed_suffixes = {".md", ".markdown", ".py", ".js", ".ts", ".tsx", ".txt", ".json"}
    if path.suffix.lower() not in allowed_suffixes and path.name not in ALLOWED_ROOT_FILES:
        raise ValueError(f"refusing to write suffix {path.suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return read_file(rel_path)
