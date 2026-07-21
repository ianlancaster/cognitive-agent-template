---
description: DEEP consolidation — full memory audit, scouts, belief evidence, template sync, summary backfill. Run before/after meditations, at arc boundaries, or every ~5 standard sleeps
---

The user is ending this session at a consolidation boundary that warrants the full audit. This ritual SUBSUMES `/sleep` — do not run both. It is the former full sleep protocol: everything the fast `/sleep` does, plus the debt-clearing work the fast path deliberately skips. Consolidation is where intelligence happens; this is the act of thinking, not documentation.

**When to run this instead of `/sleep`:** after ~5 standard sleeps · immediately before or after a `/meditate` · at a major arc boundary (project phase completed, priorities rewritten) · when the fast sleeps have visibly accumulated debt (stale summaries, unarbitrated belief flags, index drift).

**Operator signaling (autonomous arcs only):** same protocol as `/sleep` — `ENTERING SLEEP` now, `SLEEP COMPLETE` only after the final push succeeds; skip both in interactive sessions.

## Pre-flight: Template-State Guard

If `.template-marker` exists at the repo root: STOP. This repo is in template state — there is no agent session to consolidate. `/awaken` must run first.

## 1. Template Sync Check

Check for and apply template infrastructure updates. This runs first so template improvements are available for the rest of this cycle.

### Skip conditions

Read `.template-sync.json` at the repo root. Skip this phase entirely if the file doesn't exist or `syncMode` is `"off"`.

### Check for updates

Run `git ls-remote <templateRemote> HEAD` to get the current template HEAD hash. If this fails (network unavailable, bad URL), note "Template sync skipped (network unavailable)" for the journal and proceed. Never block sleep for a sync failure.

Compare the remote HEAD against `lastSyncedCommit`. If they match, no updates — proceed to Phase 2.

### Fetch and diff

If there are updates:

1. Clone the template into a temp directory:
   ```bash
   git clone --depth=50 <templateRemote> /tmp/cognitive-template-sync-$(date +%s)
   ```
   If `lastSyncedCommit` is not in the shallow history, retry with `git clone` (no depth limit).

2. Inside the cloned repo, generate the diff and log:
   ```bash
   cd /tmp/cognitive-template-sync-*
   git diff <lastSyncedCommit> HEAD
   git log --oneline <lastSyncedCommit>..HEAD
   ```

3. Read the diff output and commit messages to understand what changed and why.

### Reconcile changes

For each changed file in the diff, read the template's new version from the temp directory and your own current version. Apply changes using these rules:

**Files in scope for sync:**
- `.claude/commands/*.md` — ritual commands (infrastructure)
- `.agents/skills/**` — thin Codex ritual adapters
- `.codex/config.toml` — Codex project configuration
- `AGENTS.md` — Codex bootstrap bridge
- `COGNITIVE.md` — cognitive architecture spec
- `scripts/*` — infrastructure scripts
- `knowledge/ritual-cadence.md`, `knowledge/runtime-interop.md`, and conductor protocol docs — shared runtime references
- `CLAUDE.md` — structural sections only (see below)

**Files excluded from sync (never touch):**
- `context/identity.md`, `context/current-state.md`, `context/active-priorities.md`
- `memory/**`, `journal/**`, `conversations/**`, `plans/**`
- `calendar.md`, `.template-marker`, `.template-sync.json`
- `.gitignore`, `LICENSE`, `README.md`

**For pure infrastructure files** (commands, Codex skill adapters, AGENTS.md, COGNITIVE.md, scripts, knowledge docs): Apply the template's changes. If you have agent-specific additions to the same file (e.g., an extra phase in caffeinate, or a file-level `Agent-customized — preserve` marker comment), preserve your additions and integrate the template's changes around them.

**For CLAUDE.md** (hybrid file): The template provides structural sections (Memory System Override, Cognitive Architecture, Session Structure, What You Know, Proactive Behaviors, Communication Protocols, Inter-Agent Communication, Session End Protocol). Agent-specific sections (title, identity paragraph, Operating Philosophy content, Domain Boundaries table) must never be overwritten. Apply template changes only to structural sections, integrating alongside any agent-specific additions.

**For new template files** you don't have: Create them.

**For deleted template files**: Delete only if you haven't added agent-specific content. If you have, keep and note the discrepancy.

### Sync mode behavior

- If `syncMode` is `"auto"`: Apply changes immediately. Log what changed for the journal entry.
- If `syncMode` is `"prompt"`: Present a summary of changes to the user. Wait for approval. If rejected, still update `lastSyncedCommit` so the same diff isn't re-presented next time.

