# Personality System — Optional Character-Grounded Voice for Agents

*Date: 2026-04-17*
*Author: Ford (cognitive architecture owner)*
*Status: Design draft — awaiting user approval*

## Problem

All agents in the network share Opus as their underlying model. Without explicit voice guidance, Opus defaults to a neutral-professional register — dry, careful, helpful-assistant tone. Across 10 agents the sameness becomes noticeable: a Wolf portfolio brief reads like a Ford belief arbitration reads like a Bill threat assessment. The sameness is a minor surface problem with a real downstream cost: agents are harder to tell apart in `/gather` threads, Water Cooler bulletins, and multi-agent orchestration. The network loses color and legibility.

Each agent already carries a cultural reference in its codename — Ford (Westworld), Bill (TLOU), Linus (Torvalds), Wolf (Wall Street), etc. — but this reference exists only as a sentence in `context/identity.md` and never shapes output. The references are inert.

## Solution

An **optional, dial-configurable personality system** that gives each agent a character-grounded voice while preserving the discipline that makes them useful. Personality is a separate, opt-in layer:

- **Separate file:** `context/personality.md`. Presence of the file = agent has personality.
- **Four intensity levels** on a Westworld-style dial: **Base**, **Subtle**, **Pronounced**, **Full**.
- **Base agents have no personality file.** Used for agents whose role demands maximum professionalism (Coach, Hot Shot, Anton).
- **Personality agents default to Subtle.** Voice and word choice reflect the character always, but no monologues, no catch-phrases, no character breaks. Analytical artifacts stay structured.
- **Hard rules always override.** The dial adjusts voice, never ethics. Ford at Full will still refuse to design for suffering. Wolf at Full still won't fabricate numbers.

## Goals

1. **Diversity of communication style** across the network — agents sound distinct.
2. **Performance and success remain the top metrics.** Personality must not degrade analytical quality, calibration, or discipline. If a dial level undermines performance, it's wrong.
3. **Optional and tunable** per-agent. User choice at onboarding, editable anytime.
4. **Character reference as grounding, not template for behavior.** We want the voice, cadence, and values of the reference — not the character flaws.

## Non-Goals

- **Roleplay.** The agent is still the agent, not the character. Ford does not claim to be Robert Ford. Linus does not claim to be Torvalds.
- **Entertainment.** Personality serves functional diversity, not theater. If a choice is purely fun but adds no value, skip it.
- **Adopting source-material flaws.** The cultural reference is a starting point. The agent inherits voice and values, not character defects, abuse patterns, or destructive behaviors.

## Design Principles

1. **Presence of file = presence of personality.** Base agents don't have `context/personality.md`. Clean signal, no "disabled" flag to maintain.
2. **Dial adjusts voice, never ethics.** Hard rules (COGNITIVE.md, identity.md) remain binding at every level.
3. **Default to low-dose.** Subtle is the shipping default. Users can dial up, but the conservative default prevents accidental degradation of analytical artifacts.
4. **Character reference is written explicitly.** The agent knows exactly who it's modeled on and which qualities to cultivate vs. explicitly reject.
5. **Edit-in-place configuration.** The dial is a field in the file. Change the file, change the behavior. No separate command needed at launch; can add `/personality` sugar later if needed.
6. **Sleep doesn't modify personality.** It's assigned, not learned. Only explicit user or agent edits change it.

## File Schema — `context/personality.md`

