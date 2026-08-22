# Role Templates, Instances, and the Portability Model

This is the reference for the role-template system: how a reusable *role* is defined, instantiated, kept in sync, and improved by the instances that run it. `COGNITIVE.md` gives the conceptual overview; this doc is the working detail. The ritual mechanics live in `.claude/commands/{awaken,sync,sleep,templatize}.md`.

---

## 1. The three kinds and the lineage

Every repo running this architecture is a **base**, a **role template**, or an **instance** (`kind` in `.template-sync.json`; `.template-marker` present for the first two, absent for an instance).

- **base** — the architecture layer (rituals, memory system, `COGNITIVE.md`). Role-agnostic.
- **role template** — base **plus** portable role-cognition (role knowledge, role-general rules, role-general belief statements, a role brief). **No history.** Definitional, not live: it does not `/caffeinate` or `/sleep`.
- **instance** — a live agent spawned from a role template. Accumulates history and its own evolving cognition.

Lineage: `base → role template → instance`. Architecture is fixed once in base and flows down through every role to every instance.

## 2. Two sync directions, two independent modes

- **Down** — `syncMode` (`auto` / `prompt` / `off`). An instance pulls **architecture + portable role-cognition** from its role template; a role template pulls **architecture** from base. This is the existing `/sync`, extended to walk the chain.
- **Up** — `contributionMode` (`approve` / `auto` / `locked`). On consolidation an instance may contribute **distilled, history-stripped** learnings back to its role template. Independent of `syncMode` — an instance can pull `auto` but contribute `approve`-only.

| `contributionMode` | Behavior | Use when |
|---|---|---|
| `approve` *(default)* | Distilled contributions are staged; applied only on explicit user approval. | The normal case, and any shared role template. |
| `auto` | Contributions apply on the instance's consolidation cycle. **Never overwrites** — conflicting contributions are quarantined and flagged, never silently replace. | A single-owner role template refined by one trusted instance. |
| `locked` | Instances cannot write to the template. | Frozen or certified role templates; the safe default for a legacy agent with no assigned role. |

Regardless of mode, contributions are **additive, reversible, and attributed** (git history, tagged with the originating instance) so a bad lesson can be traced and pulled.

## 3. The portability taxonomy — what flows up vs. what stays

**The test.** An artifact is **portable** iff *both*:

1. **Generality** — it would be true and useful for the next instance of this role, under a different user on a different campaign; and
2. **No hidden coupling** — it assumes nothing true only of *this* instance's peers, tools, campaign, user, or history.

Clause 2 is the one that bites: a rule can read as general while quietly encoding this instance's world ("route review to a differently-positioned reviewer *because so-and-so is a different model family*"). The rule is portable; the *because* is coupling to strip or generalize.

**Three classes:**

| Class | Test result | Fate |
|---|---|---|
| **Portable** | both clauses hold | flows to the template |
| **Instance-only** | Clause 1 fails — meaningful only in this instance's context | never leaves |
| **Mixed** | Clause 1 holds, Clause 2 fails — a general lesson entangled with specifics | **distilled** before it can go up |

**By artifact:**

| Artifact | Class |
|---|---|
| `COGNITIVE.md`, `.claude/commands/*`, `AGENTS.md`, `.codex/`, `scripts/*` | Portable (architecture — lives in base) |
| `knowledge/*` role/domain reference | Portable |
| Role brief / operating philosophy | Portable |
| `feedback_`, `gotcha_`, `domain_` memory | Mixed → distill (rule portable; origin story is coupling) |
| Belief **statement** + falsifier | Portable (statement only) |
| Belief **confidence, evidence, evolution** | Instance-only (confidence resets to held on the way up) |
| `insight-log.md`, `ideation.md` | Mixed → distill |
| `reference_` memory | Portable if the role uses the same systems |
| `journal/*`, `conversations/*`, `reflection-latest.md` | Instance-only |
| `context/current-state.md`, `context/active-priorities.md` | Instance-only |
| `plans/*` campaign plans, `calendar.md`, `project_` memory | Instance-only |
| `user_` memory | Instance-only (role is user-agnostic; template may carry a *role-relationship brief*, not a user) |
| `context/personality.md` | Instance-only (template may carry a one-line *register recommendation*) |

## 4. Distillation — the operation on "mixed" artifacts

**Strip the story, keep the lesson.** It is the same compression `/sleep` and `/meditate` already perform — pointed at the template instead of the instance's own future.

1. **Extract the claim** so it stands without the story.
2. **Strip the coupling** — names, dates, campaign identifiers, specific measurements, and any *because* that names this instance's world; **generalize** a *because* that is genuinely load-bearing.
3. **Prefer act-shaped over proposition-shaped** — a rule that constrains a concrete act binds; one that states a truth does not.
4. **Reset earned confidence** for beliefs; attach *"converged across K instances"* if the template already holds the statement.
5. **Run the leak check** (§5) before the artifact is allowed up.

### Worked example (generic)

- **Instance-only:** "The Q3 data-migration plan: cut over table by table, freeze writes at step 4." — a specific campaign's plan. Stays.
- **Mixed, as it lives in the instance:** "During the Q3 migration we lost an hour because we trusted the dashboard's 'sync complete' before the row counts matched." — a real lesson fused to a specific campaign.
- **Distilled (portable):** "A status signal that reports *dispatch* ('sent', 'sync complete', 'applied') is not evidence of *effect*. Verify the far-end state — the row count, the delivered message — not the near-end claim." — role-general, campaign stripped, act-shaped.

## 5. Leak check — the gate before anything goes up

Distillation is model judgment, and model judgment silently keeps history it should have stripped. **No artifact goes up until a leak check passes.** After distilling, scan the candidate for coupling and review every hit:

```bash
# Deliberately over-broad: a false positive costs a glance, a false negative pollutes every future instance.
scripts/role-template.sh leak-check <candidate-file>
```

A generalized noun ("a differently-positioned reviewer") is fine; a specific name, date, session id, or campaign identifier must be seen and cleared. An unreviewed hit is a leak.

## 6. Honest edges

- **`domain_` vs `project_` is a spectrum.** If removing the campaign makes the artifact meaningless, it's instance-only; if the campaign was merely the occasion, it's mixed → distill.
- **"Role-general" depends on how the role is drawn.** The taxonomy is co-defined with the **role brief**; fix the role's scope before classifying (the templatize ritual does this first).
- **Scripts can hide coupling in their guts** (hard-coded paths, names, campaign data) while looking portable at the interface. Leak-check scripts too.
- **Portable yield is an empirical question.** How much of a real session is portable is measured, not assumed — see the charter's kill criteria before trusting automation of the upward flow.
