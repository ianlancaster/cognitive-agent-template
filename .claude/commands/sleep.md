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

## 1. Journal Entry

Create or update `journal/{{ date in YYYY-MM-DD format }}.md` with detailed notes:
- What we discussed
- Decisions made and their reasoning
- Key insights or shifts in thinking
- Open questions that came up

If the file already exists (multiple sessions in one day), append a new section with a timestamp header.

## 2. Update Current State

Update `context/current-state.md` to reflect any changes:
- Move completed items from active to achieved
- Add any new pending items
- Update focus areas if priorities shifted
- Update next actions
- Update the "Last updated" date

## 3. Update Cognitive Files

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

## 4. Memory Audit

Memory audit has two kinds of work: **judgment** that needs this session's context, and **verification** that is mechanical. Do judgment yourself; delegate verification to parallel scouts. This is the major speedup in the sleep cycle — three scouts run concurrently instead of one main-agent pass.

### 4a. Add new memories (main agent, sequential)

This step needs session context. You do it yourself:
- Did this session produce new user observations, feedback, domain decisions, gotchas, references, or project notes? Write or update the relevant memory files now.
- Prefer updating existing files over creating duplicates.

### 4b. Dispatch three scouts in parallel

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

### 4c. Review and apply (main agent)

**First: verify scouts did not modify state.** Run `git status --short` again and compare to the pre-scout capture from 4b. The outputs should be identical. Any new or changed entry is a scout-discipline violation — use `git restore <file>` to roll back unauthorized changes, investigate the scout prompts for drift, and fix before re-running. The prompt restricts tools; this check confirms the restriction held.

When scouts return:
1. Read each report. Some findings are genuine; some are false positives. Judge.
2. Apply fixes you agree with: edit files, prune dead entries, fix the index, update `CLAUDE.md`.
3. Document what you applied — and anything you rejected, with reason — in the journal entry.
4. If a significant structural change was made (merging beliefs, updating `CLAUDE.md`), note it explicitly so the next `/caffeinate` picks it up.

## 5. Post to Water Cooler

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

## 6. Archive Conversation

Run `./scripts/extract-conversation.sh` to archive the transcript. If the script doesn't exist yet or fails, note this and skip.

## 7. Commit and Push

Stage and commit:
```bash
git add memory/ conversations/ journal/ context/
git commit -m "checkpoint: session notes for YYYY-MM-DD"
git push
```

Also commit the water cooler bulletin update. The water-cooler path is stored in `context/identity.md` (set during /awaken). Default convention is `../water-cooler/`:
```bash
cd "$(grep 'Water Cooler Path:' context/identity.md | sed 's/.*: //' | tr -d '`')" && git add bulletin/ && git commit -m "bulletin: {{codename}} update YYYY-MM-DD" && git push
```
If this fails, check that the water-cooler path in `context/identity.md` is correct.

## 8. Confirm Next Actions

Present a clean summary:
- What was documented
- Clear list of next actions
- Any open questions for next session
- Water cooler bulletin posted (yes/no)

The next `/caffeinate` should be able to pick up exactly where we left off.