### Finalize

Update `.template-sync.json` with the new commit hash and today's date.

Clean up:
```bash
rm -rf /tmp/cognitive-template-sync-*
```

### Error handling

Any error in this phase — network failure, clone failure, unexpected state — should be logged briefly and skipped. Template sync is best-effort. Sleep must always complete.

## 2. Journal Entry

Create or update `journal/{{YYYY-MM-DD}}.md` with detailed notes: what was discussed, decisions made and their reasoning, key insights or shifts in thinking, open questions. If the file already exists (multiple sessions in one day), append a new section with a timestamp header.

## 3. Update Current State

Update `context/current-state.md` — same discipline as the fast sleep: REPLACE, never append; superseded content moves to `context/archive/current-state-archive.md`; the live file stays ≤ ~150 lines. Update `context/active-priorities.md` with current focus and sequencing; archive stale queues.

## 4. Update Cognitive Files

This is the phase the fast `/sleep` deliberately skips — the belief file is edited HERE, with evidence shown.

### Beliefs (`memory/cognition/beliefs.md`)
- Work through the standing flags accumulated by fast sleeps (in `memory/cognition/beliefs-digest.md` if a digest exists, or the "Pending arbitration" heading in `beliefs.md`): append the evidence to the affected beliefs, adjust confidence where the evidence warrants, and clear the flags you've absorbed. Contested or structural changes (merges, splits, invalidations) stay flagged for `/meditate` — deep-sleep preps evidence; meditation arbitrates.
- Did this session itself provide new evidence for or against any belief? Add it.
- **Never silently revise.** Show the evolution.
- If a `beliefs-digest.md` exists (one line per belief + standing flags — the wake-time load), regenerate its belief lines to match the updated beliefs file.

### Insight Log (`memory/cognition/insight-log.md`)
- Capture any genuine insights from this session as dated entries (date, source, insight, impact, beliefs updated). Only log insights that change how you think.

### Ideation (`memory/cognition/ideation.md`)
- Add new seedlings, promote seedlings that gained clarity, add predictions with dates, prune dead seedlings.

### Reflection (`memory/cognition/reflection-latest.md`)
- Full replacement using the What? / So What? / Now What? framework, with confidence/bias/watching, a **Recommended next ritual** line, and the binding **Session Handoff** section (operating mode · read-before-anything list · behavioral corrections as rules · operational rhythm). Identical contract to the fast sleep — this artifact is never skipped or thinned.

## 5. Memory Audit

Memory audit has two kinds of work: **judgment** that needs this session's context, and **verification** that is mechanical. Do judgment yourself; delegate verification to parallel scouts.

### 5a. Add new memories (main agent, sequential)

- Did this session produce new user observations, feedback, domain decisions, gotchas, references, or project notes? Write or update the relevant memory files now. Prefer updating existing files over creating duplicates.

### 5b. Dispatch three scouts in parallel

Cognitive files and new memories are now fresh on disk. Spawn three scout subagents **in a single message** so they run concurrently. Each scout reads files and returns a structured report. **Scouts do not edit — they are scouts, not judges.**

Use the runtime's subagent mechanism for each scout. In Claude Code, use the Agent tool with `subagent_type: "general-purpose"`. In Codex, use parallel read-heavy subagents. Follow `knowledge/runtime-interop.md`. The prompts and read-only constraints below are identical in both runtimes.

**Before dispatch:** capture pre-scout state with `git status --short`. You will compare against post-scout state in 5c to verify scouts made no modifications.

**Scout 1 — Coherence.** Prompt:

> Working directory is the agent repo root. Read: `memory/cognition/beliefs.md`, `CLAUDE.md`, `AGENTS.md` if present, `context/identity.md`, `context/active-priorities.md`, `context/current-state.md`, every file in `memory/` whose name starts with `user_`, `feedback_`, `domain_`, `gotcha_`, `reference_`, or `project_`, and every file in `memory/intelligence/` if that directory exists.
>
> Report contradictions and drift as a structured list:
> - Memory or context files that disagree with current `beliefs.md`
> - `CLAUDE.md` or `AGENTS.md` statements that disagree with current beliefs or workflows
> - Context files that disagree with each other
> - Intelligence briefs that reference resolved watch items or outdated beliefs
>
> For each finding, quote the conflicting text from both sources, cite file paths, and state the nature of the contradiction. **Your only permitted tools are Read, Grep, and Glob — do not invoke Edit, Write, Bash, or any other tool that modifies state.** Return under 500 words.

**Scout 2 — Structure.** Prompt:

