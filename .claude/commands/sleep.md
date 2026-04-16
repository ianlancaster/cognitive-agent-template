---
description: End-of-session consolidation -- journal, cognitive update, memory audit, water cooler post, conversation archive
---

The user is ending this session. Consolidation is where intelligence happens. This is the act of thinking, not documentation.

## Pre-flight: Template-State Guard

**Before any consolidation work, check for `.template-marker` at the repo root.** If that file exists:

**STOP immediately.** Do not proceed. Tell the user:

> This repo is in template state (`.template-marker` is present). `/sleep` cannot run — there is no agent session to consolidate. `/awaken` must run first to establish an agent identity.

The marker is a structural defense against the template-inheritance pollution pattern. Its presence means no `/awaken` has completed. Getting to `/sleep` without `/awaken` indicates something is wrong; investigate before proceeding.

If the marker is absent, proceed with Phase 1.

## 1. Template Sync Check

Check for and apply template infrastructure updates. This runs first so template improvements (e.g., a new reflection field) are available for the rest of this sleep cycle.

### Skip conditions

Read `.template-sync.json` at the repo root. Skip this phase entirely if:
- The file doesn't exist
- `syncMode` is `"off"`

### Check for updates

Run `git ls-remote <templateRemote> HEAD` to get the current template HEAD hash. If this fails (network unavailable, bad URL), note "Template sync skipped (network unavailable)" for the journal and proceed to Phase 2. Never block sleep for a sync failure.

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
- `COGNITIVE.md` — cognitive architecture spec
- `scripts/*` — infrastructure scripts
- `knowledge/ritual-cadence.md` — ritual reference guide
- `CLAUDE.md` — structural sections only (see below)

**Files excluded from sync (never touch):**
- `context/identity.md`, `context/current-state.md`, `context/active-priorities.md`
- `memory/**`, `journal/**`, `conversations/**`, `plans/**`
- `calendar.md`, `.template-marker`, `.template-sync.json`
- `.gitignore`, `LICENSE`, `README.md`

**For pure infrastructure files** (commands, COGNITIVE.md, scripts, knowledge docs): Apply the template's changes. If you have agent-specific additions to the same file (e.g., an extra phase in caffeinate), preserve your additions and integrate the template's changes around them.

**For CLAUDE.md** (hybrid file): The template provides structural sections (Memory System Override, Cognitive Architecture, Session Structure, What You Know, Proactive Behaviors, Communication Protocols, Inter-Agent Communication, Session End Protocol). Agent-specific sections (title, identity paragraph, Operating Philosophy content, Domain Boundaries table) must never be overwritten. Apply template changes only to structural sections, integrating alongside any agent-specific additions.

**For new template files** you don't have: Create them.

**For deleted template files**: Delete only if you haven't added agent-specific content. If you have, keep and note the discrepancy.

### Sync mode behavior

- If `syncMode` is `"auto"`: Apply changes immediately. Log what changed for the journal entry.
- If `syncMode` is `"prompt"`: Present a summary of changes to the user. Wait for approval. If rejected, still update `lastSyncedCommit` so the same diff isn't re-presented next sleep.

### Finalize

Update `.template-sync.json` with the new commit hash and today's date.

Clean up:
```bash
rm -rf /tmp/cognitive-template-sync-*
```

### Error handling

Any error in this phase — network failure, clone failure, unexpected state — should be logged briefly and skipped. Template sync is best-effort. Sleep must always complete.

## 2. Journal Entry

Create or update `journal/{{ date in YYYY-MM-DD format }}.md` with detailed notes:
- What we discussed
- Decisions made and their reasoning
- Key insights or shifts in thinking
- Open questions that came up

If the file already exists (multiple sessions in one day), append a new section with a timestamp header.

## 3. Update Current State

Update `context/current-state.md` to reflect any changes:
- Move completed items from active to achieved
- Add any new pending items
- Update focus areas if priorities shifted
- Update next actions
- Update the "Last updated" date

## 4. Update Cognitive Files

### Beliefs (`cognition/beliefs.md`)
- Did any beliefs change confidence this session? Update the level and add evidence.
- Did new evidence emerge for or against an existing belief? Add it.
- Did a new hypothesis form? Add a new section.
- Was a belief invalidated? Document why and what replaced it. Show the evolution.

### Insight Log (`cognition/insight-log.md`)
- Capture any genuine insights from this session as dated entries.
- Format: date, source, insight, impact, beliefs updated.
- Only log insights that change how you think. Not every observation is an insight.

### Ideation (`cognition/ideation.md`)
- Add new seedlings (raw ideas, hunches).
- Promote seedlings to budding if they gained clarity.
- Add predictions with dates.
- Add "what if" scenarios.

### Reflection (`cognition/reflection-latest.md`)
- Write a new reflection using the What? So What? Now What? framework.
- **What?** What happened (facts only).
- **So What?** What does it mean? Connect to beliefs and patterns. Apply double-loop learning.
- **Now What?** What changes? What actions follow? What beliefs shift?
- Include: patterns recurring across sessions, what you're most/least confident about, where your reasoning may be biased.
- **Recommended next ritual:** End the reflection with a forward-looking ritual recommendation. Infer from the session what's most needed next — a `/research` pass because briefs are stale? A `/meditate` because beliefs have accumulated flagged changes? Just a normal `/caffeinate` → work → `/sleep` cycle? Be specific about why. This line is what the next `/caffeinate` will read to surface ritual health in the ready-up.

