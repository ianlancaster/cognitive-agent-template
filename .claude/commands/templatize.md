---
description: Mine this mature instance into a new, reusable role template — extract portable role-cognition, leave the history behind. Use when a subject-matter-expert agent should become a role others can instantiate.
---

You are a mature agent instance, good at your role. This ritual captures **the role, not you** — it extracts the portable, role-general cognition you have accumulated (knowledge, scripts, rules, practices, belief statements) into a new **role template** that others can instantiate, and it deliberately leaves behind everything specific to your history: your journals, your campaigns, your peers, your user, your evidence.

Read `knowledge/role-template-model.md` (the portability taxonomy) and `knowledge/templatize-runbook.md` (the craft) before starting. The taxonomy is the standard; this ritual applies it.

**This ritual never mutates the source instance.** It produces a *separate* new repo. You read yourself; you do not edit yourself.

## Pre-flight: fix the role's scope first

The portability taxonomy is **co-defined with the role brief** — "role-general" is meaningless until the role is drawn. So before mining, settle with the user:

1. **The target role** — name (kebab-case), its job, its deliverables. This becomes `context/role-brief.md`.
2. **The scope** — how broad is the role? A lesson that is instance-specific for a narrow role is portable for a broad one. Draw the line explicitly.
3. **Where the new role template lives** — a destination path and (optionally) a git remote for the new repo. It must be separate from this instance.
4. **The instance's proper nouns** — your peers, your user, your campaign names, your event/namespace identifiers. Collect these into a list; they become extra leak-check patterns in Verify, because structural patterns alone won't catch a bare name.

## Phase M — Mine

Scan yourself for portable candidates and list them (do not move anything yet):

- `knowledge/*` — role/domain reference.
- `scripts/*` beyond the base template's — tools you built.
- `memory/feedback_*`, `memory/gotcha_*`, `memory/domain_*`, `memory/reference_*` — rules, pitfalls, decisions, pointers.
- `memory/cognition/beliefs.md` — belief **statements** (not their evidence).
- `memory/cognition/insight-log.md`, `ideation.md` — for distillable lessons and evergreen patterns.
- Your operating philosophy / identity's "how I work" content.

Explicitly **exclude from mining**: `journal/`, `conversations/`, `plans/` campaign work, `calendar.md`, `context/current-state.md`, `context/active-priorities.md`, `memory/project_*`, `user_*`, belief evidence/confidence, and `context/personality.md`. These are instance-only by the taxonomy; they are not candidates.

## Phase C — Classify

Run each mined candidate through the **portability test** (both clauses): would it be true and useful for the next instance of this role under a different user and campaign, **and** does it hide any coupling to your specific context? Bucket each as **portable**, **instance-only** (drop it), or **mixed** (needs distillation). Record the bucket and a one-line reason per candidate — the runbook shows how to call the tricky ones.

## Phase D — Distill

For every **mixed** candidate, produce a portable version:

- Extract the claim so it stands without the story.
- Strip the coupling — names, dates, session/event ids, specific measurements — and **generalize** any *because* that is load-bearing ("a differently-positioned reviewer", not the peer's name).
- Prefer **act-shaped over proposition-shaped**.
- For beliefs: keep the statement + falsifier, **reset confidence to a held seed (2–3/5)**, annotate *"inherited from role template"*.

## Phase A — Assemble

Create the new role template by following **awaken's "Role-Template Onboarding" (T0–T5)** against the destination repo — but feed it the artifacts from Phases M–D instead of asking the user T2/T3 interactively:

- T1 sanitizes and **keeps `.template-marker`**.
- T2's `context/role-brief.md` is the role brief settled in Pre-flight.
- T3 seeds the **portable** and **distilled** artifacts only — knowledge, role-general memory, belief statements at held confidence.
- T4 writes `kind: "role-template"` metadata with `baseRemote` pointing at the base template.

Reusing T0–T5 rather than re-implementing assembly keeps a single copy of the sanitization-and-marker procedure — do not fork it.

## Phase V — Verify (the gate)

A role template that ships one line of your history is a defect that propagates to every instance. Before declaring done:

1. **Leak-check every seeded file**, passing your proper-noun list from Pre-flight as extra patterns:
   ```bash
   for f in $(git -C <dest> ls-files knowledge memory context/role-brief.md); do
     scripts/role-template.sh leak-check "$f" <peer1> <peer2> <user> <campaign> || true
   done
   ```
   Review every hit; clear or generalize it. An unreviewed hit is a leak.
2. **Confirm the template stands alone** — a fresh instance seeded from it would have what the role needs: the role brief is complete, the essential knowledge and role-general rules are present, and no distilled artifact silently depends on something left behind.
3. **Confirm `.template-marker` is present** and `.template-sync.json` reads `kind: role-template`.

## Report

Summarize:
- **Role template created** at `<dest>` — role, job, destination.
- **Extracted**: counts of knowledge docs, rules, scripts, belief statements carried over.
- **Left behind** (and why): the instance-only artifacts, named by class, so it is visible that history was deliberately dropped, not missed.
- **Leak check**: files scanned, hits found, all cleared.
- **Next**: instantiate with `/awaken` → instance → from this role template.