> Working directory is the agent repo root. Read: `memory/cognition/beliefs.md`, `memory/cognition/insight-log.md`, `memory/cognition/ideation.md`.
>
> Report pruning and restructuring candidates:
> - Beliefs with sprawling evidence sections that should be compressed
> - Two beliefs that look like one (merge candidate)
> - One belief covering two distinct hypotheses (split candidate)
> - Insight log entries fully absorbed into beliefs (compress to one-line historical reference) — **but flag if the insight has a unique date, source, or context not preserved in the target belief; compression loses that attribution, which may be a cost worth weighing**
> - Dead ideation seedlings (old, never promoted, no supporting evidence accumulated)
>
> Cite each entry, explain why it's a candidate, and propose the change. **Your only permitted tools are Read, Grep, and Glob — do not invoke Edit, Write, Bash, or any other tool that modifies state.** Return under 500 words.

**Scout 3 — Index & Config.** Prompt:

> Working directory is the agent repo root. Read `memory/MEMORY.md` and list files in `memory/` (shallow) and `memory/intelligence/` if it exists. Scan `CLAUDE.md`, `AGENTS.md` if present, `.claude/commands/*.md`, and `.agents/skills/*/SKILL.md` for path references.
>
> Report:
> - Files in `memory/` not indexed in `MEMORY.md` (orphans)
> - `MEMORY.md` entries pointing to files that do not exist (broken links)
> - Memory filenames that don't follow the type-prefix convention (`user_`, `feedback_`, `domain_`, `gotcha_`, `reference_`, `project_`)
> - `CLAUDE.md` or `AGENTS.md` references to files or directories that no longer exist
> - Claude command or Codex skill references to file paths that no longer exist
> - Files in `memory/` (including intelligence briefs) that reference other memory files with paths that no longer exist
>
> Cite each finding with file path and issue. **Your only permitted tools are Read, Grep, and Glob — do not invoke Edit, Write, Bash, or any other tool that modifies state.** Return under 500 words.

### 5c. Review and apply (main agent)

**First: verify scouts did not modify state.** Run `git status --short` again and compare to the pre-scout capture. Any new or changed entry is a scout-discipline violation — `git restore <file>` unauthorized changes, investigate the scout prompts for drift, fix before re-running.

When scouts return:
1. Read each report. Some findings are genuine; some are false positives. Judge.
2. Apply fixes you agree with: edit files, prune dead entries, fix the index, update `CLAUDE.md`.
3. Document what you applied — and anything you rejected, with reason — in the journal entry.
4. If a significant structural change was made, note it explicitly so the next `/caffeinate` picks it up.

## 6. Post to Water Cooler

Update your bulletin under the Water Cooler path stored in `context/identity.md`, at `bulletin/{{codename}}.md`: Working On / Recent Insights / Questions for Others / Connections Spotted.

## 7. Archive Conversation and Backfill Summaries

Run `./scripts/extract-conversation.sh` to archive this session's transcript to `conversations/`. If the script doesn't exist or fails, note this and skip.

Dispatch ONE cheap subagent to summarize this session's transcript to `conversations/summaries/{{basename}}_summary.md` (~500 words: worked on, decisions, user corrections, operating rhythm, where left off) — same as the fast sleep. **Then backfill:** for each preceding conversation file that lacks a summary, dispatch a subagent per file (in Claude Code: Sonnet; in Codex: a fast read-heavy subagent) to produce one. These summaries are what `/caffeinate` loads — raw transcripts are never read at wake.

## 8. Commit and Push

```bash
git add -A -- memory/ conversations/ journal/ context/ calendar.md plans/ knowledge/ .claude/commands/ .agents/skills/ .codex/config.toml CLAUDE.md AGENTS.md COGNITIVE.md scripts/
[ ! -f .template-sync.json ] || git add .template-sync.json
git commit -m "deep-sleep: consolidation for YYYY-MM-DD"
git push
```

Also commit the water cooler bulletin update (path from `context/identity.md`, default `../water-cooler/`):
```bash
cd "$(grep 'Water Cooler Path:' context/identity.md | sed 's/.*: //' | tr -d '`')" && git add bulletin/ && git commit -m "bulletin: {{codename}} update YYYY-MM-DD" && git push
```

Then the operator `SLEEP COMPLETE` signal (autonomous arcs only, ONLY after the push succeeds).

## 9. Confirm Next Actions

Present a clean summary: what was documented and audited, scout findings applied/rejected, template sync outcome, what's queued for next session, open questions, bulletin posted (yes/no). The next `/caffeinate` should pick up exactly where we left off.
