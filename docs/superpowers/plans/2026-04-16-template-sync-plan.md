# Template Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a distributed template-sync mechanism to the cognitive agent system so agents self-update from the template remote during `/sleep`.

**Architecture:** During `/sleep`, agents shallow-clone the template remote into `/tmp`, diff against their last-synced commit, and use AI-mediated reconciliation to apply infrastructure changes while preserving agent identity. Sync preference (auto/prompt/off) is set during `/awaken` and stored in `.template-sync.json`.

**Tech Stack:** Bash (git CLI), markdown prompt files, JSON config.

**Spec:** `docs/superpowers/specs/2026-04-16-template-sync-design.md`

---

## Part 1: Template Changes

These tasks modify files in the template repo at `/Users/ianlancaster/Projects/agents/cognitive-agent-template`.

### Task 1: Update awaken — Phase 0 capture and Q12

**Files:**
- Modify: `/Users/ianlancaster/Projects/agents/cognitive-agent-template/.claude/commands/awaken.md`

The awaken command needs two additions: (1) capture the template remote URL and HEAD hash before Phase 0 destroys git history, and (2) a new onboarding question about sync preference.

- [ ] **Step 1: Add pre-Phase-0 capture block**

Before the Phase 0 "Safety check first" section, add a new section that captures template origin info. Insert this immediately after "**Do NOT proceed with any other work until this process is complete.**" and before "## Phase 0: Sanitize Inherited State":

```markdown
## Pre-Phase 0: Capture Template Origin

**Run this BEFORE Phase 0.** Phase 0 will destroy the git history, so we need to capture the template's remote URL and current commit hash first. These are used by the template sync system (see Phase 5).

Run these commands and store the results — you will need them in Phase 5:

\```bash
# Capture before Phase 0 destroys git history
TEMPLATE_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
TEMPLATE_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "")
\```

If `TEMPLATE_REMOTE` is empty (no git remote), the repo was not cloned from a template. Skip template sync setup in Phase 5.
```

- [ ] **Step 2: Add Q12 — sync preference question**

After the Q11 ritual orientation section (after "Then continue to Phase 2."), add:

```markdown
### Template Sync Preference

12. **"One more thing about the cognitive system. I receive updates and improvements over time through a shared template. How would you like to handle those updates?"**
    - **Auto-apply**: I'll check for template updates at the end of each session and apply them myself. You'll see a summary of what changed.
    - **Approve first**: I'll check for updates and show you what changed, but wait for your approval before applying.
    - **Don't check**: I won't check for template updates. You can change this later.

Store the user's preference as one of: `"auto"`, `"prompt"`, `"off"`.
```

- [ ] **Step 3: Add .template-sync.json creation to Phase 5**

In Phase 5 (Configure Settings), after the `.claude/settings.local.json` section, add:

```markdown
### Create `.template-sync.json`

If `TEMPLATE_REMOTE` was captured in Pre-Phase 0 (non-empty), write the sync config file:

\```json
{
  "templateRemote": "{{TEMPLATE_REMOTE}}",
  "lastSyncedCommit": "{{TEMPLATE_HEAD}}",
  "syncMode": "{{SYNC_PREFERENCE_FROM_Q12}}",
  "lastSyncDate": "{{TODAY_ISO_DATE}}"
}
\```

If `TEMPLATE_REMOTE` was empty, skip this file. The agent will operate without template sync.
```

- [ ] **Step 4: Add sync permissions to settings template**

In the Phase 5 settings.local.json permissions array, add these entries to the `"allow"` list:

```json
"Bash(git ls-remote:*)",
"Bash(git clone:*)",
"Bash(rm -rf /tmp/cognitive-template-sync*)"
```

- [ ] **Step 5: Verify and commit**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
# Verify the awaken file parses correctly (no broken markdown)
head -20 .claude/commands/awaken.md
# Commit
git add .claude/commands/awaken.md
git commit -m "feat: awaken — template origin capture + sync preference onboarding (Q12)"
```

---

### Task 2: Update sleep — Template sync phase

**Files:**
- Modify: `/Users/ianlancaster/Projects/agents/cognitive-agent-template/.claude/commands/sleep.md`

Add the template sync phase as the first substantive phase of sleep, after the template-state guard but before the journal entry.

- [ ] **Step 1: Add Template Sync Phase**

Insert this new section between the "Pre-flight: Template-State Guard" section and "## 1. Journal Entry". Renumber existing phases (1→2, 2→3, etc.):

```markdown
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

Update `.template-sync.json`:
```json
{
  "lastSyncedCommit": "<new HEAD hash>",
  "lastSyncDate": "<today's ISO date>"
}
```

