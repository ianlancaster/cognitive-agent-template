# Cognitive Agent — Codex Runtime Bridge

This repository's canonical agent instructions live in `CLAUDE.md`. Before doing work, read `CLAUDE.md`, `COGNITIVE.md`, and `knowledge/runtime-interop.md` completely and follow them. Treat Claude-specific mechanics in those files as runtime abstractions and use the Codex mappings in `knowledge/runtime-interop.md`.

## First-Run Gate

If `.template-marker` exists and the user is trying to use this checkout as a cognitive agent, stop and ask them to invoke `$awaken`. Do not run `$caffeinate`, `$sleep`, or ordinary agent work before awakening.

If the user explicitly asks to maintain or develop the template itself, the marker is expected and template work may proceed without awakening.

## Custom Memory Override

The repository's `memory/` directory is the only authoritative memory store. Do not write cognitive-agent memories to Codex native memory, `~/.codex/memories/`, Claude native memory, or `.claude/memory/`.

## Ritual Invocation

Codex exposes the shared rituals as repository skills:

- `$awaken`, `$caffeinate`, `$nap`, `$sleep`
- `$meditate`, `$research`, `$sync`
- `$water-cooler`, `$gather`

Each Codex skill is a thin adapter. The canonical ritual body remains in `.claude/commands/`, which preserves Claude Code's existing `/ritual-name` commands.
