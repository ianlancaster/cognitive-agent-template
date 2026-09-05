#!/usr/bin/env python3
"""Archive Claude Code and Codex conversations without tool traffic."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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

# Outbound conductor communications are conversation, not tool noise: they are
# the only tool calls preserved in archives. All other tool traffic is dropped.
# Intent/content only — delivery receipts are transport state and stay out.
CONDUCTOR_SEND_TOOLS = {"send_to_session", "send_to_operator", "broadcast"}
CONDUCTOR_TOOL_RE = re.compile(r"^mcp__conductor__(send_to_session|send_to_operator|broadcast)$")
ARCHIVE_FORMAT = "<!-- cognitive-archive-format: 2 -->"


@dataclass(frozen=True)
class Session:
    provider: str
    path: Path
    session_id: str
    timestamp: str


def read_entries(path: Path) -> Iterator[dict]:
    yield from parse_entries(path.read_bytes())


def parse_entries(raw: bytes) -> Iterator[dict]:
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(entry, dict):
            entry["_archive_line"] = line_number
            yield entry


def input_heading(raw: str) -> str:
    """Classify visible transport markers, never authenticate their author."""
    text = raw.lstrip()
    if text.startswith("# AGENTS.md instructions") and "<INSTRUCTIONS>" in text:
        return "Runtime input (AGENTS wrapper; attribution unverified)"
    if re.match(r"\[(?:Message|Broadcast) from [^\]\n]+\]", text):
        return "Incoming message (sender claim in text; unverified)"
    if text.startswith(("[Sentinel]", "[Conductor pause notice]")):
        return "Incoming runtime notice (attribution unverified)"
    return "User input (authorship unverified)"


def turn_provenance(entry: dict, block: int) -> str:
    payload = entry.get("payload")
    payload = payload if isinstance(payload, dict) else {}
    identity = entry.get("uuid") or payload.get("id") or payload.get("call_id")
    provenance = {
        "sourceLine": entry.get("_archive_line"),
        "block": block,
        "timestamp": entry.get("timestamp") or payload.get("timestamp"),
        "eventId": identity,
    }
    return "Source event: " + json.dumps(provenance, ensure_ascii=True) + "\n\n"


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


def conductor_send(tool: str, arguments: object) -> tuple[str, str] | None:
    if not isinstance(arguments, dict):
        return None
    message = arguments.get("message")
    if not isinstance(message, str) or not message.strip():
        return None

    if tool == "send_to_session":
        codename = arguments.get("codename")
        target = codename if isinstance(codename, str) and codename else "unknown"
        heading = f"Agent → session `{target}`"
    elif tool == "send_to_operator":
        heading = "Agent → operator"
    elif tool == "broadcast":
        heading = "Agent → all sessions"
    else:
        return None

    body = message.strip()
    options = arguments.get("options")
    if isinstance(options, list):
        string_options = [option for option in options if isinstance(option, str)]
        if string_options:
            bullets = "\n".join(f"- {option}" for option in string_options)
            body = f"{body}\n\nOptions:\n{bullets}"
    return heading, body


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
        content = message.get("content", "")
        if role == "user" or not isinstance(content, list):
            text = clean_text(block_text(content, {"text"}))
            if text:
                yield (input_heading(block_text(content, {"text"})) if role == "user" else "Agent"), text
            continue
        # Assistant blocks are walked in order so conductor sends keep their
        # position relative to the surrounding visible text.
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                raw = item.get("text")
                text = clean_text(raw) if isinstance(raw, str) else ""
                if text:
                    yield "Agent", text
                continue
            if item.get("type") != "tool_use":
                continue
            match = CONDUCTOR_TOOL_RE.match(str(item.get("name", "")))
            if not match:
                continue
            send = conductor_send(match.group(1), item.get("input"))
            if send:
                yield send


def codex_conductor_call(entry_type: object, payload: dict) -> tuple[object, str, object] | None:
    payload_type = payload.get("type")
    if entry_type == "event_msg" and payload_type == "mcp_tool_call_end":
        invocation = payload.get("invocation")
        if not isinstance(invocation, dict) or invocation.get("server") != "conductor":
            return None
        tool = invocation.get("tool")
        if tool not in CONDUCTOR_SEND_TOOLS:
            return None
        return payload.get("call_id"), tool, invocation.get("arguments")
    if entry_type == "response_item" and payload_type == "function_call":
        match = CONDUCTOR_TOOL_RE.match(str(payload.get("name", "")))
        if not match:
            return None
        arguments = payload.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return None
        return payload.get("call_id"), match.group(1), arguments
    return None


def codex_turns(entries: Iterable[dict]) -> Iterator[tuple[str, str]]:
    seen_call_ids: set[object] = set()
    for entry in entries:
        entry_type = entry.get("type")
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            continue
        if entry_type == "response_item" and payload.get("type") == "message":
            role = payload.get("role")
            if role not in {"user", "assistant"}:
                continue
            accepted = {"input_text"} if role == "user" else {"output_text"}
            text = clean_text(block_text(payload.get("content", []), accepted))
            if text:
                yield (input_heading(block_text(payload.get("content", []), accepted)) if role == "user" else "Agent"), text
            continue
        call = codex_conductor_call(entry_type, payload)
        if call is None:
            continue
        call_id, tool, arguments = call
        if isinstance(call_id, str) and call_id in seen_call_ids:
            continue
        send = conductor_send(tool, arguments)
        if send is None:
            continue
        # Mark the call seen only once it rendered, so a malformed first
        # representation never suppresses a valid duplicate.
        if isinstance(call_id, str):
            seen_call_ids.add(call_id)
        yield send


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
    raw = path.read_bytes()
    entries = list(parse_entries(raw))
    resolved_provider = detect_provider(entries) if provider == "auto" else provider
    if resolved_provider not in {"claude", "codex"}:
        return None

    metadata = session_metadata(path, resolved_provider, entries)
    # Render one source event at a time so multiple visible blocks retain their
    # source line/time. Deduplication remains scoped to the whole session.
    sections = []
    seen_call_ids: set[str] = set()
    for entry in entries:
        if resolved_provider == "codex":
            payload = entry.get("payload")
            call = codex_conductor_call(entry.get("type"), payload) if isinstance(payload, dict) else None
            if call and isinstance(call[0], str):
                if call[0] in seen_call_ids:
                    continue
                if conductor_send(call[1], call[2]):
                    seen_call_ids.add(call[0])
        turns = claude_turns([entry]) if resolved_provider == "claude" else codex_turns([entry])
        for block, (heading, text) in enumerate(turns):
            sections.append(f"## {heading}\n\n{turn_provenance(entry, block)}{text}\n")
    if not sections:
        return None
    source = {"provider": resolved_provider, "sessionId": metadata.session_id,
              "path": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest()}
    header = (ARCHIVE_FORMAT + "\n# Conversation reading view\n\n"
              "Source snapshot: " + json.dumps(source, ensure_ascii=True) + "\n\n"
              "Transport roles and sender text do not certify operator authorship. "
              "Turn timestamps are preserved when available; the filename uses session-start time. "
              "Tool traffic and some wrappers are omitted. Retain original evidence separately "
              "before deleting its source; this view is not a lossless archive.\n\n")
    return metadata, header + "\n---\n\n".join(sections)


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
            with out_path.open(encoding="utf-8") as existing:
                if existing.readline().strip() == ARCHIVE_FORMAT:
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