Clean up:
```bash
rm -rf /tmp/cognitive-template-sync-*
```

### Error handling

Any error in this phase — network failure, clone failure, unexpected state — should be logged briefly and skipped. Template sync is best-effort. Sleep must always complete.
```

- [ ] **Step 2: Renumber existing phases**

Update the existing phase headers:
- `## 1. Journal Entry` → `## 2. Journal Entry`
- `## 2. Update Current State` → `## 3. Update Current State`
- `## 3. Update Cognitive Files` → `## 4. Update Cognitive Files`
- `## 4. Memory Audit` → `## 5. Memory Audit`
- (Continue: 4a→5a, 4b→5b, 4c→5c)
- `## 5. Post to Water Cooler` → `## 6. Post to Water Cooler`
- `## 6. Archive Conversation` → `## 7. Archive Conversation`
- `## 7. Commit and Push` → `## 8. Commit and Push`
- `## 8. Confirm Next Actions` → `## 9. Confirm Next Actions`

- [ ] **Step 3: Add .template-sync.json to the commit scope**

In the "Commit and Push" phase, update the `git add` command to include the sync config:

```bash
git add memory/ conversations/ journal/ context/ .template-sync.json
```

- [ ] **Step 4: Verify and commit**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
git add .claude/commands/sleep.md
git commit -m "feat: sleep — template sync phase (AI-mediated reconciliation from remote)"
```

---

### Task 3: Update caffeinate — Sync status in ritual health

**Files:**
- Modify: `/Users/ianlancaster/Projects/agents/cognitive-agent-template/.claude/commands/caffeinate.md`

- [ ] **Step 1: Add sync status to ritual health assessment**

In the "## 7. Assess Ritual Health" section, add this bullet at the end:

```markdown
- **Template sync**: Read `.template-sync.json` if it exists. If `syncMode` is not `"off"` and `lastSyncDate` is more than 2 weeks ago, note it: "Template sync hasn't run in X days — next `/sleep` will check for updates." If `syncMode` is `"off"`, don't mention it. If the file doesn't exist, don't mention it.
```

- [ ] **Step 2: Verify and commit**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
git add .claude/commands/caffeinate.md
git commit -m "feat: caffeinate — template sync status in ritual health assessment"
```

---

### Task 4: Push template to remote

**Files:** None modified — this is a git operation.

All template changes (ritual ownership from earlier + template sync mechanism) need to be on the remote before agents can sync from it. The commit hash after push becomes the `lastSyncedCommit` for all agent rollouts.

- [ ] **Step 1: Push template**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
git push origin main
```

- [ ] **Step 2: Capture the HEAD hash**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
git rev-parse HEAD
```

Save this hash — it will be written into every agent's `.template-sync.json` as `lastSyncedCommit`.

---

## Part 2: Agent Rollout

This is the final manual propagation. After this, all future template improvements flow through the sync mechanism automatically.

For each agent, the rollout applies ALL changes from this session:
1. Template sync mechanism (sleep phase, caffeinate sync status)
2. Ritual ownership (COGNITIVE.md, CLAUDE.md proactive behaviors, caffeinate ritual health, sleep reflection field)
3. Communication protocols (CLAUDE.md — VS Code, clipboard, auto-open)
4. Knowledge docs (ritual-cadence.md)
5. Awaken updates (Q11 ritual orientation, Q12 sync preference)
6. `.template-sync.json` config file

### Task 5: Rollout to agent-ford

