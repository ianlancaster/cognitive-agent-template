# Template Sync — Distributed Cognitive Infrastructure Updates

*Date: 2026-04-16*
*Author: Ford (cognitive architecture owner)*
*Status: Design approved*

## Problem

The cognitive agent ecosystem has grown to 6+ agents, each created from a shared template and then diverging into independent repos. Improvements to the cognitive infrastructure (ritual commands, COGNITIVE.md, scripts, knowledge docs) must be manually propagated to each agent — a burden that scales linearly with agent count and is error-prone.

## Solution

An AI-mediated template sync mechanism embedded in the `/sleep` ritual. Agents periodically check the template's remote repository for changes, read the diff, and intelligently apply updates while preserving their own identity and customizations. The agent is the merge tool — no mechanical git reconciliation.

## Design Principles

1. **The agent is the merge tool.** No `git merge`, no `git rebase`, no mechanical file replacement. The agent reads the diff, understands the intent from commit messages, reads its own files, and surgically applies changes with full awareness of its identity.
2. **Remote is the source of truth.** Agents check the template's remote git repository, not a local sibling directory. Push to the template remote, and agents pick it up on their next sleep.
3. **Sync is best-effort, never blocking.** Network failures, missing config, or unexpected errors skip the sync silently. Sleep must always complete.
4. **User controls the sync mode.** Three tiers: auto-apply, approve first, or off. Set during onboarding, changeable anytime.

## Sync State File

`.template-sync.json` at the agent's repo root:

```json
{
  "templateRemote": "https://github.com/ianlancaster/cognitive-agent-template.git",
  "lastSyncedCommit": "aa7d326...",
  "syncMode": "auto",
  "lastSyncDate": "2026-04-16"
}
```

| Field | Purpose | Set by |
|-------|---------|--------|
| `templateRemote` | URL of the template's remote repository | `/awaken` Phase 5 |
| `lastSyncedCommit` | Hash of the last template commit this agent has reconciled | `/awaken` (initial), `/sleep` (ongoing) |
| `syncMode` | `"auto"` / `"prompt"` / `"off"` | `/awaken` Q12, user can change anytime |
| `lastSyncDate` | ISO date of last successful sync check | `/sleep` sync phase |

Committed to the agent's repo. Read during caffeinate (ritual health) and sleep (sync decision).

## Awaken Integration

### New Onboarding Question (Q12, after ritual orientation)

> "One more thing about the cognitive system. I receive updates and improvements over time through a shared template. How would you like to handle those updates?"
> - **Auto-apply**: I'll check for template updates at the end of each session and apply them myself. You'll see a summary of what changed.
> - **Approve first**: I'll check for updates and show you what changed, but wait for your approval before applying.
> - **Don't check**: I won't check for template updates. You can change this later.

### Phase 0 Capture (before git history is destroyed)

Before Phase 0 runs `rm -rf .git && git init`, capture:
- The template's remote URL (`git remote get-url origin`)
- The template's current HEAD hash (`git rev-parse HEAD`)

Store these in shell variables. Write them to `.template-sync.json` during Phase 5 alongside the user's sync preference from Q12.

## Sleep Integration — Template Sync Phase

New phase in `/sleep`, positioned **early** — after the template-state guard but before the journal entry. This way template improvements (e.g., a new reflection field) are available for the current sleep cycle.

### Flow

