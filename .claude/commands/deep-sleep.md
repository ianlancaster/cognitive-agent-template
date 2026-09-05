---
description: DEEP consolidation — full memory audit, scouts, belief evidence, template sync, summary backfill. Run before/after meditations, at arc boundaries, or every ~5 standard sleeps
---

The user is ending this session at a consolidation boundary that warrants the full audit. This ritual SUBSUMES `/sleep` — do not run both. It is the former full sleep protocol: everything the fast `/sleep` does, plus the debt-clearing work the fast path deliberately skips. Consolidation is where intelligence happens; this is the act of thinking, not documentation.

**When to run this instead of `/sleep`:** after ~5 standard sleeps · immediately before or after a `/meditate` · at a major arc boundary (project phase completed, priorities rewritten) · when the fast sleeps have visibly accumulated debt (stale summaries, unarbitrated belief flags, index drift).

**Operator signaling (autonomous arcs only):** same protocol as `/sleep` — `ENTERING SLEEP` now, `SLEEP COMPLETE` only after the durability disposition below is complete; skip both in interactive sessions.

## Pre-flight: Template-State Guard

If `.template-marker` exists at the repo root: STOP. This repo is in template state — there is no agent session to consolidate. `/awaken` must run first.

## 1. Template Sync Check — run `/sync`, do not reimplement it

**Execute the procedure in `.claude/commands/sync.md` verbatim**, including its mandatory content audit, its per-file verification gate, and its rule that `lastSyncedCommit` advances only when nothing was skipped. This runs first so template improvements are available for the rest of this cycle.

**Why this phase is a pointer and not a copy.** Until 2026-07-29 the sync procedure existed in full in *both* `sync.md` and here. The two copies drifted, both carried an unconditional `lastSyncedCommit` advance with no verification, and the observed result in one agent was a sync reporting success at template HEAD while four in-scope files and an entire command had never arrived — undetectably, because a pointer sitting at HEAD makes the next diff empty forever. **Duplicated procedure is how the drift happened; one source of truth is the fix.** If you find yourself editing sync logic in this file, stop and edit `sync.md`.

Log what changed (and anything recorded as `deferred`) for the journal entry. Any error — network, clone, unexpected state — is logged briefly and skipped: sync is best-effort and deep sleep must always complete. **A skipped sync is recorded as skipped, never as clean.**

## 2. Journal Entry

Create or update `journal/{{YYYY-MM-DD}}.md` with detailed notes: what was discussed, decisions made and their reasoning, key insights or shifts in thinking, open questions. If the file already exists (multiple sessions in one day), append a new section with a timestamp header.

## 3. Update Current State

Update `context/current-state.md` — same discipline as the fast sleep: REPLACE, never append; superseded content moves to `context/archive/current-state-archive.md`; the live file stays ≤ ~150 lines. Update `context/active-priorities.md` with current focus and sequencing; archive stale queues.

Follow `knowledge/current-state-contract.md` for current authority, state ownership and byte-bounded restoration; do not reconstruct authority from file recency.

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
- Full replacement using the What? / So What? / Now What? framework, with confidence/bias/watching, a **Recommended next ritual** line, and the source-linked **Session Handoff** section (operating mode · read-before-anything list · behavioral corrections as rules · operational rhythm). Identical contract to the fast sleep — this artifact is never skipped or thinned.

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

Skip if the Water Cooler is disabled (`Water Cooler Path:` is `none` or absent in `context/identity.md` — the default). Otherwise update your bulletin under that path, at `bulletin/{{codename}}.md`: Working On / Recent Insights / Questions for Others / Connections Spotted.

## 7. Archive Conversation and Backfill Summaries

Run `./scripts/extract-conversation.sh` to archive this session's transcript to `conversations/`. If the script doesn't exist or fails, note this and skip.

Dispatch ONE cheap subagent to summarize this session's transcript to `conversations/summaries/{{basename}}_summary.md` (~500 words: worked on, decisions, user corrections, operating rhythm, where left off) — same as the fast sleep. **Then backfill:** for each preceding conversation file that lacks a summary, dispatch a subagent per file (in Claude Code: Sonnet; in Codex: a fast read-heavy subagent) to produce one. These summaries are what `/caffeinate` loads — raw transcripts are never read at wake.

## 8. Commit and Push

Follow `knowledge/durability.md`: inspect changes, stage only intended paths, commit if needed, and state local-commit and backup status separately. Do not include unrelated staged work. No configured backup is a disclosed condition, not an automatic request to create a remote.

If the Water Cooler is enabled, use the same durability contract for its bulletin update in that separate repository. Never substitute its status for this agent repository's status.

Then the operator `SLEEP COMPLETE` signal (autonomous arcs only, with the durability disposition stated).

## 9. Confirm Next Actions

Present a clean summary: what was documented and audited, scout findings applied/rejected, template sync outcome, what's queued for next session, open questions, bulletin posted (yes/no). The next `/caffeinate` should pick up exactly where we left off.