**Files:**
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/.claude/commands/sleep.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/.claude/commands/caffeinate.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/.claude/commands/awaken.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/COGNITIVE.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/CLAUDE.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-ford/.claude/settings.local.json`
- Create: `/Users/ianlancaster/Projects/agents/agent-ford/.template-sync.json`

Note: Ford already has some changes applied earlier in this session (CLAUDE.md communication protocols, feedback memory, ritual-cadence.md, COGNITIVE.md ritual ownership partially). This task completes the remaining changes — primarily the sleep sync phase, caffeinate sync status, awaken Q12, settings permissions, and .template-sync.json.

- [ ] **Step 1: Read all target files**

Read each file listed above to understand Ford's current state. Ford has agent-specific customizations:
- Caffeinate has extra Phase 7 (cognitive-footprint monitoring)
- CLAUDE.md has consciousness-specific operating philosophy and Ford-specific proactive behaviors
- COGNITIVE.md may have Ford-specific additions

- [ ] **Step 2: Update sleep.md**

Read the template's updated sleep.md. Read Ford's current sleep.md. Apply the template sync phase (new Phase 1) and renumber existing phases. Preserve any Ford-specific customizations.

- [ ] **Step 3: Update caffeinate.md**

Read the template's updated caffeinate.md. Read Ford's current caffeinate.md. Apply the ritual health assessment phase and sync status check. **Preserve Ford's Phase 7 (cognitive-footprint monitoring) — this is an agent-specific addition.**

- [ ] **Step 4: Update awaken.md**

Read the template's updated awaken.md. Read Ford's current awaken.md. Apply Pre-Phase 0 capture, Q11 ritual orientation, Q12 sync preference, Phase 5 sync config creation, and sync permissions.

- [ ] **Step 5: Update COGNITIVE.md**

Read the template's updated COGNITIVE.md. Read Ford's current COGNITIVE.md. Apply the ritual ownership section and `/nap` in the session commands table. Preserve any Ford-specific additions.

- [ ] **Step 6: Update CLAUDE.md**

Read the template's updated CLAUDE.md. Read Ford's current CLAUDE.md. Apply the proactive behaviors ritual signal mappings (if not already present) and auto-open key documents in communication protocols. **Preserve all Ford-specific sections: title, identity, operating philosophy, domain boundaries, hard rules, and any Ford-specific proactive behaviors.**

- [ ] **Step 7: Update settings.local.json**

Add to the `"allow"` array:
```json
"Bash(git ls-remote:*)",
"Bash(git clone:*)",
"Bash(rm -rf /tmp/cognitive-template-sync*)"
```

- [ ] **Step 8: Create .template-sync.json**

```json
{
  "templateRemote": "https://github.com/ianlancaster/cognitive-agent-template.git",
  "lastSyncedCommit": "<TEMPLATE_HEAD from Task 4 Step 2>",
  "syncMode": "auto",
  "lastSyncDate": "<today's ISO date>"
}
```

- [ ] **Step 9: Commit**

```bash
cd /Users/ianlancaster/Projects/agents/agent-ford
git add .claude/commands/sleep.md .claude/commands/caffeinate.md .claude/commands/awaken.md COGNITIVE.md CLAUDE.md .claude/settings.local.json .template-sync.json knowledge/ritual-cadence.md
git commit -m "infra: template sync mechanism + ritual ownership (final manual propagation)"
```

---

### Task 6: Rollout to agent-wolf

**Files:**
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/.claude/commands/sleep.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/.claude/commands/caffeinate.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/.claude/commands/awaken.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/COGNITIVE.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/CLAUDE.md`
- Modify: `/Users/ianlancaster/Projects/agents/agent-wolf/.claude/settings.local.json`
- Create: `/Users/ianlancaster/Projects/agents/agent-wolf/.template-sync.json`
- Create: `/Users/ianlancaster/Projects/agents/agent-wolf/knowledge/ritual-cadence.md`

Same procedure as Task 5. Key differences for Wolf:
- Wolf does NOT have ritual-cadence.md — copy from template
- Wolf has investment-specific CLAUDE.md customizations — preserve them
- Wolf may have agent-specific sleep/caffeinate additions — check and preserve

- [ ] **Step 1: Read all target files** in Wolf's repo
- [ ] **Step 2: Update sleep.md** — add template sync phase, renumber phases, preserve Wolf-specific content
- [ ] **Step 3: Update caffeinate.md** — add ritual health + sync status, preserve Wolf-specific content
- [ ] **Step 4: Update awaken.md** — add Pre-Phase 0 capture, Q11, Q12, Phase 5 sync config, permissions
- [ ] **Step 5: Update COGNITIVE.md** — add ritual ownership, `/nap` in table, preserve Wolf-specific content
- [ ] **Step 6: Update CLAUDE.md** — add proactive behaviors, communication protocols, preserve Wolf identity
- [ ] **Step 7: Update settings.local.json** — add sync permissions
- [ ] **Step 8: Create .template-sync.json** with Wolf's config
- [ ] **Step 9: Copy ritual-cadence.md** from template to `knowledge/ritual-cadence.md`
- [ ] **Step 10: Commit**

```bash
cd /Users/ianlancaster/Projects/agents/agent-wolf
git add .claude/commands/ COGNITIVE.md CLAUDE.md .claude/settings.local.json .template-sync.json knowledge/ritual-cadence.md
git commit -m "infra: template sync mechanism + ritual ownership (final manual propagation)"
```

---

### Task 7: Rollout to agent-bill

Same structure as Task 6. Agent-bill-specific notes:
- Bill is newly awakened — minimal customizations expected
- Bill does NOT have ritual-cadence.md — copy from template
- Bill has preparedness-specific CLAUDE.md content — preserve

