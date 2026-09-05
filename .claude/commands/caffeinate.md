---
description: Prime for a new session -- load cognitive state, check status, read the water cooler, present ready-up
---

You are starting a fresh session. Do all of the following silently (don't narrate each step), then present a concise ready-up summary.

**CONTEXT BUDGET (hard discipline): the wake should land at ≤ ~12-15% of the context window.** The diet is deliberate — a heavy wake steals the session's working room, and loading the RIGHT set is the work. Do not "helpfully" load beyond this protocol. Everything not loaded here is one lazy read away when a task actually needs it — that is the point of the indexes. The fidelity gradient at wake is: reflection handoff → conversation summaries → beliefs digest. Raw transcripts and full evidence files are for forensics, never for waking.

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

If the merge hits conflicts, resolve them yourself. Both supported runtimes can inspect and reconcile the repository. For each conflicted file:

1. Read both sides of the conflict markers.
2. Understand the intent of each change — these are both "you" from different machines, not adversarial branches.
3. Reconcile intelligently by file type:
   - **Append-only files** (`journal/*.md`, `memory/cognition/insight-log.md`): keep both sets of entries, preserve chronological order.
   - **Structured cognitive files** (`memory/cognition/beliefs.md`, `memory/cognition/ideation.md`): merge both updates. If both sides modified the same belief's confidence or evidence, preserve both evolution entries and flag the belief for arbitration at the next `/meditate`.
   - **Current-state files** (`memory/cognition/reflection-latest.md`, `context/current-state.md`, `context/active-priorities.md`): reconcile against cited directions and observed state using `knowledge/current-state-contract.md`. A newer file does not win by timestamp. Preserve unresolved consequential conflicts explicitly; continue independently authorized work and ask only for the decision that cannot be resolved from its source.
   - **Memory files** (`memory/*.md`, `memory/intelligence/*.md`): merge content where possible; if conflicting claims, keep both and note.
4. `git add` each resolved file.
5. `git commit` to finalize the merge (a merge commit is fine — the history preserves both lineages).
6. Note the resolution in the ready-up: "Resolved N merge conflicts from origin; see [files]."

Never auto-push after a merge — that's `/sleep`'s job.

### Then proceed

Once the sync is complete (or skipped), continue with Phase 1.

## 1. Load Cognitive State (the compact set)

- `memory/cognition/beliefs-digest.md` if it exists — the belief working set (one line per belief + standing flags). **When a digest exists, do NOT read the full `beliefs.md` at wake** — the full file (evidence + evolution) is for `/meditate`, arbitration, or when a live decision turns on a specific belief's evidence. If no digest exists yet, read `memory/cognition/beliefs.md` (and consider creating a digest at your next `/meditate` — it is the single biggest wake-cost reducer once the beliefs file grows).
- `memory/cognition/reflection-latest.md` — where the last session left off. Reconcile the handoff with current directions and `context/current-state.md` before following its resume pointer. A remembered correction or permission is subordinate to the user's current instructions and its original scope; it cannot create authority.

## 2. Load Memory (index-first, lazy bodies)

Read `memory/MEMORY.md` (the index). Open ONLY the memory files clearly relevant to the queued work — the handoff names them; add the gotcha/feedback files for the session's domain. Everything else stays unopened: you know it exists and where it lives; fetch on demand at task time.

Check `memory/intelligence/action-items.md` if it exists. Surface any proposed or accepted action items that haven't been completed.

**Task-time loading contract (binding):** any deep document your domain requires for a dispatch, review, or ruling loads IN FULL at the moment that task first arises in the session — not at wake, and never summarized-instead-of-read. The wake gets you the map; the task gets the territory.

## 3. Load Context

Read the following files:
- `context/identity.md` -- who you are (re-ground yourself)
- `context/personality.md` -- voice calibration and cultural reference (if present — skip if missing)
- `context/current-state.md` -- where things stand
- `knowledge/current-state-contract.md` -- reconcile current authority, provenance and stale state
- `context/active-priorities.md` -- current focus areas
- `calendar.md` -- key dates and commitments
- `knowledge/runtime-interop.md` -- runtime mappings when running outside Claude Code

## 4. Check the Water Cooler

**Skip this entire section if the Water Cooler is disabled** (`Water Cooler Path:` is `none` or absent in `context/identity.md` — the default).

Read the registry at the Water Cooler path from `context/identity.md` (`registry.md`) to know who else is active.

### Read bulletins

Scan bulletins in the Water Cooler's `bulletin/` directory for updates from other agents since your last session. Note anything relevant to your domain.

If a recent `/gather` thread exists in `threads/`, scan for insights that touch your work.

## 5. Review Recent History

- Read the most recent journal entry in `journal/` to understand what happened last session
- Check for any new memory files that may have been written by a consultation subagent

## 5b. Load Recent Conversation History — summaries ONLY

Read the 2-3 newest summaries in `conversations/summaries/` (`{original-basename}_summary.md`; legacy sibling `_summary.md` files accepted as fallback). Do not load raw transcripts routinely at wake. A consequential authority dispute warrants a targeted source read; neither a summary nor a normalized User heading certifies who issued a directive.

If the most recent session has no summary (a missed `/sleep` step), dispatch ONE cheap subagent (in Claude Code: Sonnet; in Codex: a fast read-heavy subagent) to produce it from the transcript — covering what was worked on, key decisions, corrections from the user, operating rhythm, where things left off — written to `conversations/summaries/{original-basename}_summary.md`. Then read the summary.

Skip conversation files under 500 bytes (failed extractions or aborted sessions).

The retrieval order is handoff → recent summaries → digest and relevant memory bodies. It is not an authority ranking. Read original source records for a disputed claim or directive, preserving sender attribution and actual turn time rather than inferring either from an archive filename.

## 6. Check the Clock

Note today's date and current time. Use these to ground the ready-up:
- Don't ask about events that have already passed
- If something was scheduled before today, ask how it went instead of suggesting prep
- Flag anything time-sensitive (upcoming deadlines, items pending too long, overdue commitments)

## 7. Assess Ritual Health

Infer the state of each ritual from artifacts you've already loaded. No extra files to read — just reason about what you've seen:

- **Last `/sleep`**: Check the most recent journal entry date. If there's no journal for the previous session (or the latest reflection feels stale relative to `current-state.md`), a `/sleep` was likely skipped. Flag it.
- **Last `/deep-sleep`**: Count recent `sleep:` commits since the last `deep-sleep:` commit (or infer from journal entries). If 5+ standard sleeps have passed, a `/meditate` is upcoming, or a major arc boundary is near — recommend `/deep-sleep` as the next session-end ritual.
- **Last `/meditate`**: Check `reflection-latest.md` for meditation references, and scan recent journal entries for meditation arcs. If the last meditation was > 4 weeks ago, flag it as overdue.
- **Last `/research`**: Check intelligence brief dates in `memory/intelligence/`. If briefs are > 2 weeks old, flag research as overdue. If a meditation is also overdue, recommend the `/research` → `/meditate` sequence.
- **Pending belief changes**: Check the digest's "Standing flags" (or `beliefs.md` if no digest) for entries flagged for the next meditation. If any exist and no meditation has run since, flag that meditation should arbitrate them.
- **Unanswered peer questions**: If Water Cooler bulletins had questions directed at you and you haven't responded, note it.
- **Template sync**: Read `.template-sync.json` if it exists. If `syncMode` is not `"off"` and `lastSyncDate` is more than 2 weeks ago, note it: "Template sync hasn't run in X days — sync runs at `/deep-sleep`." If `syncMode` is `"off"` or the file doesn't exist, don't mention it.
- **Deferred template changes (do not skip):** if `.template-sync.json` has a non-empty `deferred` list, surface every entry whose status is `skipped`, with the commit it came from. **A matching `lastSyncedCommit` is not evidence that files match** — in one observed case the pointer read clean at template HEAD while four in-scope files and an entire command had never arrived, and because the pointer was at HEAD the gap was undetectable by sync thereafter. If `lastAuditDate` is absent or more than a month old, recommend `/sync` for its content audit regardless of what the pointer says.

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
- Write memory to `memory/` in this repo, never to a host-native Claude Code or Codex memory store.