1. **Read config.** Read `.template-sync.json`. If missing or `syncMode` is `"off"`, skip entirely.
2. **Check remote.** Run `git ls-remote <templateRemote> HEAD` to get the current template HEAD hash. If network fails, log silently and skip.
3. **Compare.** If remote HEAD equals `lastSyncedCommit`, skip — nothing new.
4. **Clone.** Shallow clone the template into `/tmp/cognitive-template-sync-<random>/`: `git clone --depth=50 <templateRemote> /tmp/cognitive-template-sync-XXXXX`. Depth 50 ensures we have enough history to cover the diff from `lastSyncedCommit` to HEAD. If `lastSyncedCommit` is not in the shallow history, fall back to a full clone.
5. **Diff.** Inside the cloned repo, generate: `git diff <lastSyncedCommit> HEAD` and `git log --oneline <lastSyncedCommit>..HEAD` for commit context.
6. **Read.** The agent reads the diff and commit messages, then reads its own current versions of each affected file.
7. **Reconcile.** Apply changes using the AI-mediated reconciliation protocol (below).
   - If `syncMode` is `"auto"`: apply immediately, log changes in journal.
   - If `syncMode` is `"prompt"`: present summary to user, wait for approval. If rejected, still update `lastSyncedCommit` (don't re-present the same diff next sleep).
8. **Update state.** Write new commit hash, today's date to `.template-sync.json`.
9. **Cleanup.** `rm -rf /tmp/cognitive-template-sync-*`.

### Error Handling

- Network failure on `git ls-remote`: skip sync, proceed with sleep. Note in journal: "Template sync skipped (network unavailable)."
- Clone failure: skip sync, proceed with sleep.
- `lastSyncedCommit` not in shallow history: retry with full clone. If still not found (commit was force-pushed away), treat the full template state as the baseline — do a full reconciliation against current files.
- Any unexpected error: skip sync, proceed with sleep. Never block consolidation.

## AI-Mediated Reconciliation Protocol

For each changed file in the diff:

1. **Read the template's new version** from the temp directory.
2. **Read your current version** of the same file.
3. **Understand the intent** from the commit message and diff context.
4. **Apply by file category:**

### Pure Infrastructure Files
`.claude/commands/*.md`, `COGNITIVE.md`, `scripts/*`, `knowledge/ritual-cadence.md`

Apply the template's changes, but check if you've made agent-specific modifications to the same file (e.g., Ford's caffeinate has an extra Phase 7 for cognitive-footprint monitoring). If you have local additions, merge the template's changes into your version — preserve your additions, integrate the template's.

### CLAUDE.md (Hybrid File)

The template provides structural sections:
- Memory System Override
- Cognitive Architecture reference
- Session Structure
- What You Know
- Proactive Behaviors
- Inter-Agent Communication
- Session End Protocol

Agent-specific sections that must never be overwritten:
- Title line (codename + role)
- First-run gate comment (removed post-awaken)
- Identity paragraph
- Operating Philosophy (content, not structure)
- Domain Boundaries table

Apply template changes only to structural sections. Integrate alongside any agent-specific additions the agent has made to those sections.

### New Template Files
Files the template added that the agent doesn't have: create them.

### Deleted Template Files
Files the template removed: delete only if the agent hasn't modified them with agent-specific content. If the agent has, keep and note the discrepancy.

### Excluded Files (never touched by sync)
- `context/identity.md`, `context/current-state.md`, `context/active-priorities.md`
- `memory/**`
- `journal/**`, `conversations/**`, `plans/**`
- `calendar.md`
- `.template-marker`
- `.template-sync.json`
- `.gitignore`, `LICENSE`, `README.md`

### Logging

For each file touched, one line noting:
- The file path
- What changed (brief)
- Whether agent-specific content was preserved
- The commit(s) that introduced the change

This log goes into the journal entry for the session.

## Caffeinate Integration

In the ritual-health assessment phase of caffeinate:

- Read `.template-sync.json`.
- If `lastSyncDate` is more than 2 weeks old and `syncMode` is not `"off"`, surface in the ritual health line: "Template sync hasn't run in X days — next `/sleep` will check for updates."
- If `syncMode` is `"off"`, don't mention it.

## Rollout to Existing Agents

After all template changes are pushed to the remote:

For each of the six active agents (Ford, Wolf, Coach, Hot Shot, Bill, Hans):

1. Add the template sync phase to their `/sleep` command
2. Update `/caffeinate` to report sync status in ritual health
3. Update `COGNITIVE.md` with ritual ownership section
4. Update `CLAUDE.md` proactive behaviors with ritual signal mappings
5. Propagate the ritual orientation step in `/awaken` (Q11) and sync preference question (Q12)
6. Propagate the "recommended next ritual" field in `/sleep` reflection template
7. Propagate `knowledge/ritual-cadence.md` if the agent doesn't have it
8. Create `.template-sync.json` with:
   - `templateRemote`: `"https://github.com/ianlancaster/cognitive-agent-template.git"`
   - `lastSyncedCommit`: Template's HEAD after all template changes are pushed
   - `syncMode`: `"auto"`
   - `lastSyncDate`: Today's date
9. Commit: `"infra: template sync mechanism + ritual ownership (final manual propagation)"`

This is the last manual propagation. All future template improvements flow through the sync mechanism.

## File Manifest

### New files
- `.template-sync.json` (per agent, created during awaken or rollout)

### Modified files in template
- `.claude/commands/awaken.md` — Q12 sync preference + Phase 0 capture
- `.claude/commands/sleep.md` — Template sync phase
- `.claude/commands/caffeinate.md` — Sync status in ritual health

### Previously modified (this session, already committed)
- `.claude/commands/awaken.md` — Q11 ritual orientation
- `.claude/commands/caffeinate.md` — Ritual health assessment phase
- `.claude/commands/sleep.md` — Recommended next ritual field
- `COGNITIVE.md` — Ritual ownership section, `/nap` in session commands table
- `CLAUDE.md` — Proactive behaviors ritual signal mappings
- `knowledge/ritual-cadence.md` — New file, generalized owner's manual

## Success Criteria

1. A template change pushed to the remote is picked up by an agent on its next `/sleep` cycle
2. Agent-specific identity (codename, philosophy, domain boundaries, beliefs, memory) is never overwritten
3. Agent-specific additions to infrastructure files (e.g., Ford's caffeinate Phase 7) are preserved when template changes are applied to the same file
4. Network failures or missing config never block sleep consolidation
5. The user can control sync behavior (auto/prompt/off) and change it at any time
6. After rollout, no further manual propagation is needed for template improvements