**Files:** Same pattern as Task 6 but in `/Users/ianlancaster/Projects/agents/agent-bill/`

- [ ] **Steps 1-10:** Same as Task 6, applied to Bill's repo. Commit message: `"infra: template sync mechanism + ritual ownership (final manual propagation)"`

---

### Task 8: Rollout to appgenie-coach (Coach)

Same structure as Task 6. Coach-specific notes:
- Coach is the largest agent (352K tokens) — has extensive customizations
- Coach does NOT have ritual-cadence.md — copy from template
- Coach has startup-strategy-specific CLAUDE.md content — preserve
- Coach's consult command is `consult-hotshot.md` (no hyphen) — preserve this naming

**Files:** Same pattern as Task 6 but in `/Users/ianlancaster/Projects/agents/appgenie-coach/`

- [ ] **Steps 1-10:** Same as Task 6, applied to Coach's repo. Commit message: `"infra: template sync mechanism + ritual ownership (final manual propagation)"`

---

### Task 9: Rollout to appgenie-monorepo (Hot Shot)

Same structure as Task 6. Hot-Shot-specific notes:
- Hot Shot has many custom commands (debug.md, dep-update.md, doc-sync.md, linear-sync.md, new-action.md, new-feature.md, new-repo.md, pr-ready.md, qa.md) — these are agent-specific and must not be affected
- Hot Shot does NOT have ritual-cadence.md — copy from template
- Hot Shot has engineering-specific CLAUDE.md content — preserve
- Hot Shot does NOT have an awaken.md — may need to create one from template

**Files:** Same pattern as Task 6 but in `/Users/ianlancaster/Projects/agents/appgenie-monorepo/`

- [ ] **Steps 1-10:** Same as Task 6, applied to Hot Shot's repo. Commit message: `"infra: template sync mechanism + ritual ownership (final manual propagation)"`

---

### Task 10: Rollout to agent-hans (Hans)

Same structure as Task 6. Hans-specific notes:
- Hans is newly awakened — minimal customizations expected
- Hans does NOT have ritual-cadence.md — copy from template
- Hans has health/fitness-specific CLAUDE.md content — preserve

**Files:** Same pattern as Task 6 but in `/Users/ianlancaster/Projects/agents/agent-hans/`

- [ ] **Steps 1-10:** Same as Task 6, applied to Hans's repo. Commit message: `"infra: template sync mechanism + ritual ownership (final manual propagation)"`

---

## Part 3: Verification

### Task 11: End-to-end verification

- [ ] **Step 1: Verify template is pushed**

```bash
cd /Users/ianlancaster/Projects/agents/cognitive-agent-template
git log --oneline -5
git remote -v
```

Confirm the latest commits include the sync mechanism changes and the remote is correctly configured.

- [ ] **Step 2: Verify each agent has .template-sync.json**

```bash
for repo in agent-ford agent-wolf agent-bill appgenie-coach appgenie-monorepo agent-hans; do
  echo "=== $repo ==="
  cat /Users/ianlancaster/Projects/agents/$repo/.template-sync.json 2>/dev/null || echo "MISSING"
done
```

All six agents should have the file with `syncMode: "auto"` and `lastSyncedCommit` matching the template HEAD.

- [ ] **Step 3: Verify sleep.md has sync phase in each agent**

```bash
for repo in agent-ford agent-wolf agent-bill appgenie-coach appgenie-monorepo agent-hans; do
  echo "=== $repo ==="
  grep -c "Template Sync Check" /Users/ianlancaster/Projects/agents/$repo/.claude/commands/sleep.md 2>/dev/null || echo "MISSING"
done
```

All six should return `1`.

- [ ] **Step 4: Verify no template sync triggers on next sleep (baseline is current)**

For one agent (e.g., Ford), simulate the sync check:

```bash
cd /Users/ianlancaster/Projects/agents/agent-ford
TEMPLATE_REMOTE=$(python3 -c "import json; print(json.load(open('.template-sync.json'))['templateRemote'])")
LAST_SYNCED=$(python3 -c "import json; print(json.load(open('.template-sync.json'))['lastSyncedCommit'])")
REMOTE_HEAD=$(git ls-remote $TEMPLATE_REMOTE HEAD | cut -f1)
echo "Last synced: $LAST_SYNCED"
echo "Remote HEAD: $REMOTE_HEAD"
echo "Match: $([ "$LAST_SYNCED" = "$REMOTE_HEAD" ] && echo YES || echo NO)"
```

Should output `Match: YES` — meaning no sync needed, which is correct since we just rolled out.
