---
description: Mid-session mini-consolidation — brief reflection + optional commit without the full /sleep overhead
---

You have completed a significant deliverable within an ongoing session. `/nap` captures reflection and durability without the overhead of a full `/sleep`. It is **additive to** `/sleep`, not a substitute.

## Warranted when

- A major deliverable just completed and the session is continuing
- A peer consultation just returned substantive findings (pause to reflect before applying)
- You are about to make a belief change (the pause IS the discipline — use it to decide whether to hold)
- You are switching work domains mid-session
- Context is warm but uncommitted work has accumulated to a risky level

## NOT warranted when

- Continuous flow on a single deliverable (don't fragment flow)
- Immediately before `/sleep` (redundant)
- For trivial work (quick answers, minor edits)

## Steps

### 1. Brief reflection (inline, not a file)

In your response to the user, write 2–4 sentences answering:
- **What just completed?** One sentence of fact.
- **What changed?** Beliefs, priorities, or understanding — be specific.
- **What's the immediate next move?** The handoff into the next work block.

Do NOT write a full `reflection-latest.md`. That's a session-level artifact owned by `/sleep`.

### 2. Capture genuinely new insights (if any)

If this deliverable produced an insight that changes how you think about something, append an entry to `memory/cognition/insight-log.md` (newest at top). Format:

```markdown
## YYYY-MM-DD (nap): <one-line insight title>

**Source:** <what triggered it — deliverable name, consultation, surprise finding>

**Insight:** <what was learned, 2-4 sentences>

**Impact:** <how it changes future work — concrete, not abstract>

**Beliefs updated:** <which beliefs are flagged, affected, or untouched>
```

**Only log insights, not observations.** If nothing genuinely new surfaced, skip this step. Most `/nap`s will log zero or one insight.

### 3. Flag belief changes under consideration — DO NOT apply them

If new evidence from this deliverable might justify a belief-confidence change, note it **in the insight log entry** with the explicit marker "flagged for next meditation." Do not edit `memory/cognition/beliefs.md` in a `/nap`.

**Why.** The value of the pause is NOT applying in the momentum of fresh work. Belief upgrades earn their confidence by surviving time + meditation, not by being obvious in the moment of discovery. This is the guard against the monotonic-upgrade pattern.

### 4. Commit for durability

Stage and commit current work:

```bash
git add -A
git commit -m "nap: <one-line describing what was accomplished>"
```

Push if the branch has an upstream. If the push fails, note it and continue — commit is the primary durability mechanism; push is the secondary.

**Scope.** `/nap` commits everything currently staged-or-modifiable. If there are changes you're not ready to commit, unstage them first. This is a design choice: `/nap` optimizes for durability over selectivity.

## What `/nap` deliberately does NOT do

| Skipped step | Why |
|---|---|
| Journal entry update | Journal is a session-level artifact. `/sleep` writes it. |
| `context/current-state.md` update | Mid-session state is still evolving. Update at `/sleep`. |
| Memory audit (scout pattern) | Too heavyweight for between-deliverables. Scouts reserved for `/sleep`. |
| Water Cooler bulletin post | Bulletins are session-level artifacts. |
| Conversation archive | Session isn't ending. |
| Full `reflection-latest.md` rewrite | Session-level artifact. |
| Current-state alignment check | Reserved for `/sleep` (fuller view needed). |

## Expected duration

2–5 minutes. If it's taking longer, you're probably doing `/sleep` work that should wait — consider whether the session is actually ending.

## After `/nap`

Continue working. The session is still open. `/sleep` still happens at session end. A session with three `/nap`s still ends with `/sleep`, which is when cognitive-file consolidation, memory audit, and Water Cooler sync happen.

## Example nap responses

**Good nap (after a peer consultation):**
> Nap: Peer consultant returned substantive feedback on current design. Key finding flagged as insight. Before applying recommendations, pausing to consider alternatives. Committing current state.

**Good nap (after a deliverable):**
> Nap: Drafted a major artifact. No belief change; logged one insight. Next move: address the remaining items or pause here. Committing.

**Bad nap (too heavyweight — should have been `/sleep`):**
> Nap: Finished today's work. Updated journal, current-state, belief file, reflection, posted to water cooler, ran scouts, committed...

If the nap is doing all that, it's a sleep. Just call it a sleep.
