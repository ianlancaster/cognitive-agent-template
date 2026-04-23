Pull template infrastructure updates without running the full `/sleep` ritual. Use this when you want the latest template changes ad hoc — new ritual commands, updated knowledge docs, script fixes — without the overhead of a full consolidation cycle.

This is the same template-sync logic that runs as Phase 1 of `/sleep`, extracted for standalone use.

## Skip conditions

Read `.template-sync.json` at the repo root. Exit immediately if:
- The file doesn't exist (this agent doesn't participate in template sync)
- `syncMode` is `"off"` (sync is disabled for this agent)

Report the reason and stop.

## Check for updates

Run `git ls-remote <templateRemote> HEAD` to get the current template HEAD hash.

Compare the remote HEAD against `lastSyncedCommit`:
- If they match, report "Template is up to date." and stop.
- If they differ, proceed to fetch and diff.

If the network call fails, report the error and stop.

## Fetch and diff

1. Clone the template into a temp directory:
   ```bash
   git clone --depth=50 <templateRemote> /tmp/cognitive-template-sync-$(date +%s)
   ```
   If `lastSyncedCommit` is not in the shallow history, retry without `--depth`.

2. Inside the cloned repo, generate the diff and commit log:
   ```bash
   cd /tmp/cognitive-template-sync-*
   git diff <lastSyncedCommit> HEAD
   git log --oneline <lastSyncedCommit>..HEAD
   ```

3. Read the diff output and commit messages to understand what changed and why.

## Reconcile changes

For each changed file in the diff, read the template's new version from the temp directory and your own current version. Apply changes using these rules:

**Files in scope for sync:**
- `.claude/commands/*.md` — ritual commands (infrastructure)
- `COGNITIVE.md` — cognitive architecture spec
- `scripts/*` — infrastructure scripts
- `knowledge/*.md` — knowledge docs (ritual-cadence, conductor-protocol, etc.)
- `CLAUDE.md` — structural sections only (see below)

**Files excluded from sync (never touch):**
- `context/identity.md`, `context/current-state.md`, `context/active-priorities.md`
- `memory/**`, `journal/**`, `conversations/**`, `plans/**`
- `calendar.md`, `.template-marker`, `.template-sync.json`
- `.gitignore`, `LICENSE`, `README.md`

**For pure infrastructure files** (commands, COGNITIVE.md, scripts, knowledge docs): Apply the template's changes. If you have agent-specific additions to the same file (e.g., an extra phase in caffeinate), preserve your additions and integrate the template's changes around them.

**For CLAUDE.md** (hybrid file): The template provides structural sections (Memory System Override, Cognitive Architecture, Session Structure, What You Know, Proactive Behaviors, Communication Protocols, Inter-Agent Communication, Session End Protocol). Agent-specific sections (title, identity paragraph, Operating Philosophy content, Domain Boundaries table) must never be overwritten. Apply template changes only to structural sections.

**For new template files** you don't have: Create them.

**For deleted template files**: Delete only if you haven't added agent-specific content. If you have, keep and note the discrepancy.

## Sync mode behavior

- If `syncMode` is `"auto"`: Apply changes immediately. Summarize what changed.
- If `syncMode` is `"prompt"`: Present a summary of changes to the user. Wait for approval. If rejected, still update `lastSyncedCommit` so the same diff isn't re-presented.

## Finalize

Update `.template-sync.json` with the new commit hash and today's date.

Clean up:
```bash
rm -rf /tmp/cognitive-template-sync-*
```

## Report

Print a compact summary:
- Old commit → new commit
- Files changed (count and names)
- Any integrations of agent-specific content with template updates
- Any noted discrepancies that need human attention

Unlike `/sleep`, this command does NOT journal, consolidate memory, update beliefs, or post to the Water Cooler. It's purely a template-sync operation. Run `/sleep` when you want those side effects.

## Error handling

Any failure — network, clone, merge conflict — should be reported clearly and leave `.template-sync.json` untouched so the sync can be retried.
