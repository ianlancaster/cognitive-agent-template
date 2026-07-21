#!/usr/bin/env python3
"""Archive Claude Code and Codex conversations without tool traffic."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


SYSTEM_TAG_PATTERNS = [
    re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL),
    re.compile(r"<local-command-[^>]*>.*?</local-command-[^>]*>", re.DOTALL),
    re.compile(r"<command-name>.*?</command-name>", re.DOTALL),
    re.compile(r"<command-message>.*?</command-message>", re.DOTALL),
    re.compile(r"<command-args>.*?</command-args>", re.DOTALL),
    re.compile(r"<task-notification>.*?</task-notification>", re.DOTALL),
    re.compile(r"<environment_context>.*?</environment_context>", re.DOTALL),
]


@dataclass(frozen=True)
class Session:
    provider: str
    path: Path
    session_id: str
    timestamp: str


def read_entries(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(entry, dict):
                yield entry


def clean_text(text: str) -> str:
    for pattern in SYSTEM_TAG_PATTERNS:
        text = pattern.sub("", text)
    return text.strip()


def block_text(content: object, accepted_types: set[str]) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict) or item.get("type") not in accepted_types:
            continue
        text = item.get("text")
        if isinstance(text, str) and text:
            parts.append(text)
    return "\n\n".join(parts)


def claude_turns(entries: Iterable[dict]) -> Iterator[tuple[str, str]]:
    for entry in entries:
        entry_type = entry.get("type")
        if entry_type not in {"user", "assistant"}:
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role", entry_type)
        if role not in {"user", "assistant"}:
            continue
        text = clean_text(block_text(message.get("content", ""), {"text"}))
        if text:
            yield role, text


def codex_turns(entries: Iterable[dict]) -> Iterator[tuple[str, str]]:
    for entry in entries:
        if entry.get("type") != "response_item":
            continue
        payload = entry.get("payload")
        if not isinstance(payload, dict) or payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            continue
        accepted = {"input_text"} if role == "user" else {"output_text"}
        text = clean_text(block_text(payload.get("content", []), accepted))
        if text:
            yield role, text


def detect_provider(entries: list[dict]) -> str | None:
    if any(entry.get("type") == "session_meta" for entry in entries):
        return "codex"
    if any(
        entry.get("type") in {"user", "assistant"}
        and isinstance(entry.get("message"), dict)
        for entry in entries
    ):
        return "claude"
    return None


def format_timestamp(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "unknown-date"
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "unknown-date"
    return parsed.strftime("%Y-%m-%d_%H%M")


def session_metadata(path: Path, provider: str, entries: list[dict]) -> Session:
    session_id = path.stem
    timestamp_value: object = None

    if provider == "codex":
        for entry in entries:
            if entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload")
            if isinstance(payload, dict):
                session_id = str(payload.get("id") or payload.get("session_id") or session_id)
                timestamp_value = payload.get("timestamp") or entry.get("timestamp")
                break
    else:
        for entry in entries:
            if entry.get("timestamp"):
                timestamp_value = entry.get("timestamp")
                break

    return Session(provider, path, session_id, format_timestamp(timestamp_value))


def render_session(path: Path, provider: str = "auto") -> tuple[Session, str] | None:
    entries = list(read_entries(path))
    resolved_provider = detect_provider(entries) if provider == "auto" else provider
    if resolved_provider not in {"claude", "codex"}:
        return None

    metadata = session_metadata(path, resolved_provider, entries)
    turns = claude_turns(entries) if resolved_provider == "claude" else codex_turns(entries)
    sections = [
        f"## {'User' if role == 'user' else 'Agent'}\n\n{text}\n"
        for role, text in turns
    ]
    if not sections:
        return None
    return metadata, "\n---\n\n".join(sections)


def claude_sources(repo_root: Path) -> Iterator[Path]:
    mangled = str(repo_root).replace("/", "-")
    project_dir = Path.home() / ".claude" / "projects" / mangled
    if project_dir.is_dir():
        yield from sorted(project_dir.glob("*.jsonl"))


def codex_source_matches(path: Path, repo_root: Path) -> bool:
    try:
        for entry in read_entries(path):
            if entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload")
            if not isinstance(payload, dict):
                return False
            thread_source = payload.get("thread_source")
            if thread_source is not None and thread_source != "user":
                return False
            cwd = payload.get("cwd")
            if not isinstance(cwd, str):
                return False
            try:
                resolved_cwd = Path(cwd).resolve()
                return resolved_cwd == repo_root or repo_root in resolved_cwd.parents
            except OSError:
                return False
    except OSError:
        return False
    return False


def codex_sources(repo_root: Path) -> Iterator[Path]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.is_dir():
        return
    for path in sorted(sessions_dir.rglob("*.jsonl")):
        if codex_source_matches(path, repo_root):
            yield path


def discover_sources(repo_root: Path, provider: str) -> list[Path]:
    paths: list[Path] = []
    if provider in {"auto", "claude"}:
        paths.extend(claude_sources(repo_root))
    if provider in {"auto", "codex"}:
        paths.extend(codex_sources(repo_root))
    return paths


def output_name(session: Session) -> str:
    if session.provider == "claude":
        return f"{session.timestamp}_{session.session_id}.md"
    return f"{session.timestamp}_codex_{session.session_id}.md"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session_id", nargs="?", help="extract one session and force refresh")
    parser.add_argument("--provider", choices=("auto", "claude", "codex"), default="auto")
    parser.add_argument("--transcript", type=Path, help="extract this exact JSONL transcript")
    parser.add_argument("--force", action="store_true", help="rewrite archives even if unchanged")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "conversations"

    if args.transcript:
        sources = [args.transcript.expanduser().resolve()]
    else:
        sources = discover_sources(repo_root, args.provider)

    matched = 0
    extracted = 0
    for source in sources:
        rendered = render_session(source, args.provider)
        if rendered is None:
            continue
        session, markdown = rendered
        if args.session_id and args.session_id not in {session.session_id, source.stem}:
            continue
        matched += 1
        out_path = out_dir / output_name(session)
        force = args.force or bool(args.session_id) or bool(args.transcript)
        if not force and out_path.exists() and out_path.stat().st_mtime_ns >= source.stat().st_mtime_ns:
            continue
        atomic_write(out_path, markdown)
        extracted += 1
        print(f"Extracted ({session.provider}): {out_path.name}")

    if args.session_id and matched == 0:
        print(f"Session not found: {args.session_id}", file=sys.stderr)
        return 1
    if not sources:
        print(f"No {args.provider} conversation sessions found for {repo_root}")
    print(f"Done. {extracted} conversation(s) updated in: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
