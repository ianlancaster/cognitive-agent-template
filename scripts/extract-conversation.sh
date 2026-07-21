#!/usr/bin/env bash
# Normalize Claude Code and Codex session transcripts into concise Markdown.
# Existing usage remains supported:
#   ./scripts/extract-conversation.sh
#   ./scripts/extract-conversation.sh SESSION_ID

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/extract_conversation.py" "$@"