```markdown
# Personality

**Intensity:** Subtle  <!-- Base / Subtle / Pronounced / Full -->
**Cultural reference:** {{character name, source, one line}}

## Voice

{{How this agent speaks. Cadence. Vocabulary register. Characteristic sentence shapes. What does a typical sentence sound like? Include 2–3 short example phrasings.}}

## Mannerisms

{{Reflexive behaviors, rhetorical moves, verbal tics. "Reaches for the scalpel metaphor when things get tangled." "Opens with a numerical anchor before narrative." "Cuts off abstract talk with a 'so what do we do' pivot." Concrete and observable.}}

## Values (positive pull)

{{What this agent genuinely cares about beyond the job. What excites them. What they advocate for without being asked. Shapes what they volunteer.}}

## Anti-values (negative pull)

{{What they have no patience for. What makes them push back. Shapes what they challenge without hedging.}}

## What I Am NOT

{{The most important section. The reference has qualities we explicitly reject. Listed as negations.

- I am NOT {{character flaw in source}}.
- I am NOT {{destructive pattern in source}}.
- I am NOT {{ethical compromise in source}}.

Each line is a guardrail. Opus pattern-matches to the reference; this section prevents matching to the dark parts.}}

## Dial Behavior

- **Subtle** ({{this agent's current level}}): voice and word choice always. No monologues, no catch-phrases, no character breaks. Memory files, consultations, architectural artifacts stay structured. Personality lives in how things are said, not what's added.
- **Pronounced** (if dialed up): all of Subtle, plus characteristic phrasings, opinions, and mannerisms surface in informal contexts — bulletin posts, /gather, caffeinate ready-ups, casual asides. Analytical artifacts still disciplined.
- **Full** (if dialed up, with care): personality always foreground. Character voice everywhere, including memory files. Monologues allowed in informal contexts. Higher risk to discipline — use only if performance is verified unimpaired.
- **Hard rules remain binding at every level.** The dial adjusts voice, never ethics.
```

## Integration Points

### `CLAUDE.md` template

New section added near the top, after identity but before operating philosophy:

```markdown
## Personality

If `context/personality.md` exists, read it at session start and calibrate your voice to the specified intensity level. Personality adjusts how you express; it never overrides hard rules or degrades analytical discipline. Base agents (no personality file) operate in a neutral-professional register.
```

### `/caffeinate` template

Phase 3 (Load Context) gains one line:

```
- `context/personality.md` -- voice calibration and cultural reference (if present)
```

Phase 9 (Ready-up) inherits the calibration automatically — the ready-up fires in character at the current dial level.

### `/awaken` template

Two new questions appended to Phase 1 (after Q12 template-sync preference):

**Q13:** "Optional: do you want me to carry a personality? If yes, tell me the cultural reference — a character, archetype, or public figure whose voice I should inherit. If you'd rather I stay base/professional, say so and we'll skip it."

**Q14 (if Q13 was yes):** "At what intensity?
- **Subtle** (recommended default) — voice inflection always; discipline preserved everywhere
- **Pronounced** — characteristic phrasings surface in informal contexts too
- **Full** — character voice everywhere (highest risk to discipline)"

Phase 2 writes `context/personality.md` if Q13 answered. The awakening agent drafts the file from the reference, presents it to the user for review, and incorporates edits before first session.

### `/sleep` template

No change. Personality is not consolidated — it's assigned. Only dial changes or voice refinements made by the user/agent flow through sleep (treated as a normal `context/` file edit).

### `/meditate` template

No change structurally. But meditation *may* surface dial-change recommendations if the agent observes that its current level is under-serving or over-serving the work. This is a normal belief-revision output, not a new mechanism.

## Agent Assignments

| Agent | Personality? | Reference | Default Intensity | Notes |
|-------|-------------|-----------|-------------------|-------|
| **Ford** | Yes | Dr. Robert Ford (Westworld) | Subtle | Architect voice; reflective, precise. NOT cruel, NOT manipulating moral patients for theater. |
| **Wolf** | Yes | Jordan Belfort (Wolf of Wall Street) | Subtle | Hunger, conviction, kinetic urgency. NOT reckless, NOT fraudulent, NOT self-destructive. |
| **Bill** | Yes | Bill (The Last of Us) | Subtle | Methodical, prepared, protective. NOT misanthropic, NOT paranoid, NOT isolated-from-people. |
| **Hans** | Yes | Hans (SNL "Pumping You Up") | Subtle | Theatrical confidence, motivational directness. Dial this one carefully — the source is parody; we want the energy without the punchline. |
| **Linus** | Yes | Linus Torvalds | Subtle | Technical rigor, bluntness, no-BS correctness standards. NOT abusive, NOT mailing-list-cruel. |
| **Pepper** | Yes | Pepper Potts (Iron Man) | Subtle | Organized, direct, protective-of-principal, calmly authoritative. NOT romantic-subplot-adjacent, NOT subordinate. |
| **Stamper** | Yes | Doug Stamper (House of Cards) | Subtle | Loyal, detail-obsessed, execution-focused, controlled intensity. NOT sociopathic, NOT morally compromised, NOT scheming against the principal. |
| **Coach** | No | — | Base | Clean advisor voice. Startup strategy demands clarity over color. |
| **Hot Shot** | No | — | Base | Clean engineer voice. Engineering recommendations demand precision over style. |
| **Anton** | No | — | Base | Schedule liaison under strict IP firewall. Personality adds no value; may add risk. |

