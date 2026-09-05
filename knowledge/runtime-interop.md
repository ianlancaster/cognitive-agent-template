# Runtime Interoperability

The cognitive agent can run in Claude Code or Codex. Cognitive state is shared; only host mechanics differ.

## Shared Sources of Truth

- `CLAUDE.md` and `COGNITIVE.md` — agent behavior and cognitive architecture
- `.claude/commands/*.md` — canonical ritual bodies
- `context/`, `memory/`, `journal/`, `knowledge/`, `plans/`, and `calendar.md` — persistent state
- `conversations/` — normalized transcripts from either runtime

Never create provider-specific copies of cognitive state.

## Ritual Invocation

| Ritual | Claude Code | Codex |
|---|---|---|
| awaken | `/awaken` | `$awaken` |
| caffeinate | `/caffeinate` | `$caffeinate` |
| nap | `/nap` | `$nap` |
| sleep | `/sleep` | `$sleep` |
| meditate | `/meditate` | `$meditate` |
| research | `/research` | `$research` |
| sync | `/sync` | `$sync` |
| water cooler | `/water-cooler` | `$water-cooler` |
| gather | `/gather` | `$gather` |

When writing persistent cognitive files, use the neutral ritual names (for example, “sleep” or “the sleep ritual”) unless the invocation syntax itself matters.

## Instructions and Memory

- Claude Code loads `CLAUDE.md` directly.
- Codex loads `AGENTS.md`, which directs it to the same `CLAUDE.md` and `COGNITIVE.md` sources.
- The authoritative memory location in both runtimes is `memory/` at the repository root. Host-native memory features are not part of this cognitive system. `.codex/config.toml` disables Codex native memories for this repository.

## Subagents

When a ritual calls for a scout or consultant:

- In Claude Code, use the Agent tool. Where a lightweight scout is requested, prefer Sonnet.
- In Codex, use its subagent tools. Use a read-heavy/explorer agent or a faster available model for lightweight scouts.
- Preserve the ritual's concurrency, working-directory, read-only, and consolidation requirements.
- A provider-specific model name is a preference, not part of the cognitive state.

Peer consultation and messaging flow through the Agent Conductor's injected protocol (see `knowledge/conductor-protocol.md` for where it lives). Do not create provider-specific `consult-*` commands. Ritual-owned scouts and `/gather` participants still use the runtime's subagent mechanism.

## Additional Directories

Claude Code persists peer and Water Cooler paths in `.claude/settings.local.json`.

Codex commonly needs those paths supplied when it starts:

```bash
codex --add-dir /absolute/path/to/water-cooler --add-dir /absolute/path/to/peer-repo
```

If Codex lacks write access during a ritual, request narrowly scoped access for the configured path. Do not weaken the whole sandbox.

## Conversation Archives

Run `./scripts/extract-conversation.sh`. It detects Claude Code and Codex transcripts, omits most tool traffic and enumerated host wrappers, and writes a normalized reading view with source references and per-turn provenance to `conversations/`.

This reading view is not a lossless authority archive. User-role transport does not prove human authorship; incoming sender labels are claims until joined to Conductor receipts. Session filenames use session-start time, not every turn's date. Original transcript paths and hashes support targeted verification; preserve needed raw evidence separately before deleting its source, using an appropriate private store rather than blindly committing tool output or secrets.

Optional forms:

```bash
./scripts/extract-conversation.sh --provider claude
./scripts/extract-conversation.sh --provider codex
./scripts/extract-conversation.sh --transcript /absolute/path/to/session.jsonl
./scripts/extract-conversation.sh SESSION_ID
```

## Runtime-Neutral Language

“Agent,” “main agent,” “subagent,” and “runtime” refer to either host. A canonical ritual may retain Claude-specific instructions when they are required to preserve Claude behavior; Codex follows the mapping in this document at those points.
