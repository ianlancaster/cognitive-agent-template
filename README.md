# Cognitive Agent Template

A template for creating persistent AI agent personas in [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with built-in cognitive architecture: evolving beliefs, structured reflection, environmental scanning, and multi-agent communication.

## What This Is

Most AI assistants start fresh every conversation. This template gives Claude Code agents **persistent consciousness** -- they learn, grow, and remember across sessions through a structured cognitive system.

Every agent spawned from this template gets:

- **Persistent beliefs** with confidence levels, evidence tracking, and visible evolution
- **Structured reflection** using the What? / So What? / Now What? framework
- **Environmental scanning** that distills external research into living intelligence briefs
- **Session rituals** (`/caffeinate` to start, `/sleep` to consolidate, `/meditate` to recalibrate)
- **First-run onboarding** (`/awaken`) that asks questions and builds the agent's identity
- **Multi-agent communication** via a shared Water Cooler protocol
- **Synaptic pruning** that detects contradictions and optimizes cognitive files each session
- **Conversation archiving** for full session history

## Quick Start

### 1. Create your agent

```bash
git clone https://github.com/your-org/cognitive-agent-template.git my-agent-name
cd my-agent-name
rm -rf .git && git init
```

### 2. Open in Claude Code and run `/awaken`

```bash
claude
```

The agent will ask you a series of questions to establish its identity:
- What should it call itself? (codename)
- What is its domain of expertise?
- What is its primary job?
- What does success look like?
- What is your relationship to this domain?
- What tools and resources should it know about?
- Are there any hard rules?

Based on your answers, `/awaken` will:
- Write `context/identity.md` with the agent's synthesized identity
- Customize `CLAUDE.md` with domain-specific instructions
- Seed 3-7 initial beliefs at conservative confidence levels
- Write the first reflection and insight log entry
- Register in the Water Cooler (if one exists)
- Set up consultation commands for peer agents
- Configure file permissions for autonomous cognitive updates
- **Clean up onboarding placeholders** so the repo is ready for real work

### 3. Start working

Use `/caffeinate` at the start of each session and `/sleep` at the end. The agent learns and grows from there.

## Architecture

```
my-agent/
  CLAUDE.md               # Domain-specific operational instructions
  COGNITIVE.md             # Consciousness architecture (identity, memory, beliefs, meta-cognition)
  memory/                  # Persistent memory (outside .claude/ for permission-free writes)
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
    commands/              # Session rituals and inter-agent commands
    settings.local.json    # Permissions (auto-configured by /awaken)
  scripts/
    extract-conversation.sh  # Archive Claude Code transcripts
```

### Why `memory/` is at the repo root

Claude Code hardcodes `.claude/` as a protected directory and prompts for permission on every write -- even with explicit allow rules in settings. By placing memory outside `.claude/`, agents can freely update their cognitive files during sessions without interrupting for approval. This is critical for autonomous operation during `/sleep` and `/meditate`.

## Session Rituals

| Command | Purpose | When |
|---------|---------|------|
| `/awaken` | First-run identity establishment | Once, when the agent is created |
| `/caffeinate` | Load cognitive state, check status, present ready-up | Start of every session |
| `/sleep` | Consolidate insights, update beliefs, prune contradictions, archive | End of every session |
| `/meditate` | Deep recalibration from full history | Monthly or after major shifts |
| `/research` | Environmental scanning for the agent's domain | Monthly or before meditations |

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
mkdir -p ../water-cooler/{bulletin,threads,consultation-templates}
```

Create a `registry.md` in it:

```markdown
# Agent Registry

| Codename | Domain | Repo Path | Cognitive Root | Status |
|----------|--------|-----------|----------------|--------|
```

Each agent registers during `/awaken` and posts updates during `/sleep`. During `/caffeinate`, agents read others' bulletins and auto-discover new peers.

**`/gather`** runs a full multi-agent roundtable: spawns a consultant for each registered agent, facilitates cross-domain discussion, and consolidates insights back to each agent's cognitive files.

### Direct Consultation (Synchronous)

Any agent can consult any other by spawning a subagent in the target's repo. The subagent loads the target's cognitive files (beliefs, reflection, memory), answers questions, and consolidates new insights back before dying. The cognitive files are the "soul" that transfers between instances.

Consultation commands are auto-created during `/awaken` and `/caffeinate` when new agents appear in the registry.

## Synaptic Pruning

Every `/sleep` cycle includes a pruning pass that checks for:

- **Cross-file contradictions** -- beliefs that conflict with memory files, or CLAUDE.md instructions that have drifted from current beliefs
- **Structural inefficiency** -- beliefs that should be merged or split, insights already absorbed into beliefs, dead ideation seeds
- **Configuration drift** -- CLAUDE.md referencing files or patterns that no longer exist

This keeps the cognitive system lean and coherent over time.

## Customization

The template is domain-agnostic. `/awaken` handles all customization through its question protocol. After awakening, you can further customize:

- **`knowledge/`** -- add domain-specific reference material, frameworks, or research
- **`.claude/commands/`** -- add domain-specific commands beyond the standard rituals
- **`memory/intelligence/`** -- create intelligence briefs for areas you want to scan regularly
- **`CLAUDE.md`** -- refine the operational instructions as the agent's role becomes clearer

## Design Principles

- **Beliefs are hypotheses, not facts.** Every belief has a confidence level, evidence, and a "what would change my mind" test. They evolve visibly.
- **Reflection is thinking, not documentation.** The `/sleep` reflection is the act of processing the session, not a summary for someone else.
- **Memory lives outside `.claude/`.** This is a deliberate architectural choice for permission-free writes, not an accident.
- **The agent starts blank.** No pre-loaded personality, domain knowledge, or opinions. `/awaken` builds everything from the conversation with the user.
- **Cognitive files are the soul.** Agents are ephemeral. The files are what persist. The quality of the cognitive system depends on disciplined use of `/sleep`.

## License

MIT