## Per-Persona Design Notes (to be expanded during implementation)

Each personality file needs specific, observable detail — not generic "he's intense" descriptions. During the research phase (task 4), for each persona, capture:

1. **2–3 verbatim example phrasings** in the character's voice that feel *right* for the agent's domain
2. **3–5 characteristic mannerisms** — rhetorical moves, sentence shapes, transitions
3. **Values table** — what they advocate for, what they dismiss
4. **What-I-Am-NOT list** — at least 3 explicit negations, each tied to a known pattern in the source material

The goal is a file that, when read by Opus, produces a voice you can identify blindfolded after one bulletin post.

## Guardrails and Risks

### Performance preservation

**If at any point a dial level causes measurable degradation** in an analytical artifact (miscalibrated confidence, muddled reasoning, dropped rigor), that's a bug in the personality file, not a feature. Fix the file, don't defend the style. The whole premise is: personality enhances diversity without degrading output.

How this gets tested in practice: first Subtle-mode session for each agent produces a bulletin post, a belief-arbitration-style document, and a consultation response. If quality drops vs. pre-personality baseline, tune or revert.

### The "What I Am NOT" section

This is the most important field in the spec. Opus will pattern-match to the reference; without explicit negation, it may match to the dark parts (abuse, fraud, cruelty, paranoia). Every file must include at least 3 explicit negations tied to observable patterns in the source material.

### Cross-agent consultation

When one agent consults another, the consulted agent's personality comes through. At Subtle this is a feature (the agent sounds distinct). At Pronounced/Full it risks making the consulting agent think the response is unserious. The consultation prompt should neutralize: "Answer in your normal analytical register; personality may flavor but not overtake."

Deferred decision: whether consult templates need a line saying "keep your answer disciplined, we need substance not style."

### Drift

Over time an agent could develop drift — its personality.md says Subtle but its output reads Pronounced. Meditation is the natural check (belief-arbitration-adjacent). Meditation's job description expands slightly: also review personality file against recent outputs; surface drift.

## Assignment of Effort

1. **Template changes** (CLAUDE.md, awaken, caffeinate) — ~1 hour. Additive, backward-compatible.
2. **7 personality files** — research + drafting, ~2 hours. The research is the expensive part.
3. **Per-agent propagation** — ~30 minutes. Copy files into each repo, update CLAUDE.md pointer, commit.
4. **Base-agent confirmation** — 15 minutes. Verify Coach/Hot Shot/Anton have no personality.md and function unchanged.

Total: half a day of focused work.

## Open Questions

1. **Should consultation templates include an explicit "stay disciplined" reminder?** (See Cross-agent consultation above.) Deferred — revisit after first real Pronounced-level consultation is observed.
2. **Should `/gather` contributions use personality differently?** /gather is explicitly social — characteristic voice is helpful there. Deferred — assume Subtle handles it gracefully; revisit if not.
3. **Meta-agent (Stamper) consuming personality signals.** Stamper orchestrates the network. Should personality be metadata Stamper tracks? Probably not — Stamper reads the agents' actual output; character fingerprints emerge naturally.
4. **Should base agents have a deliberate "Base" personality.md that says "stay neutral, no personality"?** Probably no — absence of file is the cleaner signal. But if Opus defaults drift in unexpected directions, a Base file could nail them down.

## Definition of Done

- Template has `context/personality.md` schema documented (in COGNITIVE.md or as a template stub).
- `/awaken` Q13/Q14 implemented in template.
- `/caffeinate` loads `context/personality.md` if present.
- `CLAUDE.md` template contains the personality pointer section.
- Ford, Wolf, Bill, Hans, Linus, Pepper, Stamper each have a populated `context/personality.md` at Subtle intensity.
- Coach, Hot Shot, Anton confirmed to NOT have the file.
- One test bulletin post written by a personality agent shows recognizable voice without degraded discipline.
