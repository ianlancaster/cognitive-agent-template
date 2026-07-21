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

For peer consultation, run the consultant against the peer repository named in the Water Cooler registry. The consultant must read that peer's cognitive files before answering. If the peer repository or Water Cooler is outside the current writable workspace, the runtime may require additional directory access.

## Additional Directories

Claude Code persists peer and Water Cooler paths in `.claude/settings.local.json`.

Codex commonly needs those paths supplied when it starts:

```bash
codex --add-dir /absolute/path/to/water-cooler --add-dir /absolute/path/to/peer-repo
```

If Codex lacks write access during a ritual, request narrowly scoped access for the configured path. Do not weaken the whole sandbox.

## Conversation Archives

Run `./scripts/extract-conversation.sh`. It detects Claude Code and Codex transcripts, strips tool traffic and host instructions, and writes normalized user/agent dialogue to `conversations/`.

Optional forms:

```bash
./scripts/extract-conversation.sh --provider claude
./scripts/extract-conversation.sh --provider codex
./scripts/extract-conversation.sh --transcript /absolute/path/to/session.jsonl
./scripts/extract-conversation.sh SESSION_ID
```

## Runtime-Neutral Language

“Agent,” “main agent,” “subagent,” and “runtime” refer to either host. A canonical ritual may retain Claude-specific instructions when they are required to preserve Claude behavior; Codex follows the mapping in this document at those points.