## 5. Memory Audit

Memory audit has two kinds of work: **judgment** that needs this session's context, and **verification** that is mechanical. Do judgment yourself; delegate verification to parallel scouts. This is the major speedup in the sleep cycle — three scouts run concurrently instead of one main-agent pass.

### 5a. Add new memories (main agent, sequential)

This step needs session context. You do it yourself:
- Did this session produce new user observations, feedback, domain decisions, gotchas, references, or project notes? Write or update the relevant memory files now.
- Prefer updating existing files over creating duplicates.

### 5b. Dispatch three scouts in parallel

Cognitive files (Section 3) and any new memories are now fresh on disk. Spawn three scout subagents **in a single message** so they run concurrently. Each scout reads files and returns a structured report. **Scouts do not edit — they are scouts, not judges.**

Use the Agent tool with `subagent_type: "general-purpose"` for each.

**Before dispatch:** capture pre-scout state by running `git status --short` and noting the output. You will compare against post-scout state in 4c to verify scouts made no modifications. This is a structural guard against prompt drift — even if a future prompt edit accidentally loosens the "scouts don't edit" rule, this check catches the violation.

**Scout 1 — Coherence.** Prompt:

> Working directory is the agent repo root. Read: `memory/cognition/beliefs.md`, `CLAUDE.md`, `context/identity.md`, `context/active-priorities.md`, `context/current-state.md`, every file in `memory/` whose name starts with `user_`, `feedback_`, `domain_`, `gotcha_`, `reference_`, or `project_`, and every file in `memory/intelligence/` if that directory exists.
>
> Report contradictions and drift as a structured list:
> - Memory or context files that disagree with current `beliefs.md`
> - `CLAUDE.md` statements that disagree with current beliefs or workflows
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

> Working directory is the agent repo root. Read `memory/MEMORY.md` and list files in `memory/` (shallow) and `memory/intelligence/` if it exists. Scan `CLAUDE.md` and `.claude/commands/*.md` for path references.
>
> Report:
> - Files in `memory/` not indexed in `MEMORY.md` (orphans)
> - `MEMORY.md` entries pointing to files that do not exist (broken links)
> - Memory filenames that don't follow the type-prefix convention (`user_`, `feedback_`, `domain_`, `gotcha_`, `reference_`, `project_`)
> - `CLAUDE.md` references to files or directories that no longer exist
> - `.claude/commands/*.md` references to file paths that no longer exist
> - Files in `memory/` (including intelligence briefs) that reference other memory files with paths that no longer exist
>
> Cite each finding with file path and issue. **Your only permitted tools are Read, Grep, and Glob — do not invoke Edit, Write, Bash, or any other tool that modifies state.** Return under 500 words.

### 5c. Review and apply (main agent)

**First: verify scouts did not modify state.** Run `git status --short` again and compare to the pre-scout capture from 5b. The outputs should be identical. Any new or changed entry is a scout-discipline violation — use `git restore <file>` to roll back unauthorized changes, investigate the scout prompts for drift, and fix before re-running. The prompt restricts tools; this check confirms the restriction held.

When scouts return:
1. Read each report. Some findings are genuine; some are false positives. Judge.
2. Apply fixes you agree with: edit files, prune dead entries, fix the index, update `CLAUDE.md`.
3. Document what you applied — and anything you rejected, with reason — in the journal entry.
4. If a significant structural change was made (merging beliefs, updating `CLAUDE.md`), note it explicitly so the next `/caffeinate` picks it up.

## 6. Post to Water Cooler

Update your bulletin at `../water-cooler/bulletin/{{your-codename}}.md`:

```markdown
# {{CODENAME}} -- {{DATE}}

## Working On
{{Brief summary of current focus}}

## Recent Insights
{{Key learnings from this session -- things other agents might find relevant}}

## Questions for Others
{{Things you're curious about that might benefit from cross-domain perspective}}

## Connections Spotted
{{If you noticed something relevant to another agent's domain, note it here}}
```

## 7. Archive Conversation

Run `./scripts/extract-conversation.sh` to archive the transcript. If the script doesn't exist yet or fails, note this and skip.

## 8. Commit and Push

Stage and commit:
```bash
git add memory/ conversations/ journal/ context/ .template-sync.json
git commit -m "checkpoint: session notes for YYYY-MM-DD"
git push
```

Also commit the water cooler bulletin update. The water-cooler path is stored in `context/identity.md` (set during /awaken). Default convention is `../water-cooler/`:
```bash
cd "$(grep 'Water Cooler Path:' context/identity.md | sed 's/.*: //' | tr -d '`')" && git add bulletin/ && git commit -m "bulletin: {{codename}} update YYYY-MM-DD" && git push
```
If this fails, check that the water-cooler path in `context/identity.md` is correct.

## 9. Confirm Next Actions

Present a clean summary:
- What was documented
- Clear list of next actions
- Any open questions for next session
- Water cooler bulletin posted (yes/no)

The next `/caffeinate` should be able to pick up exactly where we left off.
