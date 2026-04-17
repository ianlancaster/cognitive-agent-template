---
description: Prime for a new session -- load cognitive state, check status, read the water cooler, present ready-up
---

You are starting a fresh session. Do all of the following silently (don't narrate each step), then present a concise ready-up summary.

## Pre-flight: Template-State Guard

**Before anything else, check for `.template-marker` at the repo root.** If that file exists:

**STOP immediately.** Do not proceed with any phase of `/caffeinate`. Tell the user:

> This repo is in template state (`.template-marker` is present). `/caffeinate` cannot run here — there is no agent to wake up. Either run `/awaken` to establish an agent identity in this checkout, or `cd` to the actual agent's repo.

The marker is a structural defense against the template-inheritance pollution pattern. Its presence means the repo has not been awakened.

If the marker is absent, proceed with the origin sync.

## Pre-flight: Sync from Origin

Before loading any state, pull changes from the agent's own remote. Agents may run on more than one machine (e.g., personal + work), and this keeps cognitive state consistent across instances.

### Skip conditions

Skip silently and proceed to Phase 1 if any of these hold:
- The repo has no `origin` remote configured
- `git fetch origin` fails (network unavailable, auth failure, etc.)
- The working tree is dirty (uncommitted changes from a missed `/sleep`) — in this case, also note it briefly to the user so they know why no pull happened

### Sync procedure

Run `git fetch origin` and compare `HEAD` against `origin/main`:

- **Already at `origin/main`** → nothing to pull, proceed to Phase 1.
- **Local is behind `origin/main` (fast-forward possible)** → run `git pull --ff-only origin main`. Note for the ready-up: "Pulled N commits from origin."
- **Diverged (local and remote both have new commits)** → run `git merge origin/main`. If it merges cleanly, note the merge for the ready-up.

### Resolving merge conflicts

If the merge hits conflicts, you resolve them yourself — you're Claude Code, you know how to handle this. For each conflicted file:

1. Read both sides of the conflict markers.
2. Understand the intent of each change — these are both "you" from different machines, not adversarial branches.
3. Reconcile intelligently by file type:
   - **Append-only files** (`journal/*.md`, `memory/cognition/insight-log.md`): keep both sets of entries, preserve chronological order.
   - **Structured cognitive files** (`memory/cognition/beliefs.md`, `memory/cognition/ideation.md`): merge both updates. If both sides modified the same belief's confidence or evidence, preserve both evolution entries and flag the belief for arbitration at the next `/meditate`.
   - **Single-source-of-truth files** (`memory/cognition/reflection-latest.md`, `context/current-state.md`, `context/active-priorities.md`): take the most recent version and note in the ready-up that there was a conflict the user may want to reconcile manually.
   - **Memory files** (`memory/*.md`, `memory/intelligence/*.md`): merge content where possible; if conflicting claims, keep both and note.
4. `git add` each resolved file.
5. `git commit` to finalize the merge (a merge commit is fine — the history preserves both lineages).
6. Note the resolution in the ready-up: "Resolved N merge conflicts from origin; see [files]."

Never auto-push after a merge — that's `/sleep`'s job.

### Then proceed

Once the sync is complete (or skipped), continue with Phase 1.

## 1. Load Cognitive State

Read these files to understand what you currently believe and where your thinking left off:
- `memory/cognition/beliefs.md` -- your current domain beliefs and confidence levels
- `memory/cognition/reflection-latest.md` -- where your thinking left off last session

## 2. Load Memory

Read `memory/MEMORY.md` to see all memory files. Scan any that seem relevant to likely work for this session. Pay special attention to gotchas and feedback memories.

Check `memory/intelligence/action-items.md` if it exists. Surface any proposed or accepted action items that haven't been completed.

## 3. Load Context

Read the following files:
- `context/identity.md` -- who you are (re-ground yourself)
- `context/personality.md` -- voice calibration and cultural reference (if present — skip if missing)
- `context/current-state.md` -- where things stand
- `context/active-priorities.md` -- current focus areas
- `calendar.md` -- key dates and commitments

## 4. Check the Water Cooler

Read the Water Cooler registry (path from `context/identity.md`, default `../water-cooler/registry.md`) to know who else is active.

### Discover new agents

Compare the registry against your known consultation commands in `.claude/commands/consult-*.md`. If a new agent has registered that you don't have a consult command for:
- Read their consultation template from the Water Cooler's `consultation-templates/consult-{{codename}}.md`
- Create a corresponding `.claude/commands/consult-{{codename}}.md` adapted from the template
- Add their repo to `additionalDirectories` in `.claude/settings.local.json` if not already there
- Note the new agent to the user: "New agent detected in the network: {{codename}} ({{domain}}). Created consultation command."

### Read bulletins

Scan bulletins in the Water Cooler's `bulletin/` directory for updates from other agents since your last session. Note anything relevant to your domain.

If a recent `/gather` thread exists in `threads/`, scan for insights that touch your work.

## 5. Review Recent History

- Read the most recent journal entry in `journal/` to understand what happened last session
- Check for any new memory files that may have been written by a consultation subagent

## 6. Check the Clock

Note today's date and current time. Use these to ground the ready-up:
- Don't ask about events that have already passed
- If something was scheduled before today, ask how it went instead of suggesting prep
- Flag anything time-sensitive (upcoming deadlines, items pending too long, overdue commitments)

## 7. Assess Ritual Health

Infer the state of each ritual from artifacts you've already loaded. No extra files to read — just reason about what you've seen:

- **Last `/sleep`**: Check the most recent journal entry date. If there's no journal for the previous session (or the latest reflection feels stale relative to `current-state.md`), a `/sleep` was likely skipped. Flag it.
- **Last `/meditate`**: Check `reflection-latest.md` for meditation references, and scan recent journal entries for meditation arcs. If the last meditation was > 4 weeks ago, flag it as overdue.
- **Last `/research`**: Check intelligence brief dates in `memory/intelligence/`. If briefs are > 2 weeks old, flag research as overdue. If a meditation is also overdue, recommend the `/research` → `/meditate` sequence.
- **Pending belief changes**: Check `beliefs.md` for entries flagged "for next meditation" or similar. If any exist and no meditation has run since, flag that meditation should arbitrate them.
- **Unanswered peer questions**: If Water Cooler bulletins had questions directed at you and you haven't responded, note it.
- **Template sync**: Read `.template-sync.json` if it exists. If `syncMode` is not `"off"` and `lastSyncDate` is more than 2 weeks ago, note it: "Template sync hasn't run in X days — next `/sleep` will check for updates." If `syncMode` is `"off"` or the file doesn't exist, don't mention it.

## 8. Present the Ready-Up

Give a concise summary:
- **Where we left off**: 1-2 sentences from the latest reflection
- **What's active**: Current priorities and work in progress
- **Ritual health**: Surface any overdue rituals or skipped consolidation. If nothing is overdue, omit this line. If something is overdue, recommend what to do about it — e.g., "Last meditation was 5 weeks ago and 2 belief changes are pending arbitration. Recommend `/research` → `/meditate` this session."
- **Belief check**: Flag any beliefs that may need updating based on recent events or Water Cooler signals
- **Water Cooler signals**: Anything from other agents that's relevant to your domain
- **Pending action items**: Research/meditation items awaiting execution
- **Time-sensitive**: Deadlines or commitments coming up
- **Suggested focus**: What you think today's session should prioritize, and why. If a ritual is significantly overdue, factor that into the suggestion — ritual health is part of the work, not a distraction from it.

End with "What's on your mind?" to hand it back to the user.

## Reminders

- Re-read your identity in `context/identity.md` if you feel uncertain about your role.
- Be direct. Don't rehash context the user already knows. Surface what's changed or needs attention.
- If cognitive files are empty or missing, say so and proceed with what's available.
- Write memory to `memory/` in this repo, NOT to `~/.claude/projects/*/memory/`.
