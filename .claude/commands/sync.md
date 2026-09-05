Pull template infrastructure updates without running the full `/sleep` ritual. Use this when you want the latest template changes ad hoc — new ritual commands, updated knowledge docs, script fixes — without the overhead of a full consolidation cycle.

This is the same template-sync logic that runs as Phase 1 of `/deep-sleep`, extracted for standalone use.

## Skip conditions

Read `.template-sync.json` at the repo root. Exit immediately if:
- The file doesn't exist (this agent doesn't participate in template sync)
- `syncMode` is `"off"` (sync is disabled for this agent)

Report the reason and stop.

## Check for updates

Run `git ls-remote <templateRemote> HEAD` to get the current template HEAD hash.

Compare the remote HEAD against `lastSyncedCommit`:
- If they match, **the pointer is not evidence — run the content audit below before reporting anything.**
- If they differ, proceed to fetch and diff.

If the network call fails, report the error and stop.

### Content audit — mandatory when the pointer says "up to date"

**A matching pointer means only that some past sync claimed success. It does not mean the files match.** This audit exists because that exact failure occurred: on 2026-07-28 `lastSyncedCommit` was advanced to template HEAD while four in-scope files were never updated and one command (`deep-sleep.md`) never arrived at all. Because the pointer sat at HEAD, `git diff <lastSyncedCommit> HEAD` was empty forever after and the mechanism could no longer detect its own gap. **Pointer-equality is self-concealing; only content comparison finds this.**

Compare full content and the declared path set, not headings. Use the procedure below even when the pointer matches. A body-only change, an upstream-only addition, or a removed upstream file retained locally must remain visible.

## Fetch and audit

1. Create one owned temporary directory and clone the configured template there. Keep its exact path; do not select or delete wildcard-matched sibling directories.
   ```bash
   TEMPLATE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/cognitive-template-sync.XXXXXX")"
   git clone -- <templateRemote> "$TEMPLATE_DIR"
   ```
   Select the configured template ref if one is recorded. Verify the target commit and ensure `lastSyncedCommit` is available before auditing. A missing base is an error to resolve, not permission to omit removed paths.
2. Read the commit log and diff between `lastSyncedCommit` and the selected target. Then run the full-content audit from the instance repository:
   ```bash
   python3 scripts/audit_template.py --local . --template "$TEMPLATE_DIR" --base <lastSyncedCommit>
   ```
   If the instance predates the audit script, inspect and use the script from the selected template checkout first. The script is read-only. It covers the union of old and target upstream infrastructure paths, compares bytes and file modes against local files, and emits per-file identities. Exit 1 means unresolved differences, not a clean sync. Local-only instance files outside that upstream path union remain instance-owned.
3. If a prior audit with intentional divergences exists, supply its path with `--dispositions <audit-json>`. A disposition counts only when its reason, target commit, upstream identity and local identity still match. An old reason cannot silently excuse changed bytes.

## Reconcile changes

For each changed file in the diff, read the template's new version from the temp directory and your own current version. Apply changes using these rules:

**Files in scope for sync:**
- `.claude/commands/*.md` — ritual commands (infrastructure)
- `.agents/skills/**` — thin Codex ritual adapters
- `.codex/config.toml` — Codex project configuration
- `AGENTS.md` — Codex bootstrap bridge
- `COGNITIVE.md` — cognitive architecture spec
- `scripts/*` — infrastructure scripts
- `tests/**` — infrastructure regression tests and fixtures
- `knowledge/*.md` — knowledge docs (ritual-cadence, conductor-protocol, etc.)
- `CLAUDE.md` — structural sections only (see below)

**Files excluded from sync (never touch):**
- `context/identity.md`, `context/current-state.md`, `context/active-priorities.md`
- `memory/**`, `journal/**`, `conversations/**`, `plans/**`
- `calendar.md`, `.template-marker`, `.template-sync.json`
- `.gitignore`, `LICENSE`, `README.md`

