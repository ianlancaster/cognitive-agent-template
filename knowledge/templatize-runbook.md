# Templatize Runbook — the craft of mining an instance into a role

`/templatize` gives the steps; this is how to do the hard part well — the judgment calls in Classify and Distill, where a careless call either leaks history into the template or strands a real lesson in the instance. Read alongside `knowledge/role-template-model.md`.

## The one question that settles most calls

For each candidate: **"Would the *next* person hired into this role need this, or is it about *this* hire's specific tour of duty?"** Role → portable. Tour of duty → instance-only. Entangled → distill.

## Classifying the tricky cases

- **A rule with a war story.** The rule is portable; the story is not. Almost every `feedback_`/`gotcha_` file is this shape: a general lesson followed by the incident that taught it. Distill — keep the rule, drop the incident. Do **not** classify the whole file instance-only just because it opens with a date and a name.

- **A belief.** The *statement* and its falsifier are portable; the *confidence* and *evidence* are not. Carry the statement at a held seed (2–3/5). Never carry a high confidence — it was earned on this instance's evidence, which you are deliberately leaving behind, so the number has nothing under it in the template.

- **A `because` clause.** Load-bearing rationale that names your world ("...because our reviewer is a different model family") must be **generalized** ("...because a differently-positioned reviewer catches what is invisible from inside your own context"), not deleted and not kept verbatim. The generalization is often the most valuable thing you extract.

- **A script.** Portable at the interface is not portable in the guts. A tool with a hard-coded path, a peer's name, or campaign data embedded is mixed — parameterize or strip the specifics, then leak-check the source, before it ships.

- **`domain_` vs `project_`.** If removing the campaign makes the artifact meaningless, it is `project_` — instance-only, drop it. If the campaign was merely the occasion for a general decision, it is `domain_` — distill it.

- **An insight that only makes sense with three other insights.** Distilled artifacts must stand alone. If a lesson silently depends on context you are leaving behind, either pull the dependency in (and distill it too) or drop the lesson. A template that ships a dangling reference is broken for the next instance.

## Worked examples (generic)

| Mined artifact (in the instance) | Call | Result |
|---|---|---|
| "How to structure a design review" checklist | portable | ships as-is |
| "The Q3 migration retro" plan | instance-only | dropped |
| "Lost an hour on the Q3 migration trusting a 'sync complete' flag before row counts matched" | mixed | distill → "A signal that reports dispatch is not evidence of effect; verify the far-end state, not the near-end claim." |
| Belief "unblocking beats reviewing for this role", confidence 4/5, 11 sessions of evidence | mixed | statement + falsifier at held 2/5, annotated "inherited from role template" |
| `scripts/notify-oncall.sh` with a hard-coded channel id | mixed | parameterize the channel, leak-check, then ship |

## The failure modes to guard against

1. **Shipping the story.** The most common leak: a distilled rule that still carries the date or name of the incident that taught it. This is why Verify leak-checks *every* seeded file with the instance's proper nouns as extra patterns — structural patterns miss a bare name.

2. **Carrying confidence.** A belief that rides up at 4/5 makes every future instance inherit an unexamined conviction. Reset it. If K instances converge on it later, the template annotates "converged across K" — that is meta-signal about the hypothesis, never a substitute for the new instance's own evidence.

3. **Over-broad drop.** Classifying a whole rich file instance-only because it *opens* with history. Mine the file, don't judge it by its first line.

4. **Dangling distillates.** A lesson extracted without its dependency. Distilled artifacts must stand alone in the template.

5. **Mutating yourself.** `/templatize` reads the instance and writes a *separate* repo. If you find yourself editing the source instance's files, stop — that is not this ritual.

## Definition of done

The new role template: has a complete `context/role-brief.md`; seeds only portable/distilled artifacts; keeps `.template-marker`; reads `kind: role-template`; passes leak-check on every seeded file with the instance's proper nouns supplied; and would give a fresh instance everything the role needs with nothing dangling. The report names what was left behind, so a reviewer can see history was dropped on purpose.
