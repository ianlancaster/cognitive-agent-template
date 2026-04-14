#!/usr/bin/env bash
#
# Extract Claude Code conversation transcripts into readable markdown.
# Usage:
#   ./scripts/extract-conversation.sh           # Extract all sessions
#   ./scripts/extract-conversation.sh [id]      # Extract specific session (forces re-extract)
#
# Outputs to conversations/ directory.
# Extracts Claude Code session transcripts into readable markdown.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$REPO_ROOT/conversations"

mkdir -p "$OUT_DIR"

# Find the Claude projects directory for this repo
# Claude Code stores conversations in ~/.claude/projects/ using a mangled path
REPO_PATH_MANGLED=$(echo "$REPO_ROOT" | sed 's|/|-|g' | sed 's|^-||')
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

  # Get the timestamp from the first message
  local timestamp
  timestamp=$(python3 -c "
import json, sys, datetime
with open('$jsonl_file') as f:
    for line in f:
        msg = json.loads(line)
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

  python3 -c "
import json, re, sys

with open('$jsonl_file') as f:
    lines = [json.loads(line) for line in f]

output = []
for msg in lines:
    role = msg.get('role', '')
    content = msg.get('content', '')

    # Skip non-message entries
    if role not in ('human', 'assistant'):
        continue

    # Skip tool results (arrays) and empty content
    if isinstance(content, list) or not content:
        continue

    # Remove XML system tags
    content = re.sub(r'<system-reminder>.*?</system-reminder>', '', content, flags=re.DOTALL)
    content = re.sub(r'<local-command-.*?</local-command-.*?>', '', content, flags=re.DOTALL)
    content = content.strip()

    if not content:
        continue

    speaker = 'User' if role == 'human' else 'Agent'
    output.append(f'## {speaker}\n\n{content}\n')

with open('$out_file', 'w') as f:
    f.write('\n---\n\n'.join(output))
" 2>/dev/null

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