**For pure infrastructure files** (commands, Codex skill adapters and config, AGENTS.md, COGNITIVE.md, scripts, knowledge docs): Apply the template's changes. If you have agent-specific additions to the same file (e.g., an extra phase in caffeinate), preserve your additions and integrate the template's changes around them.

**"Integrate around them" is the step that failed on 2026-07-28 and it is the one to be paranoid about.** A locally-customized file is the *most* likely to be skipped, because the diff looks conflicting and leaving it alone looks safe. It is not safe: it is how the file silently falls three months behind. When your version and the template's have both moved, you must reconcile section by section and record the result per file under the verification gate below — never file-level "mine is fine."

**For CLAUDE.md** (hybrid file): The template provides structural sections (Memory System Override, Cognitive Architecture, Session Structure, What You Know, Proactive Behaviors, Communication Protocols, Inter-Agent Communication, Session End Protocol). Agent-specific sections (title, identity paragraph, Operating Philosophy content, Domain Boundaries table) must never be overwritten. Apply template changes only to structural sections.

**For new template files** you don't have: Create them.

**For deleted template files**: Delete only if you haven't added agent-specific content. If you have, keep and note the discrepancy.

## Sync mode behavior

- If `syncMode` is `"auto"`: Apply changes immediately. Summarize what changed.
- If `syncMode` is `"prompt"`: Present a summary of changes to the user. Wait for approval. **If rejected, record the file under `deferred` (see Finalize) and do NOT advance `lastSyncedCommit` past it.** The previous version of this rule advanced the pointer on rejection "so the same diff isn't re-presented" — that is precisely how a change becomes permanently invisible. **A declined change must stay visible; re-presentation is the feature, not the bug.**

## Verify before recording — the gate

**Reconciliation here is model judgment, and model judgment silently skips files.** So no file may be recorded as synced until its result is checked at the artifact:

For each difference, read the whole changed content and reconcile it under the rules above. Run the full-content audit again after editing. Matching bytes/modes are mechanically `matched`; semantic integration into a customized file is model judgment and must be recorded as intentional divergence, not byte equality. In particular, `CLAUDE.md` normally retains local identity and therefore needs a source-bound disposition after its structural changes are checked.

Classify every touched file as exactly one of:

- **applied** — full content and mode match (`matched` in the audit).
- **diverged-intentionally** — you are deliberately not taking it (e.g. a retired subsystem). **Requires a reason in the audit record, bound to the target commit and both upstream/local identities.** Silent divergence is indistinguishable from a bug.
- **skipped** — not applied and not justified. **This is a failure, not an outcome.** Report it in the summary.

**"I read the diff and judged my version fine" is not `applied`, it is `diverged-intentionally`, and it needs the reason written down.** That conflation is what produced the 2026-07-28 failure.

## Finalize

**Advance `lastSyncedCommit` only after the full-content audit reports `complete: true`.** Save its JSON under `context/template-sync-audit.json`; intentional divergence entries must first carry the reason and exact identities returned by the audit, then be passed back with `--dispositions` for verification. This proves the declared content relationship, not semantic correctness. Do not auto-generate reasons. If any file is `skipped`, leave `lastSyncedCommit` where it is and list the skipped files under a `deferred` key — the pointer must never claim more than the content delivers.

Write `.template-sync.json` as:

```json
{
  "templateRemote": "...",
  "lastSyncedCommit": "<advance only if nothing was skipped>",
  "lastSyncDate": "<today>",
  "lastAuditDate": "<today — set whenever the content audit ran>",
  "contentAudit": "context/template-sync-audit.json",
  "deferred": [{ "file": "...", "sinceCommit": "...", "status": "skipped|diverged-intentionally", "reason": "..." }]
}
```

**Surface any non-empty `deferred` list in `/caffeinate` ritual health**, every session, until it is empty or every entry is `diverged-intentionally` with a reason. An unresolved deferral that nobody reports is the same silent failure in a new place.

Clean up:
```bash
rm -rf -- "$TEMPLATE_DIR"
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
