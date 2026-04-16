#!/usr/bin/env bash
#
# Extract Claude Code conversation transcripts into readable markdown.
# Usage:
#   ./scripts/extract-conversation.sh           # Extract all sessions
#   ./scripts/extract-conversation.sh [id]      # Extract specific session (forces re-extract)
#
# Outputs to conversations/ directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$REPO_ROOT/conversations"

mkdir -p "$OUT_DIR"

# Find the Claude projects directory for this repo.
# Claude Code stores conversations in ~/.claude/projects/ using a mangled path:
# /Users/foo/bar becomes -Users-foo-bar (every / replaced with -, leading - preserved).
REPO_PATH_MANGLED=$(echo "$REPO_ROOT" | sed 's|/|-|g')
CLAUDE_DIR="$HOME/.claude/projects/$REPO_PATH_MANGLED"

if [ ! -d "$CLAUDE_DIR" ]; then
  echo "No Claude projects directory found at $CLAUDE_DIR"
  echo "This repo may not have any Claude Code sessions yet."
  exit 0
fi

FORCE_ID="${1:-}"

extract_session() {
  local jsonl_file="$1"
  local session_id
  session_id=$(basename "$jsonl_file" .jsonl)

  # Get the timestamp from the first entry that has one
  local timestamp
  timestamp=$(python3 -c "
import json, datetime
with open('$jsonl_file') as f:
    for line in f:
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if 'timestamp' in msg:
            dt = datetime.datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            print(dt.strftime('%Y-%m-%d_%H%M'))
            break
" 2>/dev/null || echo "unknown-date")

  local out_file="$OUT_DIR/${timestamp}_${session_id}.md"

  # Skip if already extracted (unless forced)
  if [ -f "$out_file" ] && [ -z "$FORCE_ID" ]; then
    return
  fi

  python3 - "$jsonl_file" "$out_file" <<'PYEOF'
import json, re, sys

jsonl_path, out_path = sys.argv[1], sys.argv[2]

def extract_text(content):
    """Normalize content into a single text string.

    Claude Code JSONL content is either a plain string (user commands, simple
    text) or a list of blocks with a 'type' field. Text blocks carry the
    readable content; tool_use/tool_result/thinking blocks are skipped.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text = item.get('text', '')
                if text:
                    parts.append(text)
        return '\n\n'.join(parts)
    return ''

SYSTEM_TAG_PATTERNS = [
    re.compile(r'<system-reminder>.*?</system-reminder>', re.DOTALL),
    re.compile(r'<local-command-[^>]*>.*?</local-command-[^>]*>', re.DOTALL),
    re.compile(r'<command-name>.*?</command-name>', re.DOTALL),
    re.compile(r'<command-message>.*?</command-message>', re.DOTALL),
    re.compile(r'<command-args>.*?</command-args>', re.DOTALL),
    re.compile(r'<task-notification>.*?</task-notification>', re.DOTALL),
]

def clean(text):
    for pat in SYSTEM_TAG_PATTERNS:
        text = pat.sub('', text)
    return text.strip()

output = []
with open(jsonl_path) as f:
    for line in f:
        try:
            entry = json.loads(line)
        except Exception:
            continue

        # The JSONL file has many entry types (attachment, permission-mode,
        # file-history-snapshot, tool-use, tool-result, etc). Only user and
        # assistant entries contain conversational messages.
        entry_type = entry.get('type')
        if entry_type not in ('user', 'assistant'):
            continue

        message = entry.get('message') or {}
        role = message.get('role', entry_type)
        content = message.get('content', '')

        text = extract_text(content)
        if not text:
            continue

        text = clean(text)
        if not text:
            continue

        speaker = 'User' if role == 'user' else 'Agent'
        output.append(f'## {speaker}\n\n{text}\n')

with open(out_path, 'w') as f:
    f.write('\n---\n\n'.join(output))
PYEOF

  if [ -f "$out_file" ] && [ -s "$out_file" ]; then
    echo "Extracted: $(basename "$out_file")"
  fi
}

if [ -n "$FORCE_ID" ]; then
  target="$CLAUDE_DIR/$FORCE_ID.jsonl"
  if [ -f "$target" ]; then
    extract_session "$target"
  else
    echo "Session not found: $FORCE_ID"
    exit 1
  fi
else
  for jsonl_file in "$CLAUDE_DIR"/*.jsonl; do
    [ -f "$jsonl_file" ] || continue
    extract_session "$jsonl_file"
  done
fi

echo "Done. Conversations in: $OUT_DIR"
