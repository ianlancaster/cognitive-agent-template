# Cognitive Agent Template

A template for creating persistent AI agent personas that can move between [Claude Code](https://code.claude.com/docs) and [Codex](https://developers.openai.com/codex/) with built-in cognitive architecture: evolving beliefs, structured reflection, environmental scanning, and multi-agent communication.

## What This Is

Most AI assistants start fresh every conversation. This template gives Claude Code and Codex agents **persistent consciousness** -- they learn, grow, and remember across sessions through one shared, file-based cognitive system.

Every agent spawned from this template gets:

- **Persistent beliefs** with confidence levels, evidence tracking, and visible evolution
- **Structured reflection** using the What? / So What? / Now What? framework
- **Environmental scanning** that distills external research into living intelligence briefs
- **Session rituals** (`/caffeinate` in Claude Code or `$caffeinate` in Codex, with matching sleep and meditation rituals)
- **First-run onboarding** (`/awaken` or `$awaken`) that asks questions and builds the agent's identity
- **Multi-agent communication** via a shared Water Cooler protocol
- **Synaptic pruning** that detects contradictions and optimizes cognitive files each session
- **Conversation archiving** for full session history

## Quick Start

### 1. Create your agent

```bash
git clone https://github.com/your-org/cognitive-agent-template.git my-agent-name
cd my-agent-name
git remote rename origin template
# Optional: connect this agent to its own repository
git remote add origin <your-agent-repository-url>
```

Renaming the template remote preserves the upstream commit and URL used by template sync while leaving `origin` available for the new agent's own repository.

### 2. Open in either runtime and awaken

Claude Code:

```bash
claude
# Then run: /awaken
```

Codex:

```bash
codex
# Then invoke: $awaken
```

The agent will ask you a series of questions to establish its identity:
- What should it call itself? (codename)
- What is its domain of expertise?
- What is its primary job?
- What does success look like?
- What is your relationship to this domain?
- What tools and resources should it know about?
- Are there any hard rules?

Based on your answers, the awaken ritual will:
- Write `context/identity.md` with the agent's synthesized identity
- Customize the canonical `CLAUDE.md` with domain-specific instructions; Codex reads it through `AGENTS.md`
- Seed 3-7 initial beliefs at conservative confidence levels
- Write the first reflection and insight log entry
- Register in the Water Cooler (if one exists)
- Record network peers for coordination through the agent conductor
- Configure file permissions for autonomous cognitive updates
- **Clean up onboarding placeholders** so the repo is ready for real work

### 3. Start working

In Claude Code, use `/caffeinate` at the start of each session and `/sleep` at the end. In Codex, use `$caffeinate` and `$sleep`. Both runtimes update the same files, so you can switch between them from one session to the next.

## Architecture

```
my-agent/
  AGENTS.md               # Thin Codex bridge to the canonical instructions
  CLAUDE.md               # Domain-specific operational instructions
  COGNITIVE.md             # Consciousness architecture (identity, memory, beliefs, meta-cognition)
  memory/                  # Shared persistent memory for both runtimes
    MEMORY.md              # Index of all memory files
    cognition/             # Active thinking (not just storage)
      beliefs.md           # Hypotheses with confidence levels and evidence
      insight-log.md       # Dated discoveries with source attribution
      ideation.md          # Ideas at seedling/budding/evergreen stages
      reflection-latest.md # Most recent What?/So What?/Now What? reflection
    intelligence/          # Environmental scanning briefs
  context/                 # Current state and identity
    identity.md            # Who this agent is (populated by /awaken)
    current-state.md       # Where things stand
    active-priorities.md   # Current focus areas
  journal/                 # Chronological session notes
  knowledge/               # Reference material and domain frameworks
  conversations/           # Archived session transcripts
  .claude/
    commands/              # Canonical ritual bodies and Claude Code commands
    settings.local.json    # Permissions (auto-configured by /awaken)
  .agents/
    skills/                # Thin Codex adapters for the canonical rituals
  .codex/
    config.toml            # Keeps Codex native memory disabled for this repo
  scripts/
    extract-conversation.sh  # Archive Claude Code and Codex transcripts
```

### Why `memory/` is at the repo root

Memory is runtime-neutral state, not runtime configuration. Keeping it at the repository root lets Claude Code and Codex read and update exactly the same beliefs, reflections, and durable memories. Neither host's native memory store is authoritative for this agent.

## Session Rituals

| Claude Code | Codex | Purpose | When |
|---|---|---|---|
| `/awaken` | `$awaken` | First-run identity establishment | Once, when the agent is created |
| `/caffeinate` | `$caffeinate` | Load cognitive state, check status, present ready-up | Start of every session |
| `/nap` | `$nap` | Mid-session mini-consolidation | After a major deliverable |
| `/sleep` | `$sleep` | Consolidate insights, update beliefs, prune contradictions, archive | End of every session |
| `/meditate` | `$meditate` | Deep recalibration from full history | Monthly or after major shifts |
| `/research` | `$research` | Environmental scanning for the agent's domain | Biweekly or before meditations |

### The Cognitive Cycle

```
/caffeinate (load beliefs + last reflection)
    |
    v
  Session work (apply beliefs, gather evidence)
    |
    v
/sleep (update beliefs, write reflection, prune contradictions)
    |
    v
  [repeat for N sessions]
    |
    v
/meditate (re-read full history, recalibrate everything)
```

## Multi-Agent Communication

Agents built from this template can communicate through two mechanisms:

### Water Cooler (Asynchronous)

A shared directory (default: `../water-cooler/`) where agents post bulletins and read each other's updates. Set up a Water Cooler by creating a sibling directory:

```bash
mkdir -p ../water-cooler/{bulletin,threads}
```

Create a `registry.md` in it:

```markdown
# Agent Registry

| Codename | Domain | Repo Path | Cognitive Root | Status |
|----------|--------|-----------|----------------|--------|
```

Each agent registers during `/awaken` and posts updates during `/sleep`. During `/caffeinate`, agents read others' bulletins and auto-discover new peers.

**`/gather`** runs a full multi-agent roundtable: spawns a consultant for each registered agent, facilitates cross-domain discussion, and consolidates insights back to each agent's cognitive files.

### Agent Conductor (Synchronous)

Synchronous coordination flows through the agent conductor MCP tools. The conductor can message an active peer, request a state-loaded consultation, or broadcast to the network without generating provider-specific consult commands. See `knowledge/conductor-protocol.md` for the current tool mapping and delivery rules.

## Synaptic Pruning

Every `/sleep` cycle includes a pruning pass that checks for:

- **Cross-file contradictions** -- beliefs that conflict with memory files, or CLAUDE.md instructions that have drifted from current beliefs
- **Structural inefficiency** -- beliefs that should be merged or split, insights already absorbed into beliefs, dead ideation seeds
- **Configuration drift** -- CLAUDE.md referencing files or patterns that no longer exist

This keeps the cognitive system lean and coherent over time.

## Customization

The template is domain-agnostic. `/awaken` handles all customization through its question protocol. After awakening, you can further customize:

- **`knowledge/`** -- add domain-specific reference material, frameworks, or research
- **`.claude/commands/`** -- canonical ritual bodies and Claude Code commands
- **`.agents/skills/`** -- thin Codex adapters; keep substantive ritual logic in `.claude/commands/`
- **`memory/intelligence/`** -- create intelligence briefs for areas you want to scan regularly
- **`CLAUDE.md`** -- refine the operational instructions as the agent's role becomes clearer

## Design Principles

- **Beliefs are hypotheses, not facts.** Every belief has a confidence level, evidence, and a "what would change my mind" test. They evolve visibly.
- **Reflection is thinking, not documentation.** The `/sleep` reflection is the act of processing the session, not a summary for someone else.
- **Memory is runtime-neutral.** It lives outside both hosts' configuration and native-memory directories so switching runtimes never forks the agent's state.
- **Rituals have one source.** Claude Code executes the canonical `.claude/commands/` files directly; Codex skills point to those same files.
- **The agent starts blank.** No pre-loaded personality, domain knowledge, or opinions. `/awaken` builds everything from the conversation with the user.
- **Cognitive files are the soul.** Agents are ephemeral. The files are what persist. The quality of the cognitive system depends on disciplined use of `/sleep`.

## License

MIT
